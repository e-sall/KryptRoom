"""Executed Python state/policy/storage tests; no mocked cryptographic integration."""
import copy
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engines/mpc"))
from analytics_contract import (
    EXPECTED_CONTEXT, FIXED_POINT_TOLERANCE, INPUT_IDS, KEY_EPOCH, PARTIES,
    artifact_commitment, bind_request, digest, make_transition, output_id,
    validate_child, validate_context, validate_request, validate_spec,
)
from analytics_reveal import RevealService
from room_state import (
    ArtifactRef, AuthorizedReveal, CiphertextRef, CryptoContext, EncryptedShareReader,
    EncryptedShareWriter, StatePolicy, StateTransition, artifact_aad, canonical_json,
    create_room_state, ensure_local_state_key, load_room_state, write_room_state_exclusive,
)


def context():
    from room_state import room_state_from_dict
    c = EXPECTED_CONTEXT
    return CryptoContext(c["id"], c["backend"], c["backendVersion"], c["protocol"], c["field"],
                         c["securityModel"], tuple(c["participants"]), c["artifactCipher"], c["keyScope"])


def artifact(i, shape, dtype="int32", state="S1", salt=""):
    return ArtifactRef(i, "spu-secret-share", "application/vnd.kryptroom.spu-share+encrypted",
                       "secret-shared", context().id, shape, dtype, False, tuple(
        CiphertextRef(p, f"local://{p}/rooms/cancer-collaboration-room/states/{state}/artifacts/{i}.share.enc",
                      digest([p, i, salt]), 123) for p in PARTIES))


def parent(count=2, policy=None, artifacts=None):
    policy = policy or StatePolicy("deny", "forbidden", "forbidden", True,
        (AuthorizedReveal("ciphertext-metadata", PARTIES),
         AuthorizedReveal("analytics.mean.mean-a", PARTIES)), ("private_analytics",), INPUT_IDS)
    artifacts = artifacts or tuple(artifact(i, (4, 4) if i == "match-mask" else (4, 4, 1)) for i in INPUT_IDS)
    return create_room_state(state_id="S1", room_id="cancer-collaboration-room", parent_state_ids=(),
        artifacts=artifacts, transition=StateTransition("join", "private-join", (), "join", INPUT_IDS,
            "2026-10-15T00:00:00Z", canonical_json({"cohortCardinality": count}).decode()),
        policy=policy, crypto_context=context())


def spec():
    return json.loads((ROOT / "demos/cancer-collaboration/analytics-job.json").read_text())


def child(p, s):
    request = bind_request(p, s, "code", "workflow")
    outputs = tuple(artifact(output_id(m), (1,), "int32" if m["op"] == "COUNT" else "float32", "S2")
                    for m in s["metrics"])
    return create_room_state(state_id="S2", room_id=p.room_id, parent_state_ids=(p.id,), artifacts=outputs,
        transition=make_transition(p, request, outputs), policy=p.policy, crypto_context=p.crypto_context)


class AnalyticsContractTests(unittest.TestCase):
    def test_spec_and_states_validate_against_public_schemas(self):
        from jsonschema import Draft202012Validator
        Draft202012Validator(json.loads((ROOT / "packages/manifests/private-analytics.schema.json").read_text())).validate(spec())
        validator = Draft202012Validator(json.loads((ROOT / "packages/manifests/room-state.schema.json").read_text()))
        validator.validate(parent().to_dict())
        validator.validate(child(parent(), spec()).to_dict())

    def test_round_trip_and_immutable_s1_s2(self):
        p = parent()
        before = canonical_json(p.to_dict())
        s = child(p, spec())
        validate_child(s, p, "code", "workflow")
        self.assertEqual(s.parent_state_ids, ("S1",))
        self.assertNotEqual(s.commitment, p.commitment)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            write_room_state_exclusive(s, path)
            self.assertEqual(load_room_state(path).to_dict(), s.to_dict())
            with self.assertRaises(FileExistsError):
                write_room_state_exclusive(s, path)
        self.assertEqual(before, canonical_json(p.to_dict()))

    def test_exact_refs_and_commitments_bound(self):
        p = parent()
        r = bind_request(p, spec(), "code", "workflow")
        self.assertEqual(r["parentStateCommitment"], p.commitment.value)
        for bound, a in zip(r["inputs"], p.artifacts):
            self.assertEqual(bound["artifactRef"], a.to_dict())
            self.assertEqual(bound["commitment"], artifact_commitment(a, p.crypto_context))
        for key in r:
            if key == "spec":
                continue
            changed = copy.deepcopy(r)
            changed[key] = "tampered"
            with self.assertRaises(ValueError):
                validate_request(p, changed, "code", "workflow")

    def test_metric_and_input_changes_change_both_commitments(self):
        p = parent()
        original = child(p, spec())
        changed_spec = spec()
        changed_spec["metrics"][1]["input"]["artifact"] = "lab-b-features"
        changed_input = parent(artifacts=(artifact(INPUT_IDS[0], (4, 4), salt="changed"), *p.artifacts[1:]))
        for changed in (child(p, changed_spec), child(changed_input, spec())):
            self.assertNotEqual(changed.commitment, original.commitment)
            self.assertNotEqual(changed.transition.bindings_json, original.transition.bindings_json)

    def test_deterministic_public_artifact_commitments(self):
        a = parent().artifacts[0]
        self.assertEqual(artifact_commitment(a, context()), artifact_commitment(a, context()))
        self.assertEqual(canonical_json({"b": 1, "a": 2}), canonical_json({"a": 2, "b": 1}))

    def test_zero_cohort_means_fail_closed(self):
        for operation in ("MEAN", "CROSS_MEAN"):
            s = spec()
            s["metrics"] = [m for m in s["metrics"] if m["op"] == operation]
            s["requestedReveals"] = []
            with self.assertRaisesRegex(ValueError, "EMPTY_COHORT"):
                validate_spec(s, parent(0))
        s["metrics"] = [{"id": "zero", "op": "COUNT"}]
        self.assertEqual(validate_spec(s, parent(0)), 0)

    def test_wrong_context_and_epoch_rejected(self):
        c = context()
        for field, wrong in (("protocol", "SEMI2K"), ("field", "FM64"),
                             ("participants", tuple(reversed(PARTIES))), ("backend", "other"),
                             ("id", "other"), ("backend_version", "other")):
            with self.assertRaises(ValueError):
                validate_context(replace(c, **{field: wrong}), KEY_EPOCH)
        with self.assertRaises(ValueError):
            validate_context(c, "rotated-key-epoch")
        with self.assertRaises(ValueError):
            parent(artifacts=(replace(parent().artifacts[0], crypto_context_id="other"), *parent().artifacts[1:]))

    def test_computation_and_reveal_authorization_are_distinct(self):
        p = parent()
        with self.assertRaises(PermissionError):
            validate_spec(spec(), parent(policy=replace(p.policy, allowed_operators=())))
        s = spec()
        s["requestedReveals"].append("analytics.cross_mean.cross-ab")
        with self.assertRaises(PermissionError):
            validate_spec(s, p)

    def test_unsupported_operation_and_private_selectors_rejected(self):
        for mutate in (lambda s: s["metrics"][0].update(op="VARIANCE"),
                       lambda s: s["metrics"][1]["input"].update(column=1),
                       lambda s: s["metrics"][1]["input"].update(artifact="patient_id"),
                       lambda s: s["metrics"][1]["input"].update(alias="private-schema"),
                       lambda s: s.update(inputStateIds=["S1", "S0"])):
            s = spec()
            mutate(s)
            with self.assertRaises(ValueError):
                validate_spec(s, parent())

    def test_unauthorized_reveal_never_loads_transfers_or_reconstructs(self):
        calls = []
        service = RevealService(parent().policy, {}, lambda x: calls.append(x), None)
        with self.assertRaises(PermissionError):
            service.scalar(spec(), "analytics.cross_mean.cross-ab", lambda x: calls.append(x))
        self.assertEqual(calls, [])

    def test_authorized_reveal_only_scalar(self):
        calls = []
        class Secret:
            def to(self, party):
                calls.append(party)
                return 25.0
        service = RevealService(parent().policy, {p: p for p in PARTIES}, lambda x: x, float)
        value = service.scalar(spec(), "analytics.mean.mean-a", lambda i: Secret())
        self.assertAlmostEqual(value, 25, delta=FIXED_POINT_TOLERANCE)
        self.assertEqual(calls, list(PARTIES))

    def test_aes_gcm_wrong_key_context_and_tamper_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            keys = [root / "a.key", root / "b.key"]
            for key in keys:
                ensure_local_state_key(str(key))
            self.assertNotEqual(keys[0].read_bytes(), keys[1].read_bytes())
            aad = artifact_aad(room_id="r", state_id="S2", artifact_id="metric", party="lab-a", crypto_context_id=context().id)
            path = str(root / "metric.share.enc")
            with EncryptedShareWriter(path, str(keys[0]), aad)() as output:
                output.write(b"local-serialized-share-for-unit-test")
            with EncryptedShareReader(path, str(keys[0]), aad)() as source:
                self.assertEqual(source.read(), b"local-serialized-share-for-unit-test")
            for key, binding in ((keys[1], aad), (keys[0], aad + b"wrong")):
                with self.assertRaisesRegex(ValueError, "authentication"):
                    with EncryptedShareReader(path, str(key), binding)():
                        pass
            payload = bytearray(Path(path).read_bytes())
            payload[-1] ^= 1
            Path(path).write_bytes(payload)
            with self.assertRaises(ValueError):
                with EncryptedShareReader(path, str(keys[0]), aad)():
                    pass


if __name__ == "__main__":
    unittest.main()
