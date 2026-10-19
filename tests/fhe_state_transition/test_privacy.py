import ast
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FHE = ROOT / "engines" / "fhe"


class FHEStructuralPrivacyTests(unittest.TestCase):
    def test_evaluator_has_no_decryption_or_private_key_path(self):
        for name in ("fhe_kernel.py", "fhe_transition.py"):
            source = (FHE / name).read_text(encoding="utf-8")
            tree = ast.parse(source)
            calls = [ast.unparse(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)]
            self.assertFalse(any(call.endswith(".Decrypt") for call in calls))
            self.assertFalse(any("deserialize_private_key" in call for call in calls))
            self.assertNotIn("private_key_path", source)
        kernel = (FHE / "fhe_kernel.py").read_text(encoding="utf-8")
        self.assertIn("EvalAdd", kernel)
        self.assertNotIn("MakePackedPlaintext", kernel)

    def test_no_mock_or_plaintext_fallback(self):
        for path in FHE.glob("*.py"):
            source = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("mock_cipher", source)
            self.assertNotIn("plaintext_fallback", source)
            self.assertNotIn("decrypt_then", source)

    def test_decryption_is_behind_policy_check(self):
        source = (FHE / "fhe_reveal.py").read_text(encoding="utf-8")
        method = source.index("def reveal_vector")
        authorization = source.index("child.policy.authorizes", method)
        private_key_call = source.index("deserialize_private_key(fhe", method)
        self.assertLess(authorization, private_key_call)
        tree = ast.parse(source)
        calls = [ast.unparse(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)]
        self.assertIn("context.Decrypt", calls)

    def test_exact_wheel_and_real_ci_gate_are_pinned(self):
        requirement = (ROOT / "tests/fhe_state_transition/requirements-openfhe.txt").read_text()
        self.assertIn("openfhe==1.5.1.0.24.4", requirement)
        self.assertIn("sha256:b39f50f570ea1236dc8a8c64b01552848eb66c068592c4178fa37249f182106e", requirement)
        workflow = (ROOT / ".github/workflows/fhe-state-transition.yml").read_text()
        self.assertIn("--require-hashes", workflow)
        self.assertIn("tests/fhe_state_transition/run_integration.py", workflow)
        self.assertIn("cancel-in-progress: false", workflow)

    def test_schema_names_real_fhe_protection(self):
        schema = json.loads((ROOT / "packages/manifests/room-state.schema.json").read_text())
        artifact = schema["$defs"]["artifactRef"]
        self.assertEqual(artifact["properties"]["protection"]["const"], "fhe_ciphertext")
        self.assertIn("openfhe-ciphertext", artifact["properties"]["kind"]["enum"])


if __name__ == "__main__":
    unittest.main()
