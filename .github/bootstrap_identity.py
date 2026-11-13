"""Native disposable CI controller; original identity acceptance, scan before cleanup."""
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys


def main():
    root = Path(os.environ['GITHUB_WORKSPACE'])
    service = root/'services/control-api'
    if os.name != 'posix' or os.geteuid() != 0 or str(root).startswith('/mnt/'):
        raise RuntimeError('Native Linux trusted fixture controller required')
    source = runpy.run_path(str(service/'scripts/identity-stack-acceptance.py'))
    acceptance = source['acceptance']
    compose = source['compose']
    try:
        compose('down','--volumes','--remove-orphans')
        runpy.run_path(str(service/'scripts/local-secrets.py'),run_name='__main__')
        compose('config','--quiet')
        compose('build')
        compose('run','--rm','identity-prepare')
        compose('up','-d','api','keycloak','bff')
        source['wait_ready']()
        acceptance['browser_acceptance']()
        privacy = runpy.run_path(str(service/'scripts/identity-privacy.py'))
        print(json.dumps(privacy['verify']()))
        # No claim that a separately rebuilt image equals a preflight image.
        # Inspect and rescan the actual running IDs before cleanup/acceptance.
        subprocess.run([sys.executable,str(root/'.github/bootstrap_images.py'),'--running'],check=True,timeout=1800)
    finally:
        print(acceptance['sanitized_browser_log']())
        compose('--profile','operator','down','--volumes','--remove-orphans')


if __name__ == '__main__':
    main()
