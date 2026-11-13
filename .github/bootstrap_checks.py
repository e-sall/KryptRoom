"""Owner-controlled diagnostic bootstrap, not independent review or release approval."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

BRANCH = 'release/m9-hosted-ci-20261112'
BASE = 'd8a5c0aa7ed845c31bd2ff40c1b3491246c6cf83'
CI_FILES = {
    '.github/ci_scope.py', '.github/fixtures/frontend-security-audit.json',
    '.github/frontend_security_gate.py', '.github/release_checks.py',
    '.github/test_frontend_security_gate.py', '.github/test_m9_ci_scope.py',
    '.github/test_m9_identity_ci_scope.py', '.github/test_release_checks.py',
    '.github/test_release_workflow.py', '.github/bootstrap_checks.py',
    '.github/bootstrap_images.py', '.github/bootstrap_identity.py', '.github/bootstrap_audit.py', '.github/test_bootstrap.py',
    '.github/workflows/control-api-identity.yml', '.github/workflows/web-foundation.yml',
    '.github/workflows/m9-release-readiness.yml', '.github/workflows/m9-hosted-bootstrap.yml',
}
DOCS = {'PROJECT_CONTEXT.md', 'ARCHITECTURE.md', 'CHANGELOG.md', 'TODO.md', 'docs/DECISIONS.md'}


def permitted_path(path):
    # A diagnostic build allowlist, NOT a core=false classification exemption.
    return path in CI_FILES | DOCS or path.startswith(('services/control-api/', 'apps/web/', 'docs/m9/', 'docs/m8/'))


def policy(event_name, event, repository, head, read_git):
    if repository != 'e-sall/KryptRoom' or event_name not in ('push', 'pull_request'):
        raise ValueError('Unsupported repository/event')
    if event_name == 'push':
        if event['ref'] != 'refs/heads/' + BRANCH or event.get('deleted'):
            raise ValueError('Unsupported/deleted push ref')
        if event['after'] != head:
            raise ValueError('Push checkout mismatch')
    else:
        pr = event['pull_request']
        if pr['head']['repo']['full_name'] != repository:
            raise ValueError('Foreign source refused before applicability')
        if pr['head']['ref'] != BRANCH:
            return False
        if pr['head']['repo']['full_name'] != repository or pr['base']['ref'] != 'dev' or pr['base']['sha'] != BASE:
            raise ValueError('Foreign source or wrong target')
        if event['action'] not in ('opened', 'reopened', 'synchronize') or pr['merge_commit_sha'] != head:
            raise ValueError('Unexpected PR event/merge checkout')
    if not re.fullmatch('[0-9a-f]{40}', head):
        raise ValueError('Invalid source SHA')
    read_git('merge-base', '--is-ancestor', BASE, head)
    paths = read_git('diff', '--no-renames', '--name-only', '-z', BASE, head).split('\0')
    if any(not permitted_path(p) for p in paths if p):
        raise ValueError('Core/unknown input changed; diagnostics refused before installs')
    return True


def aggregate(applicable, results):
    if results.get('policy') != 'success':
        raise ValueError('Policy failed/missing/cancelled')
    required = {'policy', 'backend', 'security', 'images', 'frontend', 'identity'}
    if set(results) != required:
        raise ValueError('Missing/unknown required consumer')
    if applicable == 'true':
        if any(value != 'success' for value in results.values()):
            raise ValueError('Release refused: a required consumer failed/cancelled/skipped')
    elif applicable == 'false':
        if any(value != 'skipped' for key, value in results.items() if key != 'policy'):
            raise ValueError('Unexpected execution on non-applicable PR')
    else:
        raise ValueError('Missing applicability')


def require_pr_validation(event_name, scopes):
    if event_name == 'pull_request' and scopes['core']:
        raise ValueError('Core validation outstanding; bootstrap PR cannot be green while crypto execution is refused')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['policy', 'aggregate'])
    args = parser.parse_args()
    if args.mode == 'policy':
        def git(*command):
            return subprocess.check_output(['git', *command], text=True)
        head = git('rev-parse', 'HEAD').strip()
        if head != os.environ['GITHUB_SHA']:
            raise ValueError('Checkout SHA mismatch')
        event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
        applicable = policy(os.environ['GITHUB_EVENT_NAME'], event, os.environ['GITHUB_REPOSITORY'], head, git)
        if applicable:
            from ci_scope import classify_scopes_event
            scopes = classify_scopes_event(os.environ['GITHUB_EVENT_NAME'], event, git)
            require_pr_validation(os.environ['GITHUB_EVENT_NAME'], scopes)
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
            f.write('applicable=' + str(applicable).lower() + '\n')
        print(json.dumps({'applicable': applicable, 'head': head, 'baseline': BASE, 'independent_review': False}))
    else:
        aggregate(os.environ['APPLICABLE'], json.loads(os.environ['RESULTS']))
        print('Explicit bootstrap decision; no production or merge authorization')


if __name__ == '__main__':
    main()
