"""Isolated V2 proposal. Local validation is NOT trusted GitHub enforcement."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import uuid

IMAGE = 'node:22.23.5-alpine3.23@sha256:6868d4695b947ee120bffaa463fecd68cde370d7bfec92955e7c8ac576b4f475'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def decode(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Non-finite JSON')))

def require(ok, message):
    if not ok:
        raise ValueError(message)

def validate(report, proof, context, returncode, now):
    require(type(returncode) is int and returncode == 0, 'Audit execution failed')
    require(type(report) is dict and 'error' not in report, 'Invalid/error audit')
    require(report.get('auditReportVersion') == 2, 'Unsupported audit version')
    require(type(report.get('metadata')) is dict, 'Missing metadata')
    counts = report['metadata'].get('vulnerabilities')
    require(type(counts) is dict and set(counts) == {'info','low','moderate','high','critical','total'}, 'Invalid counts')
    require(all(type(n) is int and n == 0 for n in counts.values()), 'Unresolved findings')
    require(type(report.get('vulnerabilities')) is dict and not report['vulnerabilities'], 'Contradictory/missing vulnerabilities')
    require(type(proof) is dict, 'Missing/invalid review record')
    keys = {'source_sha','baseline_sha','event_name','repository','lock_sha256','audit_sha256',
            'node_image','lint_supported','embedded_nft_reviewed_fixed','embedded_nft_sha256',
            'review_reference','issued_utc','expires_utc','revoked'}
    require(set(proof) == keys, 'Invalid review schema')
    for field in ('source_sha','baseline_sha'):
        require(type(proof[field]) is str and re.fullmatch('[0-9a-f]{40}', proof[field]), 'Invalid SHA')
    require(context['event_name'] in {'push','pull_request','workflow_dispatch'}, 'Unsupported event')
    for field in ('source_sha','baseline_sha','event_name','repository','lock_sha256'):
        require(proof[field] == context[field], 'Context mismatch: '+field)
    for field in ('lock_sha256','audit_sha256','embedded_nft_sha256'):
        require(type(proof[field]) is str and re.fullmatch('[0-9a-f]{64}', proof[field]), 'Invalid hash')
    require(proof['audit_sha256'] == digest(json.dumps(report, sort_keys=True).encode()), 'Audit mismatch')
    require(proof['revoked'] is False, 'Revoked review')
    require(proof['node_image'] == IMAGE, 'Image mismatch')
    require(proof['lint_supported'] is True and proof['embedded_nft_reviewed_fixed'] is True, 'Unsupported/unfixed tooling')
    require(type(proof['review_reference']) is str and bool(proof['review_reference'].strip()), 'Missing provenance')
    times = []
    for field in ('issued_utc','expires_utc'):
        value = proof[field]
        require(type(value) is str and value.endswith('Z'), 'UTC timestamp required')
        times.append(dt.datetime.fromisoformat(value[:-1]+'+00:00'))
    issued, expiry = times
    require(issued <= now < expiry and dt.timedelta(0) < expiry-issued <= dt.timedelta(hours=24), 'Invalid lifetime')

def execute_audit(command, output, runner=subprocess.run):
    """Persist failures too. Cleanup failure itself blocks; never emit success."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    container = 'kr-audit-'+uuid.uuid4().hex
    command = command[:2]+['--name',container]+command[2:]
    stdout, stderr, result_code = b'', b'', None
    failure = None
    try:
        result = runner(command, capture_output=True, timeout=120, check=False)
        stdout, stderr, result_code = result.stdout, result.stderr, result.returncode
    except (OSError, subprocess.TimeoutExpired) as error:
        failure = type(error).__name__
        stdout = getattr(error,'stdout',None) or b''
        stderr = getattr(error,'stderr',None) or b''
    finally:
        (output/'audit.json').write_bytes(stdout)
        (output/'audit.stderr').write_bytes(stderr)
        try:
            cleanup = runner(['docker','rm','-f',container], capture_output=True, timeout=15, check=False)
            # Missing container is expected after --rm; daemon failure is not success.
            removed = cleanup.returncode == 0 or b'No such container' in cleanup.stderr
        except (OSError, subprocess.TimeoutExpired):
            removed = False
        (output/'execution.json').write_text(json.dumps({'returncode':result_code,'failure':failure,'cleanup_confirmed':removed}),encoding='utf-8')
    require(not failure and removed, 'Audit unavailable/timeout/cleanup unconfirmed')
    return decode(stdout), result_code

def git_context(root, env):
    """Bind to the actual checkout, including a PR test merge, never just PR head."""
    source = subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    require(source == env['REVIEW_SOURCE_SHA'], 'Checkout/source mismatch')
    baseline = env['REVIEW_BASELINE_SHA']
    require(re.fullmatch('[0-9a-f]{40}',baseline) and baseline != '0'*40,
            'Missing baseline (first push requires independent baseline selection)')
    subprocess.run(['git','cat-file','-e',baseline+'^{commit}'],cwd=root,check=True,capture_output=True)
    subprocess.run(['git','merge-base','--is-ancestor',baseline,source],cwd=root,check=True,capture_output=True)
    return {'source_sha':source,'baseline_sha':baseline,'event_name':env['GITHUB_EVENT_NAME'],
            'repository':env['GITHUB_REPOSITORY'],
            'lock_sha256':digest((root/'apps/web/package-lock.json').read_bytes())}

def main():
    root = Path(os.environ['GITHUB_WORKSPACE'])
    evidence = root/'frontend-security-evidence'
    evidence.mkdir(exist_ok=True)
    # A rerun must not leave a previous local PASS next to a new refusal.
    (evidence/'local-validation.json').unlink(missing_ok=True)
    try:
        context = git_context(root, os.environ)
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp).chmod(0o755)
            for name in ('package.json','package-lock.json'):
                target = Path(tmp)/name
                shutil.copyfile(root/'apps/web'/name,target)
                target.chmod(0o444)
            cmd = ['docker','run','--rm','--user','10001:10001','--read-only','--cap-drop','ALL',
                   '--security-opt','no-new-privileges:true','--tmpfs','/tmp',
                   '--env','npm_config_cache=/tmp/npm-cache','--mount',f'type=bind,source={tmp},target=/audit,readonly',
                   '--workdir','/audit',IMAGE,'npm','audit','--json','--registry=https://registry.npmjs.org']
            report, code = execute_audit(cmd,evidence)
        print(json.dumps(report))  # Findings remain visible even when validation refuses.
        proof = decode(os.environ.get('FRONTEND_SECURITY_EVIDENCE_JSON','null'))
        validate(report,proof,context,code,dt.datetime.now(dt.timezone.utc))
        (evidence/'local-validation.json').write_text(json.dumps({'local_validation':'PASS','trusted_enforcement':'NOT ESTABLISHED',**context}),encoding='utf-8')
    except Exception as error:
        (evidence/'refusal.json').write_text(json.dumps({'status':'REFUSED','reason':type(error).__name__}),encoding='utf-8')
        raise SystemExit('Frontend gate refused; inspect preserved evidence') from None

if __name__ == '__main__':
    main()
