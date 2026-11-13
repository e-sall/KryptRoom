"""No crypto/server execution: policy, context, dependency and refusal regressions."""
import copy
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from bootstrap_checks import BASE, BRANCH, aggregate, permitted_path, policy, require_pr_validation
from ci_scope import classify_paths, refuse_bootstrap_crypto
from bootstrap_images import supported_postgres

ROOT = Path(__file__).parent
HEAD = 'a'*40


class BootstrapTests(unittest.TestCase):
    def test_postgres_floor_refuses_old_missing_and_wrong_major(self):
        for value in ['17.11','17.11-1.pgdg12+1','18.1','', 'bad', '117.12']:
            self.assertFalse(supported_postgres(value),value)
        for value in ['17.12','17.12-1.pgdg12+1','17.13']:
            self.assertTrue(supported_postgres(value),value)

    def event(self):
        return {'action':'synchronize','pull_request':{'head':{'ref':BRANCH,'sha':HEAD,'repo':{'full_name':'e-sall/KryptRoom'}},'base':{'ref':'dev','sha':BASE},'merge_commit_sha':HEAD}}

    def test_first_push_zero_before_uses_checked_baseline(self):
        calls=[]
        def git(*args):
            calls.append(args)
            return 'services/control-api/src/kryptroom_control/app.py\0' if args[0]=='diff' else ''
        self.assertTrue(policy('push',{'ref':'refs/heads/'+BRANCH,'after':HEAD,'before':'0'*40},'e-sall/KryptRoom',HEAD,git))
        self.assertIn(('merge-base','--is-ancestor',BASE,HEAD),calls)

    def test_invalid_missing_or_nonancestor_baseline_refused(self):
        def git(*args):raise subprocess.CalledProcessError(1,['git',*args])
        with self.assertRaises(subprocess.CalledProcessError):
            policy('push',{'ref':'refs/heads/'+BRANCH,'after':HEAD},'e-sall/KryptRoom',HEAD,git)

    def test_real_git_ancestry_first_push_and_pr_merge_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            def git(*args):
                return subprocess.check_output(['git',*args],cwd=directory,text=True,stderr=subprocess.DEVNULL).strip()
            def commit(name):
                git('add','.')
                git('-c','user.name=Local fixture','-c','user.email=fixture@example.invalid','commit','-m',name)
                return git('rev-parse','HEAD')
            git('init','--initial-branch=base')
            path=Path(directory)/'apps/web/example.txt';path.parent.mkdir(parents=True);path.write_text('base')
            base=commit('base')
            git('checkout','-b','feature')
            path.write_text('feature');head=commit('feature')
            git('checkout','base')
            other=Path(directory)/'docs/m9/example.txt';other.parent.mkdir(parents=True);other.write_text('target')
            target=commit('target')
            git('-c','user.name=Local fixture','-c','user.email=fixture@example.invalid','merge','--no-ff','feature','-m','test merge')
            merge=git('rev-parse','HEAD')
            with patch('bootstrap_checks.BASE',base):
                self.assertTrue(policy('push',{'ref':'refs/heads/'+BRANCH,'after':head,'before':'0'*40},'e-sall/KryptRoom',head,git))
                event=self.event();event['pull_request']['head']['sha']=head;event['pull_request']['base']['sha']=base;event['pull_request']['merge_commit_sha']=merge
                self.assertTrue(policy('pull_request',event,'e-sall/KryptRoom',merge,git))
                with self.assertRaises(ValueError):policy('pull_request',event,'e-sall/KryptRoom',head,git)
            for invalid in ['f'*40,target]:
                with patch('bootstrap_checks.BASE',invalid),self.assertRaises(subprocess.CalledProcessError):
                    policy('push',{'ref':'refs/heads/'+BRANCH,'after':head},'e-sall/KryptRoom',head,git)

    def test_pr_merge_sha_not_head_is_required(self):
        event=self.event()
        self.assertTrue(policy('pull_request',event,'e-sall/KryptRoom',HEAD,lambda *a:''))
        with self.assertRaises(ValueError):policy('pull_request',event,'e-sall/KryptRoom','b'*40,lambda *a:'')

    def test_other_pr_is_explicitly_not_applicable(self):
        event=self.event();event['pull_request']['head']['ref']='feat/unrelated'
        self.assertFalse(policy('pull_request',event,'e-sall/KryptRoom',HEAD,lambda *a:''))

    def test_fork_wrong_base_event_ref_or_checkout_refused(self):
        for key in ['fork','base','baseline','event']:
            event=self.event()
            if key=='fork':event['pull_request']['head']['repo']['full_name']='foreign/repo'
            elif key=='base':event['pull_request']['base']['ref']='main'
            elif key=='baseline':event['pull_request']['base']['sha']='f'*40
            else:event['action']='labeled'
            with self.subTest(key=key),self.assertRaises(ValueError):policy('pull_request',event,'e-sall/KryptRoom',HEAD,lambda *a:'')
        for event in [{'ref':'refs/heads/main','after':HEAD},{'ref':'refs/heads/'+BRANCH,'after':'b'*40},{'ref':'refs/heads/'+BRANCH,'after':HEAD,'deleted':True}]:
            with self.assertRaises(ValueError):policy('push',event,'e-sall/KryptRoom',HEAD,lambda *a:'')

    def test_core_shared_unknown_and_crypto_workflow_changes_not_bootstrapped(self):
        for path in ['engines/zk/code.rs','nodes/krypt-node/src/main.rs','tests/state_proof/fixtures/S1.json','packages/manifests/room-state.schema.json','package-lock.json','compose.persistent-state.yml','.github/workflows/private-nn.yml','.github/workflows/new-danger.yml','unknown-file']:
            with self.subTest(path=path):
                self.assertFalse(permitted_path(path))
                flags=classify_paths([path],lambda _:None,lambda _:None)
                self.assertTrue(flags['core'])
                with self.assertRaises(ValueError):policy('push',{'ref':'refs/heads/'+BRANCH,'after':HEAD},'e-sall/KryptRoom',HEAD,lambda *args:path+'\0' if args[0]=='diff' else '')

    def test_m9_m8_mixed_and_ci_stay_conservative(self):
        for paths in [['services/control-api/src/kryptroom_control/app.py'],['apps/web/src/features/marketing/test.tsx'],['.github/ci_scope.py'],['services/control-api/src/kryptroom_control/app.py','engines/psi/changed.rs']]:
            flags=classify_paths(paths,lambda _:None,lambda _:None)
            self.assertEqual(flags['core'],any(p.startswith(('engines/','.github/')) for p in paths))
        self.assertTrue(classify_paths(['services/control-api/Dockerfile.postgres-candidate'],lambda _:None,lambda _:None)['core'])

    def test_crypto_refusal_does_not_turn_core_false_or_disable_other_branches(self):
        scopes={'core':True,'web':True,'m9':True};event=self.event()
        paths=['.github/ci_scope.py','services/control-api/Dockerfile.postgres-candidate']
        self.assertTrue(refuse_bootstrap_crypto('pull_request',event,scopes,paths))
        self.assertTrue(scopes['core'])
        self.assertFalse(refuse_bootstrap_crypto('push',event,scopes,paths))
        self.assertFalse(refuse_bootstrap_crypto('workflow_dispatch',event,scopes,paths))
        for actual_core in ['engines/zk/src/main.rs','tests/state_proof/fixtures/S1.json','packages/manifests/room-state.schema.json','.github/workflows/private-nn.yml','unknown']:
            self.assertFalse(refuse_bootstrap_crypto('pull_request',event,scopes,paths+[actual_core]))
            self.assertTrue(classify_paths(paths+[actual_core],lambda _:None,lambda _:None)['core'])
        event['pull_request']['head']['ref']='feat/core-fix'
        self.assertFalse(refuse_bootstrap_crypto('pull_request',event,scopes,paths))
        with self.assertRaises(ValueError):require_pr_validation('pull_request',scopes)
        require_pr_validation('push',scopes)

    def test_ci_cli_writes_core_true_then_refuses_before_heavy_job(self):
        event=self.event()
        with tempfile.TemporaryDirectory() as directory:
            eventfile=Path(directory)/'event.json';eventfile.write_text(json.dumps(event));output=Path(directory)/'output'
            env={**os.environ,'GITHUB_EVENT_NAME':'pull_request','GITHUB_EVENT_PATH':str(eventfile),'GITHUB_OUTPUT':str(output)}
            # Replace only Git diff lookup: use real main/refusal/output handling.
            import runpy
            with patch.dict(os.environ,env), patch('subprocess.check_output',side_effect=lambda args: (BASE if args[1]=='merge-base' else '.github/ci_scope.py\0').encode()),self.assertRaises(SystemExit):
                runpy.run_path(str(ROOT/'ci_scope.py'),run_name='__main__')
            self.assertIn('core=true',output.read_text())

    def test_aggregate_all_success_only_and_no_skipped_required_consumer(self):
        names=['policy','backend','security','images','frontend','identity'];valid=dict.fromkeys(names,'success')
        aggregate('true',valid)
        for name in names:
            for state in ['failure','cancelled','skipped','']:
                data={**valid,name:state}
                with self.subTest(name=name,state=state),self.assertRaises(ValueError):aggregate('true',data)
        for value in ['',None,'unknown']:
            with self.assertRaises(ValueError):aggregate(value,valid)
        with self.assertRaises(ValueError):aggregate('true',{'policy':'success'})
        aggregate('false',{**dict.fromkeys(names,'skipped'),'policy':'success'})
        with self.assertRaises(ValueError):aggregate('false',valid)

    def test_workflow_no_privileged_event_secret_write_or_mutable_action(self):
        text=(ROOT/'workflows/m9-hosted-bootstrap.yml').read_text()
        for forbidden in ['pull_request_target','workflow_run','workflow_call','schedule:','${{ secrets.','contents: write','id-token:','continue-on-error','--ignore-unfixed','--legacy-peer-deps']:
            self.assertNotIn(forbidden,text)
        self.assertTrue(all(re.fullmatch(r'actions/[a-z-]+@[0-9a-f]{40}',x) for x in re.findall(r'uses: (\S+)',text)))
        self.assertLess(text.index('id: policy'),text.index("python3 -m unittest discover"))
        self.assertIn("if: steps.policy.outputs.applicable == 'true'",text)
        for name in ['bootstrap-frontend','bootstrap-identity']:
            body=re.split(r'\n  [a-z][a-z-]+:',text.split('  '+name+':',1)[1])[0]
            # Check dependency line directly without interpreting shell expressions.
            self.assertIn('needs:',body)
            self.assertIn('bootstrap-security' if name=='bootstrap-frontend' else 'bootstrap-images',body)
            if name=='bootstrap-identity':self.assertIn('bootstrap-frontend',body)
        self.assertIn('if: always()',text.split('  m9-bootstrap-release:',1)[1])

    def test_every_existing_heavy_job_has_a_failed_scope_prerequisite(self):
        heavy={'private-join.yml':'cryptographic-integration','persistent-state.yml':'cryptographic-integration','private-analytics.yml':'cryptographic-integration','private-nn.yml':'cryptographic-integration','fhe-state-transition.yml':'real-openfhe-bgv','state-proof-acceptance.yml':'real-sp1-groth16-proof'}
        for file,job in heavy.items():
            body=(ROOT/'workflows'/file).read_text().split('  '+job+':',1)[1]
            header=body.split('    steps:',1)[0]
            self.assertIn('needs: change-scope',header)
            self.assertIn("if: ${{ needs.change-scope.outputs.core == 'true' }}",header)
            self.assertNotRegex(header,r'always\(|failure\(|cancelled\(')


if __name__=='__main__':unittest.main()
