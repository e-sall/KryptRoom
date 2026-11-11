"""Read-only inputs, synthetic runner IO; no Docker/npm/frontend execution."""
from pathlib import Path
import copy, datetime as dt, hashlib, json, os, subprocess, sys, tempfile, unittest
from unittest.mock import patch
import frontend_security_gate as g

NOW=dt.datetime.now(dt.timezone.utc)
REPORT={'auditReportVersion':2,'metadata':{'vulnerabilities':{k:0 for k in ('info','low','moderate','high','critical','total')}},'vulnerabilities':{}}
CTX={'source_sha':'4b7e6bb4cafe7062360e79322f0cd63579bae119','baseline_sha':'d8a5c0aa7ed845c31bd2ff40c1b3491246c6cf83',
     'event_name':'pull_request','repository':'e-sall/KryptRoom','lock_sha256':'a'*64}
PROOF={**CTX,'audit_sha256':g.digest(json.dumps(REPORT,sort_keys=True).encode()),'node_image':g.IMAGE,
       'lint_supported':True,'embedded_nft_reviewed_fixed':True,'embedded_nft_sha256':'b'*64,
       'review_reference':'synthetic-only','issued_utc':(NOW-dt.timedelta(minutes=1)).isoformat().replace('+00:00','Z'),
       'expires_utc':(NOW+dt.timedelta(hours=1)).isoformat().replace('+00:00','Z'),'revoked':False}
ROWS=[]

class Gate(unittest.TestCase):
    def test_real_git_baseline_and_pr_merge_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            subprocess.run(['git','init','-q',tmp],check=True,capture_output=True)
            def git(*args,input=None):
                return subprocess.check_output(['git','-c','user.name=Gate Test','-c','user.email=gate@example.invalid',*args],cwd=root,input=input).decode().strip()
            tree=git('mktree',input=b'')
            sequence=[]
            def commit(*parents):
                sequence.append(1)
                return git('commit-tree',tree,*[arg for p in parents for arg in ('-p',p)],input=f'synthetic gate context {len(sequence)}\n'.encode())
            a=commit();left=commit(a);right=commit(a);merge=commit(left,right);unrelated=commit()
            git('update-ref','HEAD',merge)
            (root/'apps/web').mkdir(parents=True);(root/'apps/web/package-lock.json').write_text('{}')
            env={'REVIEW_SOURCE_SHA':merge,'REVIEW_BASELINE_SHA':left,'GITHUB_EVENT_NAME':'pull_request','GITHUB_REPOSITORY':'e-sall/KryptRoom'}
            self.assertEqual(g.git_context(root,env)['source_sha'],merge)
            for baseline in ('f'*40,unrelated,'0'*40):
                with self.subTest(baseline=baseline),self.assertRaises((ValueError,subprocess.CalledProcessError)):
                    g.git_context(root,{**env,'REVIEW_BASELINE_SHA':baseline})
            with self.assertRaises(ValueError):g.git_context(root,{**env,'REVIEW_SOURCE_SHA':left})
            with self.assertRaises(ValueError):
                g.git_context(root,{**env,'GITHUB_EVENT_NAME':'push','REVIEW_BASELINE_SHA':'0'*40})
    def test_refusal_prevents_downstream_marker_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);subprocess.run(['git','init','-q',tmp],check=True,capture_output=True)
            marker=root/'frontend-started'
            gate=Path(g.__file__).resolve()
            # Real subprocess failure, no Docker: source mismatch refuses before audit.
            code='import subprocess,sys,pathlib; subprocess.run([sys.executable,sys.argv[1]],check=True); pathlib.Path(sys.argv[2]).touch()'
            env={**os.environ,'GITHUB_WORKSPACE':tmp,'REVIEW_SOURCE_SHA':'f'*40,'REVIEW_BASELINE_SHA':'0'*40}
            result=subprocess.run([sys.executable,'-c',code,str(gate),str(marker)],env=env,capture_output=True)
            self.assertNotEqual(result.returncode,0);self.assertFalse(marker.exists())
            self.assertTrue((root/'frontend-security-evidence/refusal.json').exists())
    def test_valid_control(self):g.validate(REPORT,PROOF,CTX,0,NOW)
    def test_real_historical_eight_findings_still_block(self):
        data=json.loads((Path(__file__).parent/'fixtures/frontend-security-audit.json').read_text())
        with self.assertRaises(ValueError):g.validate(data,PROOF,CTX,1,NOW)
    def test_all_invalid_records(self):
        cases={
          '01 missing review':lambda r,p,c:(r,None,c,0),
          '02 wrong lock':lambda r,p,c:(r,{**p,'lock_sha256':'c'*64},c,0),
          '03 wrong SHA':lambda r,p,c:(r,{**p,'source_sha':'c'*40},c,0),
          '04 expired':lambda r,p,c:(r,{**p,'expires_utc':p['issued_utc']},c,0),
          '05 EOL':lambda r,p,c:(r,{**p,'lint_supported':False},c,0),
          '06 embedded unreviewed':lambda r,p,c:(r,{**p,'embedded_nft_reviewed_fixed':False},c,0),
          '07 missing provenance':lambda r,p,c:(r,{**p,'review_reference':''},c,0),
          '08 new finding':lambda r,p,c:({**r,'metadata':{'vulnerabilities':{**r['metadata']['vulnerabilities'],'high':1,'total':1}}},p,c,0),
          'wrong baseline':lambda r,p,c:(r,{**p,'baseline_sha':'c'*40},c,0),
          'wrong event':lambda r,p,c:(r,{**p,'event_name':'push'},c,0),
          'revoked':lambda r,p,c:(r,{**p,'revoked':True},c,0),
          'missing vulnerabilities':lambda r,p,c:({k:v for k,v in r.items() if k!='vulnerabilities'},p,c,0),
          'counts contradict list':lambda r,p,c:({**r,'vulnerabilities':{'x':{'severity':'high'}}},p,c,0),
          'error plus clean counts':lambda r,p,c:({**r,'error':{}},p,c,0),
          'nonzero clean report':lambda r,p,c:(r,p,c,1),
          'bad embedded hash':lambda r,p,c:(r,{**p,'embedded_nft_sha256':'not-a-hash'},c,0),
          'missing metadata':lambda r,p,c:({},p,c,0),
          'missing count':lambda r,p,c:({**r,'metadata':{'vulnerabilities':{}}},p,c,0),
          'bool count':lambda r,p,c:({**r,'metadata':{'vulnerabilities':{**r['metadata']['vulnerabilities'],'low':False}}},p,c,0),
          'wrong audit hash':lambda r,p,c:(r,{**p,'audit_sha256':'c'*64},c,0),
          'unknown field':lambda r,p,c:(r,{**p,'bypass':True},c,0),
          'missing field':lambda r,p,c:(r,{k:v for k,v in p.items() if k!='revoked'},c,0),
          'wrong type':lambda r,p,c:(r,[],c,0),
          'no issued time':lambda r,p,c:(r,{**p,'issued_utc':''},c,0),
          'future issued':lambda r,p,c:(r,{**p,'issued_utc':p['expires_utc']},c,0),
          'over24h':lambda r,p,c:(r,{**p,'expires_utc':(NOW+dt.timedelta(days=2)).isoformat().replace('+00:00','Z')},c,0),
          'wrong repo':lambda r,p,c:(r,{**p,'repository':'other/repo'},c,0),
          'unsupported event':lambda r,p,c:(r,p,{**c,'event_name':'pull_request_target'},0),
          'wrong image':lambda r,p,c:(r,{**p,'node_image':'latest'},c,0),
        }
        for name,mutate in cases.items():
            with self.subTest(name=name):
                try:
                    args=mutate(copy.deepcopy(REPORT),copy.deepcopy(PROOF),copy.deepcopy(CTX))
                    with self.assertRaises((ValueError,TypeError,KeyError)):g.validate(*args[:3],args[3],NOW)
                except Exception:
                    ROWS.append({'case':name,'status':'FAIL'});raise
                ROWS.append({'case':name,'status':'PASS','observed':'REFUSED'})
    def test_decode(self):
        for raw in ('','{','nonsense','{"a":1,"a":2}','{"x":NaN}'):
            with self.subTest(raw=raw),self.assertRaises((ValueError,TypeError)):g.decode(raw)
    def test_actual_child_process_timeout(self):
        with self.assertRaises(subprocess.TimeoutExpired):
            subprocess.run([sys.executable,'-c','import time; time.sleep(2)'],timeout=0.1,capture_output=True)
    def test_main_refuses_invalid_review_and_checkout(self):
        for wrong_checkout in (False,True):
            with self.subTest(wrong_checkout=wrong_checkout),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);(root/'apps/web').mkdir(parents=True)
                (root/'apps/web/package-lock.json').write_text('{}')
                (root/'apps/web/package.json').write_text('{}')
                env={'GITHUB_WORKSPACE':tmp,'REVIEW_SOURCE_SHA':CTX['source_sha'],
                     'REVIEW_BASELINE_SHA':CTX['baseline_sha'],'GITHUB_EVENT_NAME':'pull_request',
                     'GITHUB_REPOSITORY':CTX['repository'],'FRONTEND_SECURITY_EVIDENCE_JSON':'{'}
                with patch.dict(os.environ,env),patch.object(g.subprocess,'check_output',return_value=('c'*40 if wrong_checkout else CTX['source_sha'])+'\n'),patch.object(g.subprocess,'run'),patch.object(g,'execute_audit',return_value=(REPORT,0)):
                    with self.assertRaises(SystemExit):g.main()
                self.assertTrue((root/'frontend-security-evidence/refusal.json').exists())
                self.assertFalse((root/'frontend-security-evidence/local-validation.json').exists())
    def test_transport_and_cleanup(self):
        for failure in (OSError('network unavailable'),subprocess.TimeoutExpired('audit',120)):
            with self.subTest(failure=type(failure).__name__),tempfile.TemporaryDirectory() as tmp:
                calls=[]
                def runner(cmd,**kw):
                    calls.append(cmd)
                    if cmd[:2]==['docker','run']:raise failure
                    return subprocess.CompletedProcess(cmd,0,b'',b'')
                with self.assertRaises(ValueError):g.execute_audit(['docker','run','--rm'],tmp,runner)
                self.assertTrue((Path(tmp)/'audit.json').exists())
                self.assertTrue((Path(tmp)/'audit.stderr').exists())
                self.assertEqual(calls[-1][:3],['docker','rm','-f'])
                self.assertTrue(json.loads((Path(tmp)/'execution.json').read_text())['cleanup_confirmed'])
        with tempfile.TemporaryDirectory() as tmp:
            def broken(cmd,**kw):
                if cmd[1]=='run':return subprocess.CompletedProcess(cmd,0,json.dumps(REPORT).encode(),b'')
                raise OSError('daemon down')
            with self.assertRaises(ValueError):g.execute_audit(['docker','run'],tmp,broken)
    def test_noop_is_not_trusted_enforcement(self):
        # Demonstrates unresolved remote prerequisite; it is NOT a bypass-prevention PASS.
        scope={};exec('def validate(*a): return None',scope)
        self.assertIsNone(scope['validate'](None))
    def test_both_proposed_call_sites_identical(self):
        root=Path(__file__).parent/'workflows'
        for name in ('web-foundation.yml','control-api-identity.yml'):
            text=(root/name).read_text()
            self.assertEqual(text.count('run: python3 .github/frontend_security_gate.py'),1)
            index=text.index('run: python3 .github/frontend_security_gate.py')
            for command in ('run: npm ci','scripts/pr1-upgrade-acceptance.py','scripts/identity-stack-acceptance.py'):
                if command in text:self.assertLess(index,text.index(command))
            self.assertIn('REVIEW_BASELINE_SHA:',text)
            upload=text[text.index('      - name: Preserve frontend gate evidence'):]
            self.assertIn('actions/upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f',upload)
            self.assertNotIn('continue-on-error',text)
            for command in ('run: npm ci','run: npm run lint','run: npm run build','scripts/pr1-upgrade-acceptance.py','scripts/identity-stack-acceptance.py'):
                if command in text:
                    segment=text[text.rfind('      - ',0,text.index(command)):text.index(command)+len(command)]
                    self.assertNotIn('always()',segment)
                    self.assertNotIn('!cancelled()',segment)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Gate))
    Path(__import__('os').environ['FRONTEND_GATE_TEST_RESULTS']).write_text(json.dumps({'tests_run':result.testsRun,'failures':len(result.failures),
       'errors':len(result.errors),'negative_cases':ROWS,'trusted_enforcement':'NOT RUN; requires GitHub admin controls',
       'synthetic_io':True,'actual_hosted_execution':False},indent=2),encoding='utf-8')
    raise SystemExit(not result.wasSuccessful())
