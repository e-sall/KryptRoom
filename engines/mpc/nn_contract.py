"""Canonical M4 contracts over the existing RoomState architecture."""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

from analytics_contract import (
    EXPECTED_CONTEXT, INPUT_IDS, KEY_EPOCH, PARTIES, artifact_commitment,
    digest, exact_keys, safe_id, validate_artifact, validate_context,
    validate_policy,
)
from room_state import (
    ArtifactRef, AuthorizedReveal, RoomState, StatePolicy, StateTransition,
    canonical_json, sha256_hex,
)

MODEL_IDS = (
    "model-nn-layer1-weight",
    "model-nn-layer1-bias",
    "model-nn-output-weight",
    "model-nn-output-bias",
)
MODEL_SHAPES = ((1, 2), (2,), (2, 1), (1,))
MODEL_TENSORS = (("W1", (1, 2)), ("b1", (2,)), ("W2", (2, 1)), ("b2", (1,)))
EVALUATION_ID = "model-evaluation-mse"
EVALUATION_REVEAL = "model.evaluation.mse"
TRAINING_OPERATOR = "private_nn_training"
EVALUATION_OPERATOR = "private_model_evaluation"
CODE_FILES = (
    "nn_contract.py", "nn_kernel.py", "private_nn.py", "analytics_reveal.py",
    "analytics_contract.py", "private_analytics.py", "room_state.py",
    "persistent_room_state.py", "private_join.py",
)


def source_hash(directory: Path) -> str:
    return digest({name: sha256_hex((directory / name).read_text(encoding="utf-8").encode())
                   for name in CODE_FILES})


def workflow_hash(path: Path) -> str:
    return sha256_hex(path.read_text(encoding="utf-8").encode())


def validate_model_spec(spec):
    exact_keys(spec, ("type", "inputDim", "layers", "outputInterpretation"))
    if (spec["type"] != "feedforward_neural_network" or spec["inputDim"] != 1
            or spec["outputInterpretation"] != "normalized_continuous_treatment_response"):
        raise ValueError("Unsupported M4 model specification")
    layers = spec["layers"]
    if not isinstance(layers, list) or len(layers) != 3:
        raise ValueError("M4 requires exactly Dense-square-Dense")
    exact_keys(layers[0], ("type", "inputDim", "outputDim"))
    exact_keys(layers[1], ("type",))
    exact_keys(layers[2], ("type", "inputDim", "outputDim"))
    if (layers[0] != {"type": "dense", "inputDim": 1, "outputDim": 2}
            or layers[1] != {"type": "square"}
            or layers[2] != {"type": "dense", "inputDim": 2, "outputDim": 1}):
        raise ValueError("Unsupported M4 model architecture or activation")


def _selector(value, artifact):
    exact_keys(value, ("artifact", "column", "divideBy"))
    if value["artifact"] != artifact or value["column"] != 0:
        raise ValueError("M4 requires the exact non-identifier feature and label selectors")
    expected = 10 if artifact == "lab-a-features" else 1000
    if type(value["divideBy"]) is not int or value["divideBy"] != expected:
        raise ValueError("M4 normalization divisor is not approved")


def validate_training_spec(spec):
    exact_keys(spec, ("loss", "optimizer", "learningRate", "steps", "shuffle",
                      "feature", "label", "initializer"))
    if (spec["loss"] != "masked_mse" or spec["optimizer"] != "full_batch_gradient_descent"
            or type(spec["learningRate"]) not in (int, float) or spec["learningRate"] != 0.4
            or type(spec["steps"]) is not int or spec["steps"] != 4
            or spec["shuffle"] is not False):
        raise ValueError("Unsupported M4 training configuration")
    _selector(spec["feature"], "lab-a-features")
    _selector(spec["label"], "lab-b-features")
    initializer = spec["initializer"]
    exact_keys(initializer, ("algorithm", "seed", "scale"))
    if (initializer["algorithm"] != "kryptroom-sha256-uniform-v1"
            or type(initializer["seed"]) is not int or initializer["seed"] != 1
            or type(initializer["scale"]) not in (int, float) or initializer["scale"] != 0.30):
        raise ValueError("Unsupported M4 deterministic initializer")


def validate_evaluation_spec(spec, training=None):
    exact_keys(spec, ("loss", "feature", "label"))
    if spec["loss"] != "masked_mse":
        raise ValueError("M4 evaluation requires masked MSE")
    _selector(spec["feature"], "lab-a-features")
    _selector(spec["label"], "lab-b-features")
    if training is not None and (spec["feature"] != training["feature"]
                                 or spec["label"] != training["label"]):
        raise ValueError("Training and evaluation normalization must match")


def initializer_metadata(training_spec):
    validate_training_spec(training_spec)
    initializer = training_spec["initializer"]
    tensors = []
    for tensor_name, shape in MODEL_TENSORS:
        values = []
        for index in range(math.prod(shape)):
            material = (b"kryptroom-m4-init-v1" + canonical_json(initializer["seed"])
                        + tensor_name.encode("utf-8") + canonical_json(index))
            unsigned = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
            unit = unsigned / 2**64
            values.append((2 * unit - 1) * initializer["scale"])
        tensors.append({"name": tensor_name, "shape": list(shape), "values": values})
    public = {"algorithm": initializer["algorithm"], "seed": initializer["seed"],
              "scale": initializer["scale"], "tensors": tensors}
    return {**public, "commitment": digest(public)}


def initializer_values(training_spec):
    return tuple(tensor["values"] for tensor in initializer_metadata(training_spec)["tensors"])


def _state_cardinality(state):
    value = json.loads(state.transition.bindings_json or "{}").get("cohortCardinality")
    if type(value) is not int:
        raise ValueError("Missing commitment-bound cohort cardinality")
    return value


def _validate_s1(state, operator):
    state.verify()
    validate_policy(state.policy)
    validate_context(state.crypto_context, KEY_EPOCH)
    if state.crypto_context.to_dict() != EXPECTED_CONTEXT:
        raise ValueError("M4 crypto context mismatch")
    if (operator not in state.policy.allowed_operators
            or tuple(state.policy.allowed_input_artifact_ids) != INPUT_IDS):
        raise PermissionError("S1 policy does not authorize the M4 operator and exact inputs")
    if tuple(a.id for a in state.artifacts) != INPUT_IDS:
        raise ValueError("M4 requires the exact S1 join artifacts")
    mask, feature, label = state.artifacts
    if len(mask.shape) != 2 or mask.shape[0] != mask.shape[1]:
        raise ValueError("Invalid fixed S1 join grid")
    if feature.shape != (*mask.shape, 1) or label.shape != (*mask.shape, 1):
        raise ValueError("Invalid fixed S1 feature/label grid")
    for artifact in state.artifacts:
        validate_artifact(artifact, state)
    cardinality = _state_cardinality(state)
    if not 0 <= cardinality <= mask.shape[0]:
        raise ValueError("Invalid commitment-bound cohort cardinality")
    if cardinality == 0:
        raise ValueError("EMPTY_COHORT: private NN requires a positive cohort")
    return cardinality


def _base_policy(reveals, operators=(), inputs=()):
    return StatePolicy(
        default_reveal="deny", plaintext_materialization="forbidden",
        matched_identifier_reveal="forbidden",
        future_identifier_disclosure_requires_opt_in=True,
        authorized_reveals=tuple(reveals), allowed_operators=tuple(operators),
        allowed_input_artifact_ids=tuple(inputs),
    )


def derive_model_policy(parent):
    _validate_s1(parent, TRAINING_OPERATOR)
    if not parent.policy.authorizes("ciphertext-metadata", PARTIES):
        raise PermissionError("S1 does not authorize ciphertext metadata")
    reveals = [AuthorizedReveal("ciphertext-metadata", PARTIES)]
    if parent.policy.authorizes(EVALUATION_REVEAL, PARTIES):
        reveals.append(AuthorizedReveal(EVALUATION_REVEAL, PARTIES))
    return _base_policy(reveals, (EVALUATION_OPERATOR,), MODEL_IDS)


def derive_evaluation_policy(model_state, data_state):
    if (not model_state.policy.authorizes("ciphertext-metadata", PARTIES)
            or not data_state.policy.authorizes("ciphertext-metadata", PARTIES)):
        raise PermissionError("Both parents must authorize ciphertext metadata")
    reveals = [AuthorizedReveal("ciphertext-metadata", PARTIES)]
    if (model_state.policy.authorizes(EVALUATION_REVEAL, PARTIES)
            and data_state.policy.authorizes(EVALUATION_REVEAL, PARTIES)):
        reveals.append(AuthorizedReveal(EVALUATION_REVEAL, PARTIES))
    return _base_policy(reveals)


def validate_job(job):
    exact_keys(job, ("version", "roomId", "cryptoContextId", "keyEpoch", "modelSpec",
                     "trainingSpec", "trainingTransition", "evaluationSpec",
                     "evaluationTransition"))
    if job["version"] != "1" or job["keyEpoch"] != KEY_EPOCH:
        raise ValueError("Unsupported M4 job version or key epoch")
    safe_id(job["roomId"])
    if job["cryptoContextId"] != EXPECTED_CONTEXT["id"]:
        raise ValueError("M4 job crypto context mismatch")
    validate_model_spec(job["modelSpec"])
    validate_training_spec(job["trainingSpec"])
    validate_evaluation_spec(job["evaluationSpec"], job["trainingSpec"])
    training = job["trainingTransition"]
    evaluation = job["evaluationTransition"]
    for value, operator, parents, output, reveals in (
        (training, TRAINING_OPERATOR, ["S1"], "S3_model", []),
        (evaluation, EVALUATION_OPERATOR, ["S3_model", "S1"], "S4_eval", [EVALUATION_REVEAL]),
    ):
        exact_keys(value, ("operator", "inputStateIds", "outputStateId", "transitionId",
                           "effectiveAt", "requestedReveals"))
        if (value["operator"] != operator or value["inputStateIds"] != parents
                or value["outputStateId"] != output or value["requestedReveals"] != reveals
                or not isinstance(value["effectiveAt"], str)):
            raise ValueError("Invalid fixed M4 transition specification")
        safe_id(value["outputStateId"])
        safe_id(value["transitionId"])


def bind_training_request(parent, job, code_hash, flow_hash):
    validate_job(job)
    if parent.room_id != job["roomId"] or parent.id != job["trainingTransition"]["inputStateIds"][0]:
        raise ValueError("Training parent identity mismatch")
    _validate_s1(parent, TRAINING_OPERATOR)
    output_policy = derive_model_policy(parent)
    transition = job["trainingTransition"]
    return {
        "version": "1", "operator": TRAINING_OPERATOR,
        "parentStateId": parent.id, "parentStateCommitment": parent.commitment.value,
        "inputs": [{"artifactRef": a.to_dict(),
                    "commitment": artifact_commitment(a, parent.crypto_context)} for a in parent.artifacts],
        "modelSpec": job["modelSpec"], "modelSpecHash": digest(job["modelSpec"]),
        "trainingSpec": job["trainingSpec"], "trainingSpecHash": digest(job["trainingSpec"]),
        "featureSelector": job["trainingSpec"]["feature"],
        "labelSelector": job["trainingSpec"]["label"],
        "featureNormalizationDivisor": job["trainingSpec"]["feature"]["divideBy"],
        "labelNormalizationDivisor": job["trainingSpec"]["label"]["divideBy"],
        "initializer": initializer_metadata(job["trainingSpec"]),
        "codeHash": code_hash, "workflowHash": flow_hash,
        "cryptoContextHash": digest(parent.crypto_context.to_dict()),
        "inputPolicyHash": digest(parent.policy.to_dict()),
        "outputPolicy": output_policy.to_dict(), "outputPolicyHash": digest(output_policy.to_dict()),
        "requestedRevealsHash": digest(transition["requestedReveals"]),
        "outputStateId": transition["outputStateId"], "transition": transition,
    }


def validate_training_request(parent, request, job, code_hash, flow_hash):
    expected = bind_training_request(parent, job, code_hash, flow_hash)
    if canonical_json(request) != canonical_json(expected):
        raise ValueError("Training request does not bind exact S1, model, training, code or policy")


@dataclass(frozen=True)
class PrivateNNTrainingTransition(StateTransition):
    """Existing transition record with canonical M4 training bindings."""


def make_training_transition(parent, request, outputs):
    spec = request["transition"]
    payload = {
        "operator": TRAINING_OPERATOR, "request": request,
        "outputStateId": spec["outputStateId"],
        "outputArtifactCommitments": [artifact_commitment(a, parent.crypto_context) for a in outputs],
    }
    bindings = {**payload, "transitionCommitment": digest(payload)}
    return PrivateNNTrainingTransition(
        id=spec["transitionId"], operation=TRAINING_OPERATOR,
        parent_state_ids=(parent.id,), input_job_id=spec["transitionId"],
        output_artifact_ids=tuple(a.id for a in outputs), effective_at=spec["effectiveAt"],
        bindings_json=canonical_json(bindings).decode(),
    )


def validate_training_child(child, parent, job, code_hash, flow_hash):
    child.verify()
    validate_context(child.crypto_context, KEY_EPOCH)
    request = json.loads(child.transition.bindings_json or "{}").get("request")
    if request is None:
        raise ValueError("S3 lacks committed training request")
    validate_training_request(parent, request, job, code_hash, flow_hash)
    if (child.id != request["outputStateId"] or child.room_id != parent.room_id
            or child.parent_state_ids != (parent.id,) or child.crypto_context != parent.crypto_context
            or child.policy != derive_model_policy(parent)):
        raise ValueError("Invalid S3 identity, lineage, context or model policy")
    if tuple(a.id for a in child.artifacts) != MODEL_IDS:
        raise ValueError("S3 must contain exactly four model artifacts")
    for artifact, shape in zip(child.artifacts, MODEL_SHAPES, strict=True):
        validate_artifact(artifact, child)
        if artifact.shape != shape or artifact.dtype != "float32":
            raise ValueError("Invalid model artifact shape or dtype")
    if child.transition.to_dict() != make_training_transition(parent, request, child.artifacts).to_dict():
        raise ValueError("Invalid private NN training transition commitment")
    return request


def bind_evaluation_request(model_state, data_state, job, code_hash, flow_hash):
    validate_job(job)
    validate_training_child(model_state, data_state, job, code_hash, flow_hash)
    _validate_s1(data_state, EVALUATION_OPERATOR)
    if (model_state.policy.allowed_operators != (EVALUATION_OPERATOR,)
            or model_state.policy.allowed_input_artifact_ids != MODEL_IDS):
        raise PermissionError("S3 policy does not authorize exact model evaluation inputs")
    transition = job["evaluationTransition"]
    if transition["inputStateIds"] != [model_state.id, data_state.id]:
        raise ValueError("Evaluation requires exact ordered S3 and S1 parents")
    output_policy = derive_evaluation_policy(model_state, data_state)
    return {
        "version": "1", "operator": EVALUATION_OPERATOR,
        "parents": [
            {"stateId": model_state.id, "stateCommitment": model_state.commitment.value,
             "policyHash": digest(model_state.policy.to_dict())},
            {"stateId": data_state.id, "stateCommitment": data_state.commitment.value,
             "policyHash": digest(data_state.policy.to_dict())},
        ],
        "modelInputs": [{"artifactRef": a.to_dict(),
                         "commitment": artifact_commitment(a, model_state.crypto_context)}
                        for a in model_state.artifacts],
        "dataInputs": [{"artifactRef": a.to_dict(),
                        "commitment": artifact_commitment(a, data_state.crypto_context)}
                       for a in data_state.artifacts],
        "modelSpec": job["modelSpec"], "modelSpecHash": digest(job["modelSpec"]),
        "evaluationSpec": job["evaluationSpec"],
        "evaluationSpecHash": digest(job["evaluationSpec"]),
        "codeHash": code_hash, "workflowHash": flow_hash,
        "cryptoContextHash": digest(model_state.crypto_context.to_dict()),
        "inputPolicyHashes": [digest(model_state.policy.to_dict()), digest(data_state.policy.to_dict())],
        "outputPolicy": output_policy.to_dict(), "outputPolicyHash": digest(output_policy.to_dict()),
        "requestedRevealsHash": digest(transition["requestedReveals"]),
        "outputStateId": transition["outputStateId"], "transition": transition,
    }


def validate_evaluation_request(model_state, data_state, request, job, code_hash, flow_hash):
    expected = bind_evaluation_request(model_state, data_state, job, code_hash, flow_hash)
    if canonical_json(request) != canonical_json(expected):
        raise ValueError("Evaluation request does not bind exact parents, inputs, model, code or policies")


@dataclass(frozen=True)
class PrivateModelEvaluationTransition(StateTransition):
    """Existing transition record with canonical M4 multi-parent bindings."""


def make_evaluation_transition(model_state, data_state, request, output):
    spec = request["transition"]
    payload = {
        "operator": EVALUATION_OPERATOR, "request": request,
        "outputStateId": spec["outputStateId"],
        "outputArtifactCommitments": [artifact_commitment(output, model_state.crypto_context)],
    }
    bindings = {**payload, "transitionCommitment": digest(payload)}
    return PrivateModelEvaluationTransition(
        id=spec["transitionId"], operation=EVALUATION_OPERATOR,
        parent_state_ids=(model_state.id, data_state.id), input_job_id=spec["transitionId"],
        output_artifact_ids=(output.id,), effective_at=spec["effectiveAt"],
        bindings_json=canonical_json(bindings).decode(),
    )


def validate_evaluation_child(child, model_state, data_state, job, code_hash, flow_hash):
    child.verify()
    validate_context(child.crypto_context, KEY_EPOCH)
    request = json.loads(child.transition.bindings_json or "{}").get("request")
    if request is None:
        raise ValueError("S4 lacks committed evaluation request")
    validate_evaluation_request(model_state, data_state, request, job, code_hash, flow_hash)
    if (child.id != request["outputStateId"] or child.room_id != data_state.room_id
            or child.parent_state_ids != (model_state.id, data_state.id)
            or child.crypto_context != data_state.crypto_context
            or child.policy != derive_evaluation_policy(model_state, data_state)):
        raise ValueError("Invalid S4 identity, lineage, context or evaluation policy")
    if len(child.artifacts) != 1 or child.artifacts[0].id != EVALUATION_ID:
        raise ValueError("S4 must contain exactly the secret evaluation MSE")
    artifact = child.artifacts[0]
    validate_artifact(artifact, child)
    if artifact.shape != (1,) or artifact.dtype != "float32":
        raise ValueError("Evaluation output must be a float32 logical scalar")
    if child.transition.to_dict() != make_evaluation_transition(
            model_state, data_state, request, artifact).to_dict():
        raise ValueError("Invalid private model evaluation transition commitment")
    return request
