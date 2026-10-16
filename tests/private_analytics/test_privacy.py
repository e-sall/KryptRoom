import ast
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "engines/mpc"
sys.path.insert(0, str(CODE))
from analytics_contract import CODE_FILES, source_hash, workflow_hash


class StructuralPrivacyTests(unittest.TestCase):
    def test_only_reveal_service_references_sf_reveal(self):
        for name in ("analytics_contract.py", "analytics_kernel.py", "private_analytics.py", "analytics_reveal.py"):
            tree = ast.parse((CODE / name).read_text())
            reveals = [n for n in ast.walk(tree) if isinstance(n, ast.Attribute) and n.attr == "reveal"
                       and isinstance(n.value, ast.Name) and n.value.id == "sf"]
            self.assertEqual(len(reveals), 1 if name == "analytics_reveal.py" else 0)
            self.assertFalse(any(isinstance(n, ast.ImportFrom) and n.module == "secretflow" and
                                 any(a.name == "reveal" for a in n.names) for n in ast.walk(tree)))

    def test_kernel_has_no_storage_or_reveal_boundary(self):
        tree = ast.parse((CODE / "analytics_kernel.py").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = ast.unparse(node.func)
                self.assertFalse(any(x in name for x in ("reveal", "open", "load", "dump", "print")))

    def test_compute_environment_excludes_sources_and_peer_state(self):
        source = (ROOT / "compose.private-analytics.yml").read_text()
        self.assertNotIn("/data/", source)
        self.assertNotIn(".csv", source)
        a, b = source.split("  lab-a:")[1].split("  lab-b:")
        self.assertNotIn("KRYPTROOM_LAB_B_STATE_DIR", a)
        self.assertNotIn("KRYPTROOM_LAB_A_STATE_DIR", b)
        runtime = ast.parse((CODE / "private_analytics.py").read_text())
        imported = [n for n in ast.walk(runtime) if isinstance(n, ast.ImportFrom)]
        self.assertFalse(any(any(a.name in ("load_local_dataset", "build_private_join_handoff") for a in n.names) for n in imported))

    def test_code_and_workflow_hashes_are_deterministic(self):
        self.assertEqual(len(CODE_FILES), 7)
        self.assertEqual(source_hash(CODE), source_hash(CODE))
        workflow = ROOT / ".github/workflows/private-analytics.yml"
        self.assertEqual(workflow_hash(workflow), workflow_hash(workflow))
        self.assertEqual(len(workflow_hash(workflow)), 64)

    def test_runtime_pin_and_authoritative_ci_chain(self):
        compose = (ROOT / "compose.private-analytics.yml").read_text()
        self.assertIn("secretflow/secretflow-ubuntu:1.14.0b0@sha256:bdd43242c28466bdc0afddb99d7b50237a94748b5ca7467f8aea73667a38383b", compose)
        ci = (ROOT / ".github/workflows/private-analytics.yml").read_text()
        self.assertIn("tests/private_analytics/run_integration.py", ci)
        self.assertIn("cancel-in-progress: false", ci)


if __name__ == "__main__":
    unittest.main()
