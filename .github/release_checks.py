"""Measured release evidence, not an independent signature or trusted PR authority."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tarfile

spec = importlib.util.spec_from_file_location('gate', Path(__file__).with_name('frontend_security_gate.py'))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def verify_scan(report, returncode, image_id):
    gate.require(type(returncode) is int and returncode == 0, 'Scanner failed or found vulnerabilities')
    gate.require(type(report) is dict and report.get('SchemaVersion') == 2, 'Invalid scanner report')
    gate.require(report.get('Metadata', {}).get('ImageID') == image_id, 'Wrong image scanned')
    results = report.get('Results')
    gate.require(type(results) is list and results, 'Missing scan results')
    gate.require(any(r.get('Class') == 'os-pkgs' and r.get('Packages') for r in results), 'OS inventory absent')
    for result in results:
        gate.require(type(result) is dict and result.get('Class') in {'os-pkgs', 'lang-pkgs'}, 'Unexpected scan class')
        gate.require(not result.get('Vulnerabilities'), 'Unresolved image findings (including unfixed)')


def measure(archive, image_id):
    gate.require(re.fullmatch(r'sha256:[0-9a-f]{64}', image_id) is not None, 'Invalid image ID')
    with tarfile.open(archive) as tar:
        manifest = gate.decode(tar.extractfile('manifest.json').read())
        gate.require(type(manifest) is list and len(manifest) == 1, 'One image per archive required')
        config = tar.extractfile(manifest[0]['Config']).read()
        config_id = 'sha256:' + hashlib.sha256(config).hexdigest()
        if image_id != config_id:
            # Docker's containerd store returns the OCI manifest digest as .Id;
            # classic Docker returns the config digest. Verify both, never tags.
            raw = tar.extractfile('blobs/sha256/' + image_id.removeprefix('sha256:')).read()
            gate.require('sha256:' + hashlib.sha256(raw).hexdigest() == image_id, 'Manifest digest mismatch')
            image_manifest = gate.decode(raw)
            if image_manifest.get('mediaType') in {
                'application/vnd.oci.image.index.v1+json',
                'application/vnd.docker.distribution.manifest.list.v2+json',
            }:
                # A pulled multi-platform pin can be .Id while the saved archive
                # contains only one platform. Bind that exact platform descriptor;
                # never treat an index digest as the scanned config digest.
                config_data = gate.decode(config)
                platform = {key: config_data.get(key) for key in ('os', 'architecture')}
                gate.require(all(type(value) is str and value for value in platform.values()), 'Missing platform')
                descriptors = image_manifest.get('manifests')
                gate.require(type(descriptors) is list and 0 < len(descriptors) <= 64, 'Invalid image index')
                matches = [d for d in descriptors if type(d) is dict and
                           all(d.get('platform', {}).get(key) == value for key, value in platform.items())]
                gate.require(len(matches) == 1, 'Missing/ambiguous platform descriptor')
                descriptor = matches[0]
                child_id, size = descriptor.get('digest'), descriptor.get('size')
                gate.require(type(child_id) is str and re.fullmatch(r'sha256:[0-9a-f]{64}', child_id), 'Invalid child digest')
                gate.require(type(size) is int and 0 < size <= 1024 * 1024, 'Invalid child size')
                child_file = tar.extractfile('blobs/sha256/' + child_id[7:])
                child = child_file.read(size + 1)
                gate.require(len(child) == size and 'sha256:' + hashlib.sha256(child).hexdigest() == child_id, 'Child manifest mismatch')
                image_manifest = gate.decode(child)
            gate.require(image_manifest.get('config', {}).get('digest') == config_id, 'Archive/config mismatch')
    with Path(archive).open('rb') as stream:
        archive_sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'image_id': image_id, 'config_id': config_id, 'sha256': archive_sha}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    (args.directory / 'PROVENANCE.json').unlink(missing_ok=True)
    gate.require(re.fullmatch('[0-9a-f]{40}', args.source) is not None, 'Exact source SHA required')
    images = {}
    for name in ('api', 'web', 'postgres', 'keycloak'):
        image_id = (args.directory / (name + '.id')).read_text().strip()
        images[name] = measure(args.directory / (name + '.tar'), image_id)
        report = gate.decode((args.directory / (name + '.scan.json')).read_bytes())
        code = int((args.directory / (name + '.scan.exit')).read_text())
        verify_scan(report, code, images[name]['config_id'])
    (args.directory / 'PROVENANCE.json').write_text(json.dumps({'source_sha': args.source, 'images': images, 'independently_signed': False}, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
