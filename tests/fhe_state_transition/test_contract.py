from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FHE = ROOT / "engines" / "fhe"
MPC = ROOT / "engines" / "mpc"
sys.path[:0] = [str(FHE), str(MPC)]
TEMP_ROOT = ROOT / "build" / "m6-unit"
TEMP_ROOT.mkdir(parents=True, exist_ok=True)

from fhe_contract import (
    CONTEXT_ID,
    EVALUATOR,
    INPUT_ARTIFACT_IDS,
    INPUT_STATE_ID,
    KEY_EPOCH,
    OUTPUT_ARTIFACT_ID,
    OUTPUT_STATE_ID,
    PARTIES,
    REVEAL_NAME,
    artifact_from_file,
    context_from_report,
    create_child_state,
    create_initial_state,
    resolve_uri,
    source_hash,
    validate_context,
    validate_spec,
    verify_artifact_file,
    workflow_hash,
)
from fhe_reveal import FHERevealService
from room_state import canonical_json, create_room_state, load_room_state, write_room_state_exclusive


class Fixture:
    def __init__(self, root: Path):
        self.root = root
        self.roots = {holder: root / holder for holder in (*PARTIES, EVALUATOR)}
        public = self.roots[EVALUATOR] / "crypto"
        public.mkdir(parents=True)
        context_file = public / "openfhe-bgv-context.bin"
        public_key = public / "openfhe-bgv-public-key.bin"
        context_file.write_bytes(b"synthetic-public-context")
        public_key.write_bytes(b"synthetic-public-key")
        from openfhe_backend import sha256_file

        report = {
            "backend": "OpenFHE",
            "backendVersion": "1.5.1.0.24.4",
            "scheme": "BGV-RNS",
            "keyEpoch": KEY_EPOCH,
            "keyOwner": "lab-a",
            "parameters": {
                "plaintextModulus": 65537,
                "multiplicativeDepth": 0,
                "batchSize": 4,
                "securityLevel": "HEStd_128_classic",
                "ringDimension": 4096,
                "serialization": "BINARY",
                "operationSet": ["EvalAdd"],
            },
            "publicMaterials": [
                {
                    "id": "openfhe-bgv-context",
                    "kind": "crypto-context",
                    "fileName": context_file.name,
                    "sha256": sha256_file(context_file),
                    "sizeBytes": context_file.stat().st_size,
                },
                {
                    "id": "openfhe-bgv-public-key",
                    "kind": "public-key",
                    "fileName": public_key.name,
                    "sha256": sha256_file(public_key),
                    "sizeBytes": public_key.stat().st_size,
                },
            ],
            "evaluationMaterials": [],
        }
        self.context = context_from_report(report)
        artifacts = []
        for identifier, holder in zip(INPUT_ARTIFACT_IDS, PARTIES, strict=True):
            path = resolve_uri(
                f"local://{holder}/rooms/cancer-collaboration-room/states/{INPUT_STATE_ID}/artifacts/{identifier}.openfhe.bin",
                self.roots,
            )
            path.parent.mkdir(parents=True)
            path.write_bytes(f"synthetic-{holder}-ciphertext".encode())
            artifacts.append(
                artifact_from_file(
                    artifact_id=identifier,
                    holder=holder,
                    state_id=INPUT_STATE_ID,
                    path=path,
                    context=self.context,
                )
            )
        self.parent = create_initial_state(self.context, tuple(artifacts))
        output_path = resolve_uri(
            f"local://{EVALUATOR}/rooms/cancer-collaboration-room/states/{OUTPUT_STATE_ID}/artifacts/{OUTPUT_ARTIFACT_ID}.openfhe.bin",
            self.roots,
        )
        output_path.parent.mkdir(parents=True)
        output_path.write_bytes(b"synthetic-result-ciphertext")
        output = artifact_from_file(
            artifact_id=OUTPUT_ARTIFACT_ID,
            holder=EVALUATOR,
            state_id=OUTPUT_STATE_ID,
            path=output_path,
            context=self.context,
        )
        self.spec = json.loads(
            (ROOT / "demos/cancer-collaboration/m6/fhe-vector-add-job.json").read_text()
        )
        self.code_hash = source_hash(FHE)
        self.flow_hash = workflow_hash(ROOT / ".github/workflows/fhe-state-transition.yml")
        self.child = create_child_state(
            self.parent, self.spec, output, self.code_hash, self.flow_hash
        )


class FHEContractTests(unittest.TestCase):
    def test_public_job_and_room_states_validate_against_closed_schemas(self):
        from jsonschema import Draft202012Validator

        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp:
            fixture = Fixture(Path(temp))
            job_schema = json.loads(
                (ROOT / "packages/manifests/fhe-state-transition.schema.json").read_text()
            )
            state_schema = json.loads(
                (ROOT / "packages/manifests/room-state.schema.json").read_text()
            )
            Draft202012Validator(job_schema).validate(fixture.spec)
            validator = Draft202012Validator(state_schema)
            validator.validate(fixture.parent.to_dict())
            validator.validate(fixture.child.to_dict())

    def test_context_and_state_bind_exact_public_material_and_lineage(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp:
            fixture = Fixture(Path(temp))
            self.assertEqual(fixture.context.id, CONTEXT_ID)
            self.assertEqual(fixture.context.key_owner, "lab-a")
            self.assertEqual(fixture.context.key_epoch, KEY_EPOCH)
            self.assertEqual(fixture.context.evaluation_material_refs, ())
            self.assertEqual(fixture.child.parent_state_ids, (INPUT_STATE_ID,))
            self.assertEqual(fixture.child.id, OUTPUT_STATE_ID)
            self.assertNotEqual(fixture.child.commitment, fixture.parent.commitment)
            encoded = canonical_json(fixture.child.to_dict())
            self.assertNotIn(b"private-key", encoded)
            self.assertNotIn(b"secretKey", encoded)

    def test_state_is_immutable_and_round_trips(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp:
            fixture = Fixture(Path(temp))
            path = Path(temp) / "state.json"
            write_room_state_exclusive(fixture.child, path)
            self.assertEqual(load_room_state(path), fixture.child)
            with self.assertRaises(FileExistsError):
                write_room_state_exclusive(fixture.child, path)

    def test_computation_and_reveal_are_separate_authorizations(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp:
            fixture = Fixture(Path(temp))
            validate_spec(fixture.spec, fixture.parent)
            requested = copy.deepcopy(fixture.spec)
            requested["requestedReveals"] = [REVEAL_NAME]
            with self.assertRaises(ValueError):
                validate_spec(requested, fixture.parent)
            blocked_policy = replace(fixture.parent.policy, allowed_operators=())
            blocked = create_room_state(
                state_id=fixture.parent.id,
                room_id=fixture.parent.room_id,
                parent_state_ids=fixture.parent.parent_state_ids,
                artifacts=fixture.parent.artifacts,
                transition=fixture.parent.transition,
                policy=blocked_policy,
                crypto_context=fixture.parent.crypto_context,
            )
            with self.assertRaises(PermissionError):
                validate_spec(fixture.spec, blocked)

    def test_unauthorized_reveal_fails_before_any_artifact_or_key_read(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp:
            fixture = Fixture(Path(temp))
            for root in fixture.roots.values():
                for path in sorted(root.rglob("*"), reverse=True):
                    if path.is_file():
                        path.unlink()
            with self.assertRaises(PermissionError):
                FHERevealService().reveal_vector(
                    parent=fixture.parent,
                    child=fixture.child,
                    reveal_name=REVEAL_NAME,
                    recipients=("ui",),
                    roots={EVALUATOR: fixture.roots[EVALUATOR]},
                    private_key_path=Path(temp) / "missing-private-key.bin",
                )

    def test_context_epoch_or_parameter_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp:
            fixture = Fixture(Path(temp))
            with self.assertRaises(ValueError):
                validate_context(replace(fixture.context, key_epoch="other-epoch"))
            changed = json.loads(fixture.context.parameters_json)
            changed["plaintextModulus"] = 17
            with self.assertRaises(ValueError):
                validate_context(
                    replace(
                        fixture.context,
                        parameters_json=canonical_json(changed).decode(),
                    )
                )

    def test_rebound_parent_still_rejects_changed_transition(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp:
            fixture = Fixture(Path(temp))
            changed = create_room_state(
                state_id=fixture.parent.id,
                room_id=fixture.parent.room_id,
                parent_state_ids=fixture.parent.parent_state_ids,
                artifacts=fixture.parent.artifacts,
                transition=replace(fixture.parent.transition, input_job_id="other-job"),
                policy=fixture.parent.policy,
                crypto_context=fixture.parent.crypto_context,
            )
            with self.assertRaisesRegex(ValueError, "initial FHE encryption transition"):
                validate_spec(fixture.spec, changed)

    def test_ciphertext_tampering_is_rejected_before_backend_load(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp:
            fixture = Fixture(Path(temp))
            artifact = fixture.parent.artifacts[0]
            path = resolve_uri(artifact.ciphertexts[0].uri, fixture.roots)
            path.write_bytes(path.read_bytes() + b"tampered")
            with self.assertRaisesRegex(ValueError, "commitment verification"):
                verify_artifact_file(
                    artifact,
                    state_id=fixture.parent.id,
                    holder="lab-a",
                    context=fixture.context,
                    roots=fixture.roots,
                )

    def test_resolver_rejects_unavailable_holder_and_traversal(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp:
            roots = {"lab-a": Path(temp)}
            with self.assertRaises(PermissionError):
                resolve_uri("local://lab-b/artifact.bin", roots)
            with self.assertRaises(ValueError):
                resolve_uri("local://lab-a/../private/key.bin", roots)


if __name__ == "__main__":
    unittest.main()