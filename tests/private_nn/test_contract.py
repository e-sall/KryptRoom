import copy
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "engines/mpc"
sys.path.insert(0, str(CODE))

from analytics_contract import EXPECTED_CONTEXT, INPUT_IDS, PARTIES, digest
from analytics_reveal import RevealService
from nn_contract import (
    EVALUATION_ID, EVALUATION_OPERATOR, EVALUATION_REVEAL, MODEL_IDS, MODEL_SHAPES,
    TRAINING_OPERATOR, bind_evaluation_request, bind_training_request,
    derive_evaluation_policy, derive_model_policy, initializer_metadata,
    make_evaluation_transition, make_training_transition, validate_evaluation_child,
    validate_evaluation_request, validate_job, validate_model_spec,
    validate_training_child, validate_training_request, validate_training_spec,
)
from room_state import (
    ArtifactRef, AuthorizedReveal, CiphertextRef, CryptoContext, StatePolicy,
    StateTransition, canonical_json, create_room_state,
)


def context():
    c = EXPECTED_CONTEXT
    return CryptoContext(c["id"], c["backend"], c["backendVersion"], c["protocol"],
                         c["field"], c["securityModel"], tuple(c["participants"]),
                         c["artifactCipher"], c["keyScope"])


def artifact(identifier, shape, state, salt="", dtype="int32"):
    return ArtifactRef(
        identifier, "spu-secret-share", "application/vnd.kryptroom.spu-share+encrypted",
        "secret-shared", context().id, shape, dtype, False,
        tuple(CiphertextRef(
            p, f"local://{p}/rooms/cancer-collaboration-room/states/{state}/artifacts/{identifier}.share.enc",
            digest([p, identifier, state, salt]), 123,
        ) for p in PARTIES),
    )


def m4_policy(operators=("private_analytics", TRAINING_OPERATOR, EVALUATION_OPERATOR), reveal=True):
    reveals = [AuthorizedReveal("intersection-cardinality", (*PARTIES, "ui")),
               AuthorizedReveal("ciphertext-metadata", PARTIES),
               AuthorizedReveal("matched-feature-sum", PARTIES)]
    if reveal:
        reveals.append(AuthorizedReveal(EVALUATION_REVEAL, PARTIES))
    return StatePolicy("deny", "forbidden", "forbidden", True, tuple(reveals),
                       tuple(operators), INPUT_IDS)


def s1(policy=None, cardinality=6, salt=""):
    artifacts = tuple(artifact(i, (8, 8) if i == "match-mask" else (8, 8, 1), "S1", salt)
                      for i in INPUT_IDS)
    transition = StateTransition("join-m4", "private-join", (), "join-m4", INPUT_IDS,
                                 "2026-10-16T00:00:00Z",
                                 canonical_json({"cohortCardinality": cardinality}).decode())
    return create_room_state(state_id="S1", room_id="cancer-collaboration-room",
                             parent_state_ids=(), artifacts=artifacts, transition=transition,
                             policy=policy or m4_policy(), crypto_context=context())


def job():
    return json.loads((ROOT / "demos/cancer-collaboration/m4/private-nn-job.json").read_text())


def s3(parent=None, request=None, salt=""):
    parent = parent or s1()
    request = request or bind_training_request(parent, job(), "code", "workflow")
    outputs = tuple(artifact(i, shape, "S3_model", salt, "float32")
                    for i, shape in zip(MODEL_IDS, MODEL_SHAPES, strict=True))
    return create_room_state(
        state_id="S3_model", room_id=parent.room_id, parent_state_ids=(parent.id,),
        artifacts=outputs, transition=make_training_transition(parent, request, outputs),
        policy=derive_model_policy(parent), crypto_context=parent.crypto_context,
    )


def s4(model=None, data=None, request=None, salt=""):
    data = data or s1()
    model = model or s3(data)
    request = request or bind_evaluation_request(model, data, job(), "code", "workflow")
    output = artifact(EVALUATION_ID, (1,), "S4_eval", salt, "float32")
    return create_room_state(
        state_id="S4_eval", room_id=data.room_id, parent_state_ids=(model.id, data.id),
        artifacts=(output,), transition=make_evaluation_transition(model, data, request, output),
        policy=derive_evaluation_policy(model, data), crypto_context=data.crypto_context,
    )


class PrivateNNContractTests(unittest.TestCase):
    def test_public_manifest_schema_and_exact_contract(self):
        from jsonschema import Draft202012Validator
        schema = json.loads((ROOT / "packages/manifests/private-nn.schema.json").read_text())
        # The executable validator is authoritative; schema is closed at every M4 object.
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(job())
        validate_job(job())

    def test_model_and_training_canonicalization(self):
        value = job()
        self.assertEqual(canonical_json(value), canonical_json(json.loads(json.dumps(value, sort_keys=True))))
        self.assertEqual(digest(value["modelSpec"]), digest(copy.deepcopy(value["modelSpec"])))
        self.assertEqual(digest(value["trainingSpec"]), digest(copy.deepcopy(value["trainingSpec"])))

    def test_unknown_model_and_training_keys_are_rejected(self):
        for field in ("modelSpec", "trainingSpec"):
            value = job()
            value[field]["unknown"] = True
            with self.assertRaises(ValueError):
                validate_job(value)

    def test_unsupported_architecture_and_activation_are_rejected_and_change_hash(self):
        original = job()["modelSpec"]
        for mutate in (
            lambda value: value["layers"][0].update(outputDim=3),
            lambda value: value["layers"][1].update(type="relu"),
            lambda value: value["layers"].pop(),
        ):
            changed = copy.deepcopy(original)
            mutate(changed)
            self.assertNotEqual(digest(original), digest(changed))
            with self.assertRaises(ValueError):
                validate_model_spec(changed)

    def test_selectors_identifiers_and_normalization_are_rejected(self):
        for path, value in (("feature-artifact", "patient_id"), ("label-artifact", "join-key"),
                            ("feature-column", 1), ("label-column", 1),
                            ("feature-divisor", 11), ("label-divisor", 999)):
            changed = copy.deepcopy(job()["trainingSpec"])
            side = "feature" if path.startswith("feature") else "label"
            field = "artifact" if path.endswith("artifact") else "column" if path.endswith("column") else "divideBy"
            changed[side][field] = value
            with self.assertRaises(ValueError):
                validate_training_spec(changed)

    def test_initializer_is_exact_and_reproducible(self):
        metadata = initializer_metadata(job()["trainingSpec"])
        self.assertEqual(metadata, initializer_metadata(copy.deepcopy(job()["trainingSpec"])))
        self.assertEqual([t["name"] for t in metadata["tensors"]], ["W1", "b1", "W2", "b2"])
        self.assertEqual([t["shape"] for t in metadata["tensors"]], [[1, 2], [2], [2, 1], [1]])
        self.assertEqual(metadata["tensors"][0]["values"][0], -0.0411223635096415)
        self.assertEqual(len(metadata["commitment"]), 64)

    def test_meaningful_training_changes_affect_hashes_and_are_rejected(self):
        original = job()["trainingSpec"]
        mutations = (
            ("learningRate", 0.3), ("steps", 3),
        )
        for field, value in mutations:
            changed = copy.deepcopy(original)
            changed[field] = value
            self.assertNotEqual(digest(original), digest(changed))
            with self.assertRaises(ValueError):
                validate_training_spec(changed)
        for field, value in (("seed", 2), ("algorithm", "other")):
            changed = copy.deepcopy(original)
            changed["initializer"][field] = value
            self.assertNotEqual(digest(original), digest(changed))
            with self.assertRaises(ValueError):
                validate_training_spec(changed)

    def test_training_request_binds_exact_parent_inputs_and_policies(self):
        parent = s1()
        request = bind_training_request(parent, job(), "code", "workflow")
        self.assertEqual(request["parentStateCommitment"], parent.commitment.value)
        self.assertEqual([i["artifactRef"]["id"] for i in request["inputs"]], list(INPUT_IDS))
        self.assertEqual(request["requestedRevealsHash"], digest([]))
        changed = copy.deepcopy(request)
        changed["parentStateCommitment"] = "0" * 64
        with self.assertRaises(ValueError):
            validate_training_request(parent, changed, job(), "code", "workflow")

    def test_feature_or_label_input_change_affects_state_and_transition_commitment(self):
        parent = s1()
        original = s3(parent)
        changed_parent = s1(salt="changed")
        changed = s3(changed_parent)
        self.assertNotEqual(original.commitment.value, changed.commitment.value)
        self.assertNotEqual(original.transition.bindings_json, changed.transition.bindings_json)

    def test_training_operator_and_positive_cohort_fail_closed(self):
        with self.assertRaises(PermissionError):
            bind_training_request(s1(policy=m4_policy(("private_analytics",))), job(), "code", "workflow")
        with self.assertRaisesRegex(ValueError, "EMPTY_COHORT"):
            bind_training_request(s1(cardinality=0), job(), "code", "workflow")

    def test_context_and_key_epoch_fail_closed(self):
        value = job()
        value["keyEpoch"] = "rotated"
        with self.assertRaises(ValueError):
            validate_job(value)
        parent = s1()
        wrong = replace(parent, crypto_context=replace(parent.crypto_context, protocol="SEMI2K"))
        with self.assertRaises(ValueError):
            bind_training_request(wrong, job(), "code", "workflow")

    def test_model_policy_is_narrow_and_does_not_broaden_consent(self):
        policy = derive_model_policy(s1())
        self.assertEqual(policy.allowed_operators, (EVALUATION_OPERATOR,))
        self.assertEqual(policy.allowed_input_artifact_ids, MODEL_IDS)
        self.assertFalse(any(r.name in MODEL_IDS for r in policy.authorized_reveals))
        without = derive_model_policy(s1(policy=m4_policy(reveal=False)))
        self.assertFalse(without.authorizes(EVALUATION_REVEAL, PARTIES))

    def test_s3_exact_artifacts_and_immutable_round_trip(self):
        parent = s1()
        child = s3(parent)
        validate_training_child(child, parent, job(), "code", "workflow")
        self.assertEqual(tuple(a.id for a in child.artifacts), MODEL_IDS)
        self.assertEqual(tuple(a.shape for a in child.artifacts), MODEL_SHAPES)
        self.assertTrue(all(a.visibility == "secret-shared" and a.dtype == "float32" for a in child.artifacts))

    def test_evaluation_binds_exact_two_parent_lineage_and_all_inputs(self):
        data = s1()
        model = s3(data)
        request = bind_evaluation_request(model, data, job(), "code", "workflow")
        self.assertEqual([p["stateId"] for p in request["parents"]], ["S3_model", "S1"])
        self.assertEqual([i["artifactRef"]["id"] for i in request["modelInputs"]], list(MODEL_IDS))
        self.assertEqual([i["artifactRef"]["id"] for i in request["dataInputs"]], list(INPUT_IDS))
        child = s4(model, data, request)
        validate_evaluation_child(child, model, data, job(), "code", "workflow")
        self.assertEqual(child.parent_state_ids, ("S3_model", "S1"))
        self.assertEqual(tuple(a.id for a in child.artifacts), (EVALUATION_ID,))

    def test_evaluation_operator_authorization_fails_closed(self):
        data = s1(policy=m4_policy(("private_analytics", TRAINING_OPERATOR)))
        model = s3(data)
        with self.assertRaises(PermissionError):
            bind_evaluation_request(model, data, job(), "code", "workflow")

    def test_parent_or_model_change_affects_evaluation_commitments(self):
        data = s1()
        model = s3(data)
        original = s4(model, data)
        changed_model = s3(data, salt="changed")
        changed = s4(changed_model, data)
        self.assertNotEqual(original.commitment.value, changed.commitment.value)
        self.assertNotEqual(original.transition.bindings_json, changed.transition.bindings_json)

    def test_reveal_denies_weight_and_unknown_metric_before_load(self):
        state = s4()
        requested = [EVALUATION_REVEAL]
        mapping = {EVALUATION_REVEAL: EVALUATION_ID}
        calls = []
        service = RevealService(state.policy, {}, lambda value: calls.append(value), None)
        for name in (MODEL_IDS[0], "model.evaluation.rmse"):
            with self.assertRaises(PermissionError):
                service.named_scalar(requested, name, mapping, lambda value: calls.append(value))
        self.assertEqual(calls, [])

    def test_authorized_mse_uses_single_existing_reveal_boundary(self):
        state = s4()
        calls = []
        class Secret:
            def to(self, party):
                calls.append(party)
                return 0.012
        service = RevealService(state.policy, {p: p for p in PARTIES}, lambda value: value, float)
        value = service.named_scalar([EVALUATION_REVEAL], EVALUATION_REVEAL,
                                     {EVALUATION_REVEAL: EVALUATION_ID}, lambda _: Secret())
        self.assertAlmostEqual(value, 0.012)
        self.assertEqual(calls, list(PARTIES))

    def test_real_jax_gradient_changes_all_model_state(self):
        try:
            import jax.numpy as jnp
            from nn_kernel import training_kernel_for
        except (ImportError, RuntimeError) as error:
            self.skipTest(f"JAX unavailable in local interpreter: {error}")
        spec = job()["trainingSpec"]
        initial = initializer_metadata(spec)["tensors"]
        values = tuple(t["values"] for t in initial)
        mask = jnp.eye(2, dtype=jnp.int32)
        left = jnp.asarray([[[-8], [0]], [[0], [8]]], dtype=jnp.int32)
        right = jnp.asarray([[[252], [0]], [[0], [438]]], dtype=jnp.int32)
        trained = training_kernel_for(spec, values)(mask, left, right)
        self.assertTrue(any(float(jnp.max(jnp.abs(a - b))) > 0
                            for a, b in zip(trained, (
                                jnp.asarray(values[0]).reshape(1, 2), jnp.asarray(values[1]),
                                jnp.asarray(values[2]).reshape(2, 1), jnp.asarray(values[3]),
                            ), strict=True)))


if __name__ == "__main__":
    unittest.main()
