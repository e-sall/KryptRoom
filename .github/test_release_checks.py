import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import tarfile
import unittest
from unittest.mock import patch

import release_checks as checks


class ReleaseEvidenceTests(unittest.TestCase):
    def test_refusal_removes_stale_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = Path(directory) / 'PROVENANCE.json'
            previous.write_text('{"stale":"PASS"}')
            with patch('sys.argv', ['release_checks.py', '--source', 'a'*40, '--directory', directory]):
                with self.assertRaises(FileNotFoundError):
                    checks.main()
            self.assertFalse(previous.exists())

    def report(self):
        return {'SchemaVersion': 2, 'Metadata': {'ImageID': 'sha256:' + 'a'*64}, 'Results': [{'Class': 'os-pkgs', 'Packages': [{'Name': 'libc6'}], 'Vulnerabilities': []}]}

    def test_clean_bound_inventory(self):
        checks.verify_scan(self.report(), 0, 'sha256:' + 'a'*64)

    def test_failures_do_not_become_clean(self):
        for code in (1, 2, -9, None, True):
            with self.subTest(code=code), self.assertRaises(ValueError):
                checks.verify_scan(self.report(), code, 'sha256:' + 'a'*64)

    def test_wrong_image_empty_missing_inventory_and_findings(self):
        cases = [{}, {**self.report(), 'Results': []}, {**self.report(), 'Metadata': {'ImageID': 'wrong'}}]
        for mutation in ({'Vulnerabilities': [{'VulnerabilityID': 'unfixed', 'Severity': 'LOW'}]}, {'Packages': []}, {'Class': 'unknown'}):
            report = copy.deepcopy(self.report())
            report['Results'][0].update(mutation)
            cases.append(report)
        for report in cases:
            with self.subTest(report=report), self.assertRaises(ValueError):
                checks.verify_scan(report, 0, 'sha256:' + 'a'*64)

    def test_archive_config_tampering(self):
        config = b'{"architecture":"amd64"}'
        expected = 'sha256:' + hashlib.sha256(config).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'image.tar'
            with tarfile.open(path, 'w') as tar:
                for name, data in [('manifest.json', json.dumps([{'Config': 'config.json'}]).encode()), ('config.json', config)]:
                    info = tarfile.TarInfo(name)
                    info.size = len(data)
                    tar.addfile(info, io.BytesIO(data))
            self.assertEqual(checks.measure(path, expected)['image_id'], expected)
            with self.assertRaises((ValueError, KeyError)):
                checks.measure(path, 'sha256:' + '0'*64)

    def test_containerd_manifest_id_binds_to_scan_config_id(self):
        config = b'{"architecture":"amd64"}'
        config_id = 'sha256:' + hashlib.sha256(config).hexdigest()
        image_manifest = json.dumps({'schemaVersion': 2, 'config': {'digest': config_id}}).encode()
        manifest_id = 'sha256:' + hashlib.sha256(image_manifest).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'oci.tar'
            with tarfile.open(path, 'w') as tar:
                for name, data in [('manifest.json', json.dumps([{'Config': 'config.json'}]).encode()), ('config.json', config), ('blobs/sha256/' + manifest_id[7:], image_manifest)]:
                    info = tarfile.TarInfo(name)
                    info.size = len(data)
                    tar.addfile(info, io.BytesIO(data))
            measured = checks.measure(path, manifest_id)
            self.assertEqual(measured['image_id'], manifest_id)
            self.assertEqual(measured['config_id'], config_id)


if __name__ == '__main__':
    unittest.main()
