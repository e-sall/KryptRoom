"""Read-only exact-source trigger inventory. Needs hash-locked PyYAML from M9 dev tools."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import yaml
from bootstrap_checks import BASE, BRANCH, permitted_path
from ci_scope import classify_paths, refuse_bootstrap_crypto

HEAVY = {'private-join.yml':'cryptographic-integration','persistent-state.yml':'cryptographic-integration','private-analytics.yml':'cryptographic-integration','private-nn.yml':'cryptographic-integration','fhe-state-transition.yml':'real-openfhe-bgv','state-proof-acceptance.yml':'real-sp1-groth16-proof'}


def match(pattern, value):
    # Current workflow filters use these glob operators, no brace/extglob syntax.
    if re.search(r'[\[\]{}+\\]',pattern):
        raise ValueError('Unsupported filter syntax: review required')
    regex = re.escape(pattern).replace(r'\*\*','.*').replace(r'\*','[^/]*').replace(r'\?','[^/]')
    return re.fullmatch(regex,value) is not None


def any_match(patterns, value):
    result = False
    for pattern in patterns:
        negative = pattern.startswith('!')
        if match(pattern[1:] if negative else pattern,value):result = not negative
    return result


def triggered(events, event, paths):
    if event not in events:return False
    config = events[event] or {}
    branch = BRANCH if event == 'push' else 'dev'
    if 'branches' in config and not any_match(config['branches'],branch):return False
    if 'branches-ignore' in config and any_match(config['branches-ignore'],branch):return False
    if len(paths)>300 and ('paths' in config or 'paths-ignore' in config):
        raise ValueError('GitHub path filter 300-file boundary: cannot assert this event')
    if 'paths' in config and not any(any_match(config['paths'],p) for p in paths):return False
    if 'paths-ignore' in config and all(any_match(config['paths-ignore'],p) for p in paths):return False
    return True


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    def git(*cmd):return subprocess.check_output(['git',*cmd],text=True)
    source=git('rev-parse',args.source).strip()
    paths=[p for p in git('diff','--no-renames','--name-only','-z',BASE,source).split('\0') if p]
    def at(sha,path):
        try:return git('show',sha+':'+path)
        except subprocess.CalledProcessError:return None
    scopes=classify_paths(paths,lambda p:at(BASE,p),lambda p:at(source,p))
    if not paths or not all(permitted_path(p) for p in paths):
        raise ValueError('Actual Core/unknown changes: publication is outside this diagnostic authorization')
    refusal=refuse_bootstrap_crypto('pull_request',{'pull_request':{'head':{'ref':BRANCH}}},scopes,paths)
    rows=[]
    for path in git('ls-tree','-r','--name-only',source,'.github/workflows').splitlines():
        if not path.endswith(('.yml','.yaml')):continue
        raw=at(source,path);doc=yaml.safe_load(raw);events=doc.get('on',doc.get(True))
        unexpected=set(events)-{'push','pull_request','workflow_dispatch'}
        if unexpected:raise ValueError('Unexpected chained/scheduled event: '+path)
        push=triggered(events,'push',paths);pr=triggered(events,'pull_request',paths)
        jobs=[]
        heavy_job=HEAVY.get(Path(path).name)
        if heavy_job and heavy_job not in doc['jobs']:
            raise ValueError('Expected heavy job missing: review required '+path)
        for job,spec in doc['jobs'].items():
            needs=spec.get('needs',[]);needs=[needs] if isinstance(needs,str) else needs
            heavy=job==heavy_job
            if heavy:
                expected="${{ needs.change-scope.outputs.core == 'true' }}"
                if spec.get('if')!=expected or needs!=['change-scope']:raise ValueError('Heavy job lacks verified successful-scope prerequisite: '+path)
            status='WORKFLOW_NOT_TRIGGERED' if not pr else ('BLOCKED_BY_FAILED_SCOPE' if heavy and refusal else 'SEE_JOB_CONDITIONS')
            if pr and job=='change-scope':status='FAILS_EXECUTION_REFUSAL_CORE_TRUE' if refusal else 'CLASSIFIES_NORMALLY'
            if pr and not needs and not spec.get('if') and job not in ['change-scope','release-policy','bootstrap-policy','m9-control-foundation','m9-identity-organizations','foundation']:
                status='RUN_FAST_CONTRACTS' # Commands preserved in raw record for review.
            jobs.append({'id':job,'name':spec.get('name',job),'needs':needs,'if':spec.get('if'),'pr_static_outcome':status})
        rows.append({'file':path,'name':doc.get('name'),'events':events,'push_release':push,'pr_open_dev':pr,'pr_synchronize_dev_same_paths':pr,'permissions':doc.get('permissions'),'secret_references':sorted(set(re.findall(r'secrets\.([A-Za-z0-9_]+)',raw))),'sha256':hashlib.sha256(raw.encode()).hexdigest(),'jobs':jobs,'raw_utf8':raw})
    result={'source_sha':source,'baseline_dev':BASE,'branch':BRANCH,'path_count':len(paths),'paths':paths,'classification':scopes,'rows':rows,'hosted_execution':'NOT RUN','scope':'Exact reviewed source and current full PR diff only. Any workflow/helper/filter change requires a new audit. Self-modifying PRs are not externally enforced.'}
    args.output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'source':source,'paths':len(paths),'push_workflows':[r['file'] for r in rows if r['push_release']],'pr_workflows':[r['file'] for r in rows if r['pr_open_dev']],'scopes':scopes},indent=2))


if __name__=='__main__':main()
