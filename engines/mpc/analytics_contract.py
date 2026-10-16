"""Deterministic M3 validation and bindings using the existing RoomState contracts."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from room_state import (
    ArtifactRef, CryptoContext, RoomState, StateTransition,
    canonical_json, sha256_hex,
)

PARTIES = ("lab-a", "lab-b")
INPUT_IDS = ("match-mask", "lab-a-features", "lab-b-features")
OPERATIONS = ("COUNT", "SUM", "MEAN", "CROSS_MEAN")
# Absolute error, for the bounded synthetic acceptance fixture; not a general range guarantee.
FIXED_POINT_TOLERANCE = 0.001
KEY_EPOCH = "room-state-v1"
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
EXPECTED_CONTEXT = {
    "id": "secretflow-spu-cheetah-fm128-v1", "backend": "SecretFlow SPU",
    "backendVersion": "1.14.0b0", "protocol": "CHEETAH", "field": "FM128",
    "securityModel": "semi-honest", "participants": list(PARTIES),
    "artifactCipher": "AES-256-GCM", "keyScope": "per-kryptnode-local",
}
CODE_FILES = ("analytics_contract.py", "analytics_kernel.py", "analytics_reveal.py",
              "private_analytics.py", "room_state.py", "persistent_room_state.py", "private_join.py")


def digest(value) -> str:
    return sha256_hex(canonical_json(value))


def safe_id(value):
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
        raise ValueError("Invalid public identifier")
    return value


def exact_keys(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError("Unexpected or missing analytics contract fields")


def artifact_commitment(artifact: ArtifactRef, context: CryptoContext) -> str:
    """Commit only public holder ciphertext descriptors, never the local shares."""
    return digest({"artifact": artifact.to_dict(), "cryptoContext": context.to_dict()})


def source_hash(directory: Path) -> str:
    return digest({name: sha256_hex((directory / name).read_text(encoding="utf-8").encode())
                   for name in CODE_FILES})


def workflow_hash(path: Path) -> str:
    return sha256_hex(path.read_text(encoding="utf-8").encode())


def validate_context(context, key_epoch):
    if context.to_dict() != EXPECTED_CONTEXT or key_epoch != KEY_EPOCH:
        raise ValueError("Incompatible crypto context or key epoch")


def validate_policy(policy):
    if (policy.default_reveal != "deny" or policy.plaintext_materialization != "forbidden"
            or policy.matched_identifier_reveal != "forbidden"
            or not policy.future_identifier_disclosure_requires_opt_in):
        raise PermissionError("Analytics requires the default-deny state policy")


def metric_reveal(metric):
    return f"analytics.{metric['op'].lower()}.{metric['id']}"


def output_id(metric):
    return f"analytics-{metric['op'].lower().replace('_', '-')}-{metric['id']}"


def validate_spec(spec, parent: RoomState):
    exact_keys(spec, ("version", "operator", "roomId", "inputStateIds", "outputStateId",
                      "transitionId", "effectiveAt", "cryptoContextId", "keyEpoch",
                      "metrics", "requestedReveals"))
    parent.verify()
    validate_policy(parent.policy)
    validate_context(parent.crypto_context, spec["keyEpoch"])
    if spec["version"] != "1" or spec["operator"] != "private_analytics":
        raise ValueError("Unsupported analytics operation")
    if (spec["roomId"] != parent.room_id or spec["inputStateIds"] != [parent.id]
            or spec["cryptoContextId"] != parent.crypto_context.id):
        raise ValueError("Analytics parent identity or context mismatch")
    safe_id(spec["outputStateId"])
    safe_id(spec["transitionId"])
    if spec["outputStateId"] == parent.id or not isinstance(spec["effectiveAt"], str):
        raise ValueError("Analytics must produce a new state")
    if ("private_analytics" not in parent.policy.allowed_operators
            or tuple(parent.policy.allowed_input_artifact_ids) != INPUT_IDS):
        raise PermissionError("State policy does not authorize private_analytics inputs")
    if tuple(a.id for a in parent.artifacts) != INPUT_IDS:
        raise ValueError("Expected the three persisted private-join artifacts")
    mask, left, right = parent.artifacts
    if len(mask.shape) != 2 or mask.shape[0] != mask.shape[1]:
        raise ValueError("Invalid fixed join grid")
    if any(a.shape != (*mask.shape, 1) for a in (left, right)):
        raise ValueError("Invalid feature grid")
    for artifact in parent.artifacts:
        validate_artifact(artifact, parent)
    metrics = spec["metrics"]
    if not isinstance(metrics, list) or not 1 <= len(metrics) <= 16:
        raise ValueError("Analytics requires a bounded metric list")
    ids = set()
    for metric in metrics:
        if not isinstance(metric, dict) or metric.get("op") not in OPERATIONS:
            raise ValueError("Unsupported analytics metric")
        safe_id(metric.get("id"))
        safe_id(output_id(metric))
        if metric["id"] in ids:
            raise ValueError("Duplicate metric identifier")
        ids.add(metric["id"])
        if metric["op"] == "COUNT":
            exact_keys(metric, ("id", "op"))
        elif metric["op"] in ("SUM", "MEAN"):
            exact_keys(metric, ("id", "op", "input"))
            validate_selector(metric["input"], parent)
        else:
            exact_keys(metric, ("id", "op", "left", "right"))
            validate_selector(metric["left"], parent, "lab-a-features")
            validate_selector(metric["right"], parent, "lab-b-features")
    requested = spec["requestedReveals"]
    if not isinstance(requested, list) or len(set(requested)) != len(requested):
        raise ValueError("Invalid requested reveals")
    names = {metric_reveal(m) for m in metrics}
    for name in requested:
        if name not in names or not parent.policy.authorizes(name, PARTIES):
            raise PermissionError("State policy does not authorize requested analytics reveal")
    cardinality = json.loads(parent.transition.bindings_json or "{}").get("cohortCardinality")
    if type(cardinality) is not int or not 0 <= cardinality <= mask.shape[0]:
        raise ValueError("Missing or invalid previously authorized cohort cardinality")
    if cardinality == 0 and any(m["op"] in ("MEAN", "CROSS_MEAN") for m in metrics):
        raise ValueError("EMPTY_COHORT: mean operations require positive parent cardinality")
    return cardinality


def validate_artifact(artifact, state):
    if (artifact.visibility != "secret-shared" or artifact.includes_identifiers
            or artifact.kind != "spu-secret-share" or artifact.dtype not in ("int32", "float32")
            or artifact.media_type != "application/vnd.kryptroom.spu-share+encrypted"
            or artifact.crypto_context_id != state.crypto_context.id
            or tuple(c.party for c in artifact.ciphertexts) != PARTIES):
        raise ValueError("Invalid secret artifact context or holders")
    for c in artifact.ciphertexts:
        expected = f"local://{c.party}/rooms/{state.room_id}/states/{state.id}/artifacts/{artifact.id}.share.enc"
        if c.uri != expected or not re.fullmatch(r"[a-f0-9]{64}", c.sha256) or c.size_bytes <= 0:
            raise ValueError("Invalid holder ciphertext descriptor")


def validate_selector(selector, parent, required_artifact=None):
    exact_keys(selector, ("artifact", "column"))
    if selector["artifact"] not in INPUT_IDS[1:]:
        raise ValueError("Only explicit feature selectors are accepted")
    if required_artifact and selector["artifact"] != required_artifact:
        raise ValueError("CROSS_MEAN requires Lab A and Lab B features")
    artifact = next(a for a in parent.artifacts if a.id == selector["artifact"])
    if type(selector["column"]) is not int or not 0 <= selector["column"] < artifact.shape[-1]:
        raise ValueError("Feature column outside public shape")


def bind_request(parent, spec, code_hash, flow_hash):
    validate_spec(spec, parent)
    return {
        "spec": spec, "parentStateCommitment": parent.commitment.value,
        "inputs": [{"artifactRef": a.to_dict(), "commitment": artifact_commitment(a, parent.crypto_context)}
                   for a in parent.artifacts],
        "codeHash": code_hash, "workflowHash": flow_hash,
        "cryptoContextHash": digest(parent.crypto_context.to_dict()),
        "policyHash": digest(parent.policy.to_dict()),
        "analyticsSpecHash": digest(spec), "requestedRevealsHash": digest(spec["requestedReveals"]),
    }


def validate_request(parent, request, code_hash, flow_hash):
    expected = bind_request(parent, request["spec"], code_hash, flow_hash)
    if canonical_json(request) != canonical_json(expected):
        raise ValueError("Analytics request does not bind exact parent, artifacts, code or policy")


@dataclass(frozen=True)
class PrivateAnalyticsTransition(StateTransition):
    """Existing transition record with canonical M3 bindings, not a second state model."""


def make_transition(parent, request, outputs):
    spec = request["spec"]
    payload = {
        "operator": "private_analytics", "request": request,
        "outputStateId": spec["outputStateId"],
        "outputArtifactCommitments": [artifact_commitment(a, parent.crypto_context) for a in outputs],
    }
    bindings = {**payload, "transitionCommitment": digest(payload)}
    return PrivateAnalyticsTransition(
        id=spec["transitionId"], operation="private_analytics", parent_state_ids=(parent.id,),
        input_job_id=spec["transitionId"], output_artifact_ids=tuple(a.id for a in outputs),
        effective_at=spec["effectiveAt"], bindings_json=canonical_json(bindings).decode(),
    )


def validate_child(child, parent, code_hash, flow_hash):
    child.verify()
    validate_context(child.crypto_context, KEY_EPOCH)
    if child.crypto_context != parent.crypto_context or child.policy != parent.policy:
        raise ValueError("Child policy or crypto context changed")
    bindings = json.loads(child.transition.bindings_json or "{}")
    request = bindings["request"]
    validate_request(parent, request, code_hash, flow_hash)
    spec = request["spec"]
    if child.parent_state_ids != (parent.id,) or child.id != spec["outputStateId"] or child.room_id != parent.room_id:
        raise ValueError("Child identity or parent mismatch")
    if tuple(a.id for a in child.artifacts) != tuple(output_id(m) for m in spec["metrics"]):
        raise ValueError("Child output artifacts mismatch")
    for artifact, metric in zip(child.artifacts, spec["metrics"], strict=True):
        validate_artifact(artifact, child)
        expected_dtype = "int32" if metric["op"] == "COUNT" else "float32"
        if artifact.shape != (1,) or artifact.dtype != expected_dtype:
            raise ValueError("Analytics outputs must be logical scalar artifacts")
    expected = make_transition(parent, request, child.artifacts)
    if child.transition.to_dict() != expected.to_dict():
        raise ValueError("Invalid analytics transition commitment")
    return spec
