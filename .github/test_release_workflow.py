"""Static contract tests; hosted execution is separately required, never inferred."""
from pathlib import Path
import re
import unittest


class ReleaseWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = (Path(__file__).parent / 'workflows/m9-release-readiness.yml').read_text()

    def test_actions_permissions_and_no_audit_exceptions(self):
        actions = re.findall(r'uses: (\S+)', self.text)
        self.assertGreater(len(actions), 5)
        self.assertTrue(all(re.fullmatch(r'actions/[a-z-]+@[0-9a-f]{40}', action) for action in actions))
        for forbidden in ('pull_request_target', 'contents: write', 'id-token:', '${{ secrets.', 'continue-on-error:', '--ignore-unfixed', '--severity', 'npm audit fix', '--legacy-peer-deps'):
            self.assertNotIn(forbidden, self.text)

    def test_security_is_dependency_before_frontend_execution(self):
        packaging = self.text.split('  release-packaging:', 1)[1].split('  release-ready:', 1)[0]
        self.assertIn('needs: [release-policy, release-security, release-backend]', packaging)
        self.assertNotIn('if: always()', packaging.split('    steps:', 1)[0])
        self.assertIn('run: python3 .github/frontend_security_gate.py', self.text)
        self.assertIn('python3 .github/release_checks.py --source "$GITHUB_SHA"', packaging)

    def test_required_result_checks_failures_and_non_applicability(self):
        ready = self.text.split('  release-ready:', 1)[1]
        self.assertIn('if: always()', ready)
        for key in ('POLICY', 'BACKEND', 'SECURITY', 'PACKAGING'):
            self.assertIn(f'test "${key}" = success', ready)
        self.assertIn('test "$M9" = false\n            test "$WEB" = false', ready)


if __name__ == '__main__':
    unittest.main()
