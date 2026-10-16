import ast
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "engines/mpc"
sys.path.insert(0, str(CODE))

from nn_contract import CODE_FILES, MODEL_IDS, source_hash, workflow_hash
from room_state import (
    ENVELOPE_MAGIC, EncryptedShareReader, EncryptedShareWriter, artifact_aad,
    ensure_local_state_key,
)


class PrivateNNPrivacyTests(unittest.TestCase):
    def test_single_secretflow_reconstruction_boundary_remains_reveal_service(self):
        approved = "analytics_reveal.py"
        for name in ("nn_contract.py", "nn_kernel.py", "private_nn.py", "analytics_reveal.py"):
            tree = ast.parse((CODE / name).read_text())
            reveals = [node for node in ast.walk(tree)
                       if isinstance(node, ast.Attribute) and node.attr == "reveal"
                       and isinstance(node.value, ast.Name) and node.value.id == "sf"]
            self.assertEqual(len(reveals), 1 if name == approved else 0, name)

    def test_training_and_evaluation_kernel_have_no_io_or_reveal(self):
        tree = ast.parse((CODE / "nn_kernel.py").read_text())
        forbidden = ("reveal", "open", "load", "dump", "print", "write", "read")
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                self.assertFalse(any(word in ast.unparse(node.func).lower() for word in forbidden))

    def test_runtime_does_not_import_plaintext_dataset_helpers(self):
        tree = ast.parse((CODE / "private_nn.py").read_text())
        imported = [alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
                    for alias in node.names]
        imported.extend(alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
                        for alias in node.names)
        self.assertNotIn("load_local_dataset", imported)
        self.assertNotIn("build_private_join_handoff", imported)
        self.assertNotIn("csv", imported)
        source = (CODE / "private_nn.py").read_text()
        self.assertNotIn("patient_id", source)

    def test_training_compose_has_no_sources_or_peer_state(self):
        compose = (ROOT / "compose.private-nn.yml").read_text()
        self.assertNotIn("/data/", compose)
        self.assertNotIn(".csv", compose)
        lab_a, lab_b = compose.split("  lab-a:")[1].split("  lab-b:")
        self.assertNotIn("KRYPTROOM_LAB_B_STATE_DIR", lab_a)
        self.assertNotIn("KRYPTROOM_LAB_A_STATE_DIR", lab_b)
        self.assertNotIn("control", compose.lower())

    def test_only_final_parameters_and_mse_are_persistent_outputs(self):
        runtime = (CODE / "private_nn.py").read_text()
        for name in MODEL_IDS:
            self.assertIn(name, (CODE / "nn_contract.py").read_text())
        for forbidden in ("activation.share.enc", "gradient.share.enc", "prediction.share.enc",
                          "training-loss.share.enc", "row-error.share.enc"):
            self.assertNotIn(forbidden, runtime)
        self.assertIn('EVALUATION_ID = "model-evaluation-mse"', (CODE / "nn_contract.py").read_text())

    def test_node_local_model_envelopes_use_context_bound_aes_gcm(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            base = Path(temp)
            a, b = base / "a", base / "b"
            for root in (a, b):
                ensure_local_state_key(str(root / "key"))
            self.assertNotEqual((a / "key").read_bytes(), (b / "key").read_bytes())
            for root, party in ((a, "lab-a"), (b, "lab-b")):
                aad = artifact_aad(room_id="room", state_id="S3_model", artifact_id=MODEL_IDS[0],
                                   party=party, crypto_context_id="secretflow-spu-cheetah-fm128-v1")
                path = root / "model.share.enc"
                with EncryptedShareWriter(str(path), str(root / "key"), aad)() as output:
                    output.write(b"synthetic-local-spu-share")
                self.assertTrue(path.read_bytes().startswith(ENVELOPE_MAGIC))
                with EncryptedShareReader(str(path), str(root / "key"), aad)() as source:
                    self.assertEqual(source.read(), b"synthetic-local-spu-share")
                with self.assertRaisesRegex(ValueError, "authentication"):
                    with EncryptedShareReader(str(path), str(root / "key"), aad + b"wrong")():
                        pass

    def test_code_workflow_and_runtime_are_pinned_reproducibly(self):
        self.assertEqual(source_hash(CODE), source_hash(CODE))
        workflow = ROOT / ".github/workflows/private-nn.yml"
        self.assertEqual(workflow_hash(workflow), workflow_hash(workflow))
        compose = (ROOT / "compose.private-nn.yml").read_text()
        image = "secretflow/secretflow-ubuntu:1.14.0b0@sha256:bdd43242c28466bdc0afddb99d7b50237a94748b5ca7467f8aea73667a38383b"
        self.assertIn(image, compose)
        self.assertNotIn(":latest", compose)
        self.assertIn("cancel-in-progress: false", workflow.read_text())

    def test_public_fixture_has_six_matches_but_runtime_has_no_formula(self):
        def ids(path):
            return {line.split(",")[0] for line in path.read_text().splitlines()[1:]}
        a = ids(ROOT / "demos/cancer-collaboration/m4/lab-a/private-join.csv")
        b = ids(ROOT / "demos/cancer-collaboration/m4/lab-b/private-join.csv")
        self.assertEqual(len(a & b), 6)
        runtime = "\n".join((CODE / name).read_text() for name in ("nn_contract.py", "nn_kernel.py", "private_nn.py"))
        self.assertNotIn("252", runtime)
        self.assertNotIn("438", runtime)
        self.assertNotIn("target-generation", runtime)

    def test_m4_manifest_and_room_state_contracts_are_closed(self):
        schema = json.loads((ROOT / "packages/manifests/private-nn.schema.json").read_text())
        self.assertFalse(schema["additionalProperties"])
        for name in ("selector", "model", "training", "evaluation", "trainingTransition", "evaluationTransition"):
            self.assertFalse(schema["$defs"][name]["additionalProperties"])
        room = json.loads((ROOT / "packages/manifests/room-state.schema.json").read_text())
        self.assertFalse(room["additionalProperties"])
        self.assertEqual(room["$defs"]["artifactRef"]["properties"]["includesIdentifiers"]["const"], False)


if __name__ == "__main__":
    unittest.main()
