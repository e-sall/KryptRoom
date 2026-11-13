"""Build/scan without executing PG/IdP services; preserve every refusal."""
import json
import argparse
import os
from pathlib import Path
import subprocess
import re
from release_checks import measure, verify_scan


def supported_postgres(version):
    match = re.match(r'^17\.(\d+)(?:\D|$)',version)
    return bool(match and int(match[1]) >= 12)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--running', action='store_true')
    args = parser.parse_args()
    root = Path(os.environ['GITHUB_WORKSPACE'])
    out = root/('bootstrap-running-images' if args.running else 'bootstrap-images')
    out.mkdir()
    scanner = os.environ['SCANNER_IMAGE']
    cache = root/'bootstrap-scanner-cache'
    cache.mkdir(exist_ok=True)
    if os.getuid() == 0:
        os.chown(cache,10001,10001)
        uid = '10001:10001'
    else:
        uid = f'{os.getuid()}:{os.getgid()}'
    def run(*args, **kwargs):
        return subprocess.run(list(args), check=True, timeout=1200, **kwargs)
    if args.running:
        names = ['api','postgres','keycloak','web']
        for name in names:
            service = 'bff' if name == 'web' else name
            container = subprocess.check_output(['docker','compose','-p','kr-m9-pr2-real','-f',str(root/'services/control-api/compose.identity.yml'),'ps','-q',service],text=True).strip()
            if not container:
                raise ValueError('Missing running acceptance service')
            (out/(name+'.id')).write_text(subprocess.check_output(['docker','inspect','--format','{{.Image}}',container],text=True).strip())
    else:
        names = ['api','postgres','postgres-candidate','keycloak']
        for name, context, recipe, target in [
            ('api', 'services/control-api', 'Dockerfile', ['--target', 'runtime']),
            ('postgres-candidate', 'services/control-api', 'Dockerfile.postgres-candidate', []),
        ]:
            run('docker', 'build', '--iidfile', str(out/(name+'.id')), *target, '-f', str(root/context/recipe), str(root/context))
        for name in ['postgres','keycloak']:
            ref = os.environ[name.upper()+'_IMAGE']
            if '@sha256:' not in ref:
                raise ValueError('Unpinned service image')
            run('docker', 'pull', ref)
            (out/(name+'.id')).write_text(subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',ref],text=True).strip())
    common = ['docker','run','--rm','--user',uid,'--read-only','--cap-drop','ALL','--security-opt','no-new-privileges:true','--tmpfs','/tmp','-e','HOME=/tmp','-v',str(cache)+':/cache']
    for option in ['--download-db-only', '--download-java-db-only']:
        run(*common,scanner,'image','--cache-dir','/cache',option)
    results = {}
    refused = False
    for name in names:
        image_id = (out/(name+'.id')).read_text().strip()
        archive = out/(name+'.tar')
        run('docker','image','save','-o',str(archive),image_id)
        measured = measure(archive,image_id)
        with (out/(name+'.scan.json')).open('wb') as stdout, (out/(name+'.stderr.txt')).open('wb') as stderr:
            code = subprocess.run([*common,'--network','none','-v',str(out)+':/images:ro',scanner,'image','--cache-dir','/cache','--skip-db-update','--skip-java-db-update','--offline-scan','--scanners','vuln','--list-all-pkgs','--format','json','--exit-code','1','--input','/images/'+name+'.tar'],stdout=stdout,stderr=stderr,timeout=1200).returncode
        (out/(name+'.exit')).write_text(str(code))
        try:
            verify_scan(json.loads((out/(name+'.scan.json')).read_bytes()),code,measured['config_id'])
            status = 'PASS'
        except (ValueError, KeyError, TypeError):
            status = 'REFUSED'
            refused = True
        results[name] = {**measured,'exit':code,'status':status}
    (out/'MEASUREMENTS.json').write_text(json.dumps({'source_sha':os.environ['GITHUB_SHA'],'images':results,'independently_signed':False},indent=2))
    pg_env = json.loads(subprocess.check_output(['docker','image','inspect','--format','{{json .Config.Env}}',(out/'postgres.id').read_text().strip()],text=True))
    version = next((v.split('=',1)[1] for v in pg_env if v.startswith('PG_VERSION=')), '')
    if not supported_postgres(version):
        (out/'VERSION-REFUSAL.json').write_text(json.dumps({'postgres':version,'minimum':'17.12','status':'REFUSED'}))
        refused = True
    if refused:
        raise SystemExit('Image security refused; all raw findings retained; acceptance/release cannot pass')


if __name__ == '__main__':
    main()
