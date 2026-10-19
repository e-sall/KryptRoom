"""M6 policy, persistence, artifact resolution, and commitment bindings."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

MPC_DIR = Path(__file__).resolve().parents[1] / "mpc"
if str(MPC_DIR) not in sys.path:
    sys.path.insert(0, str(MPC_DIR))

from room_state import (  # noqa: E402
    ArtifactRef,
    AuthorizedReveal,
    CiphertextRef,
    CryptoContext,
    PublicMaterialRef,
    RoomState,
    StatePolicy,
    StateTransition,
    canonical_json,
    create_room_state,
    sha256_hex,
)

ROOM_ID = "cancer-collaboration-room"
INPUT_STATE_ID = "S5_fhe_inputs"
OUTPUT_STATE_ID = "S6_fhe_sum"
INPUT_ARTIFACT_IDS = ("fhe-vector-lab-a", "fhe-vector-lab-b")
OUTPUT_ARTIFACT_ID = "fhe-vector-sum"
PARTIES = ("lab-a", "lab-b")
EVALUATOR = "fhe-evaluator"
KEY_OWNER = "lab-a"
KEY_EPOCH = "fhe-key-epoch-1"
CONTEXT_ID = "openfhe-bgv-rns-1.5.1-v1"
REVEAL_NAME = "fhe.vector-sum"
VECTOR_LENGTH = 4
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
HEX_SHA256 = re.compile(r"^[a-f0-9]{64}$")
CODE_FILES = (
    "fhe_contract.py",
    "fhe_encrypt.py",
    "fhe_kernel.py",
    "fhe_reveal.py",
    "fhe_setup.py",
    "fhe_transition.py",
    "openfhe_backend.py",
)


def digest(value) -> str:
    return sha256_hex(canonical_json(value))


def exact_keys(value, keys) -> None:
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError("Unexpected or missing FHE contract fields")


def safe_id(value) -> str:
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
        raise ValueError("Invalid public identifier")
    return value


def source_hash(directory: Path) -> str:
    return digest(
        {
            name: sha256_hex((directory / name).read_bytes())
            for name in CODE_FILES
        }
    )


def workflow_hash(path: Path) -> str:
    return sha256_hex(path.read_bytes())


def artifact_commitment(artifact: ArtifactRef, context: CryptoContext) -> str:
    return digest({"artifact": artifact.to_dict(), "cryptoContext": context.to_dict()})


def _material_uri(file_name: str) -> str:
    return f"local://{EVALUATOR}/crypto/{file_name}"


def context_from_report(report: dict) -> CryptoContext:
    exact_keys(
        report,
        (
            "backend",
            "backendVersion",
            "scheme",
            "keyEpoch",
            "keyOwner",
            "parameters",
            "publicMaterials",
            "evaluationMaterials",
        ),
    )
    materials = report["publicMaterials"]
    if not isinstance(materials, list) or len(materials) != 2:
        raise ValueError("M6 requires exactly the crypto context and public key")
    if report["evaluationMaterials"] != []:
        raise ValueError("M6 EvalAdd must not introduce unnecessary evaluation keys")
    for item in materials:
        exact_keys(item, ("id", "kind", "fileName", "sha256", "sizeBytes"))
    references = tuple(
        PublicMaterialRef(
            id=safe_id(item["id"]),
            kind=item["kind"],
            uri=_material_uri(item["fileName"]),
            sha256=item["sha256"],
            size_bytes=item["sizeBytes"],
        )
        for item in materials
    )
    context = CryptoContext(
        id=CONTEXT_ID,
        backend=report["backend"],
        backend_version=report["backendVersion"],
        protocol=report["scheme"],
        field="Z_65537",
        security_model=report["parameters"]["securityLevel"],
        participants=PARTIES,
        artifact_cipher="OpenFHE-BGV-ciphertext",
        key_scope="single-owner-node-local",
        key_epoch=report["keyEpoch"],
        key_owner=report["keyOwner"],
        parameters_json=canonical_json(report["parameters"]).decode("utf-8"),
        public_material_refs=references,
        evaluation_material_refs=(),
    )
    validate_context(context)
    return context


def validate_context(context: CryptoContext) -> None:
    if (
        context.id != CONTEXT_ID
        or context.backend != "OpenFHE"
        or context.backend_version != "1.5.1.0.24.4"
        or context.protocol != "BGV-RNS"
        or context.field != "Z_65537"
        or context.security_model != "HEStd_128_classic"
        or context.participants != PARTIES
        or context.artifact_cipher != "OpenFHE-BGV-ciphertext"
        or context.key_scope != "single-owner-node-local"
        or context.key_epoch != KEY_EPOCH
        or context.key_owner != KEY_OWNER
        or context.evaluation_material_refs
    ):
        raise ValueError("Incompatible M6 OpenFHE crypto context or key epoch")
    parameters = json.loads(context.parameters_json or "null")
    exact_keys(
        parameters,
        (
            "plaintextModulus",
            "multiplicativeDepth",
            "batchSize",
            "securityLevel",
            "ringDimension",
            "serialization",
            "operationSet",
        ),
    )
    ring_dimension = parameters["ringDimension"]
    if (
        parameters["plaintextModulus"] != 65537
        or parameters["multiplicativeDepth"] != 0
        or parameters["batchSize"] != VECTOR_LENGTH
        or parameters["securityLevel"] != "HEStd_128_classic"
        or type(ring_dimension) is not int
        or ring_dimension < 1024
        or ring_dimension & (ring_dimension - 1)
        or parameters["serialization"] != "BINARY"
        or parameters["operationSet"] != ["EvalAdd"]
    ):
        raise ValueError("Unsupported M6 BGV parameters")
    expected = (
        ("openfhe-bgv-context", "crypto-context", "openfhe-bgv-context.bin"),
        ("openfhe-bgv-public-key", "public-key", "openfhe-bgv-public-key.bin"),
    )
    if len(context.public_material_refs) != len(expected):
        raise ValueError("Incomplete OpenFHE public material references")
    for reference, (identifier, kind, file_name) in zip(
        context.public_material_refs, expected, strict=True
    ):
        if (
            reference.id != identifier
            or reference.kind != kind
            or reference.uri != _material_uri(file_name)
            or not HEX_SHA256.fullmatch(reference.sha256)
            or reference.size_bytes <= 0
        ):
            raise ValueError("Invalid OpenFHE public material reference")


def default_policy() -> StatePolicy:
    return StatePolicy(
        default_reveal="deny",
        plaintext_materialization="forbidden",
        matched_identifier_reveal="forbidden",
        future_identifier_disclosure_requires_opt_in=True,
        authorized_reveals=(AuthorizedReveal(REVEAL_NAME, PARTIES),),
        allowed_operators=("fhe_vector_add",),
        allowed_input_artifact_ids=INPUT_ARTIFACT_IDS,
    )


def validate_policy(policy: StatePolicy) -> None:
    if policy != default_policy():
        raise PermissionError("M6 requires the exact default-deny state policy")


def artifact_uri(holder: str, state_id: str, artifact_id: str) -> str:
    return (
        f"local://{holder}/rooms/{ROOM_ID}/states/{state_id}/artifacts/"
        f"{artifact_id}.openfhe.bin"
    )


def artifact_from_file(
    *, artifact_id: str, holder: str, state_id: str, path: Path, context: CryptoContext
) -> ArtifactRef:
    payload = path.read_bytes()
    return ArtifactRef(
        id=artifact_id,
        kind="openfhe-ciphertext",
        media_type="application/vnd.kryptroom.openfhe-ciphertext",
        visibility="encrypted",
        crypto_context_id=context.id,
        shape=(VECTOR_LENGTH,),
        dtype="int64",
        includes_identifiers=False,
        ciphertexts=(
            CiphertextRef(
                party=holder,
                uri=artifact_uri(holder, state_id, artifact_id),
                sha256=sha256_hex(payload),
                size_bytes=len(payload),
            ),
        ),
        protection="fhe_ciphertext",
    )


def validate_artifact(
    artifact: ArtifactRef, *, state_id: str, holder: str, context: CryptoContext
) -> None:
    if (
        artifact.kind != "openfhe-ciphertext"
        or artifact.media_type != "application/vnd.kryptroom.openfhe-ciphertext"
        or artifact.visibility != "encrypted"
        or artifact.protection != "fhe_ciphertext"
        or artifact.crypto_context_id != context.id
        or artifact.shape != (VECTOR_LENGTH,)
        or artifact.dtype != "int64"
        or artifact.includes_identifiers
        or len(artifact.ciphertexts) != 1
    ):
        raise ValueError("Invalid M6 FHE artifact")
    reference = artifact.ciphertexts[0]
    if (
        reference.party != holder
        or reference.uri != artifact_uri(holder, state_id, artifact.id)
        or not HEX_SHA256.fullmatch(reference.sha256)
        or reference.size_bytes <= 0
    ):
        raise ValueError("Invalid M6 ciphertext holder descriptor")


def resolve_uri(uri: str, roots: dict[str, Path]) -> Path:
    parsed = urlparse(uri)
    if parsed.scheme != "local" or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError("Only explicit local artifact references are supported")
    if parsed.netloc not in roots:
        raise PermissionError("Artifact holder root is not available to this operation")
    relative = PurePosixPath(parsed.path.lstrip("/"))
    if not relative.parts or any(part in ("", ".", "..") for part in relative.parts):
        raise ValueError("Unsafe local artifact reference")
    root = roots[parsed.netloc].resolve()
    path = root.joinpath(*relative.parts).resolve()
    if root not in path.parents:
        raise ValueError("Artifact reference escapes its holder root")
    return path


def verify_file_reference(reference, roots: dict[str, Path]) -> Path:
    path = resolve_uri(reference.uri, roots)
    payload = path.read_bytes()
    if len(payload) != reference.size_bytes or sha256_hex(payload) != reference.sha256:
        raise ValueError("Persisted FHE artifact commitment verification failed")
    return path


def verify_public_materials(context: CryptoContext, roots: dict[str, Path]) -> dict[str, Path]:
    validate_context(context)
    return {
        reference.id: verify_file_reference(reference, roots)
        for reference in context.public_material_refs
    }


def verify_artifact_file(
    artifact: ArtifactRef,
    *,
    state_id: str,
    holder: str,
    context: CryptoContext,
    roots: dict[str, Path],
) -> Path:
    validate_artifact(artifact, state_id=state_id, holder=holder, context=context)
    return verify_file_reference(artifact.ciphertexts[0], roots)


def make_initial_transition(
    context: CryptoContext,
    artifacts: tuple[ArtifactRef, ...],
    policy: StatePolicy,
) -> StateTransition:
    request = {
        "cryptoContextHash": digest(context.to_dict()),
        "inputOwners": list(PARTIES),
        "outputStateId": INPUT_STATE_ID,
        "policyHash": digest(policy.to_dict()),
        "plaintextPersisted": False,
    }
    payload = {
        "operator": "fhe_vector_encrypt",
        "request": request,
        "outputStateId": INPUT_STATE_ID,
        "outputArtifactCommitments": [
            artifact_commitment(artifact, context) for artifact in artifacts
        ],
    }
    bindings = {**payload, "transitionCommitment": digest(payload)}
    return StateTransition(
        id="m6-fhe-input-encryption",
        operation="fhe_vector_encrypt",
        parent_state_ids=(),
        input_job_id="m6-fhe-input-encryption",
        output_artifact_ids=INPUT_ARTIFACT_IDS,
        effective_at="2026-10-18T00:00:00Z",
        bindings_json=canonical_json(bindings).decode("utf-8"),
    )


def create_initial_state(context: CryptoContext, artifacts: tuple[ArtifactRef, ...]) -> RoomState:
    validate_context(context)
    if tuple(artifact.id for artifact in artifacts) != INPUT_ARTIFACT_IDS:
        raise ValueError("Initial FHE state must contain both participant ciphertexts")
    for artifact, holder in zip(artifacts, PARTIES, strict=True):
        validate_artifact(artifact, state_id=INPUT_STATE_ID, holder=holder, context=context)
    policy = default_policy()
    return create_room_state(
        state_id=INPUT_STATE_ID,
        room_id=ROOM_ID,
        parent_state_ids=(),
        artifacts=artifacts,
        transition=make_initial_transition(context, artifacts, policy),
        policy=policy,
        crypto_context=context,
    )


def validate_parent(parent: RoomState) -> None:
    parent.verify()
    validate_context(parent.crypto_context)
    validate_policy(parent.policy)
    if (
        parent.id != INPUT_STATE_ID
        or parent.room_id != ROOM_ID
        or parent.parent_state_ids
        or tuple(artifact.id for artifact in parent.artifacts) != INPUT_ARTIFACT_IDS
    ):
        raise ValueError("Unexpected M6 input state")
    for artifact, holder in zip(parent.artifacts, PARTIES, strict=True):
        validate_artifact(
            artifact, state_id=parent.id, holder=holder, context=parent.crypto_context
        )
    expected_transition = make_initial_transition(
        parent.crypto_context, parent.artifacts, parent.policy
    )
    if parent.transition.to_dict() != expected_transition.to_dict():
        raise ValueError("Invalid initial FHE encryption transition commitment")


def validate_spec(spec: dict, parent: RoomState) -> None:
    exact_keys(
        spec,
        (
            "version",
            "operator",
            "roomId",
            "inputStateIds",
            "outputStateId",
            "transitionId",
            "effectiveAt",
            "cryptoContextId",
            "keyEpoch",
            "inputArtifactIds",
            "outputArtifactId",
            "requestedReveals",
        ),
    )
    validate_parent(parent)
    if (
        spec["version"] != "1"
        or spec["operator"] != "fhe_vector_add"
        or spec["roomId"] != parent.room_id
        or spec["inputStateIds"] != [parent.id]
        or spec["outputStateId"] != OUTPUT_STATE_ID
        or spec["transitionId"] != "m6-fhe-vector-add"
        or not isinstance(spec["effectiveAt"], str)
        or spec["cryptoContextId"] != parent.crypto_context.id
        or spec["keyEpoch"] != parent.crypto_context.key_epoch
        or spec["inputArtifactIds"] != list(INPUT_ARTIFACT_IDS)
        or spec["outputArtifactId"] != OUTPUT_ARTIFACT_ID
        or spec["requestedReveals"] != []
    ):
        raise ValueError("Unsupported or mismatched M6 FHE transition")
    if spec["operator"] not in parent.policy.allowed_operators:
        raise PermissionError("State policy does not authorize FHE vector addition")


def bind_request(parent: RoomState, spec: dict, code_hash: str, flow_hash: str) -> dict:
    validate_spec(spec, parent)
    return {
        "spec": spec,
        "parentStateCommitment": parent.commitment.value,
        "inputs": [
            {
                "artifactRef": artifact.to_dict(),
                "commitment": artifact_commitment(artifact, parent.crypto_context),
            }
            for artifact in parent.artifacts
        ],
        "codeHash": code_hash,
        "workflowHash": flow_hash,
        "cryptoContextHash": digest(parent.crypto_context.to_dict()),
        "policyHash": digest(parent.policy.to_dict()),
        "requestedRevealsHash": digest(spec["requestedReveals"]),
    }


def make_transition(
    parent: RoomState, request: dict, output: ArtifactRef
) -> StateTransition:
    spec = request["spec"]
    payload = {
        "operator": "fhe_vector_add",
        "request": request,
        "outputStateId": spec["outputStateId"],
        "outputArtifactCommitments": [
            artifact_commitment(output, parent.crypto_context)
        ],
    }
    bindings = {**payload, "transitionCommitment": digest(payload)}
    return StateTransition(
        id=spec["transitionId"],
        operation="fhe_vector_add",
        parent_state_ids=(parent.id,),
        input_job_id=spec["transitionId"],
        output_artifact_ids=(output.id,),
        effective_at=spec["effectiveAt"],
        bindings_json=canonical_json(bindings).decode("utf-8"),
    )


def create_child_state(
    parent: RoomState,
    spec: dict,
    output: ArtifactRef,
    code_hash: str,
    flow_hash: str,
) -> RoomState:
    request = bind_request(parent, spec, code_hash, flow_hash)
    child = create_room_state(
        state_id=spec["outputStateId"],
        room_id=parent.room_id,
        parent_state_ids=(parent.id,),
        artifacts=(output,),
        transition=make_transition(parent, request, output),
        policy=parent.policy,
        crypto_context=parent.crypto_context,
    )
    validate_child(child, parent, code_hash, flow_hash)
    return child


def validate_child(
    child: RoomState, parent: RoomState, code_hash: str, flow_hash: str
) -> dict:
    child.verify()
    validate_parent(parent)
    validate_context(child.crypto_context)
    if child.crypto_context != parent.crypto_context or child.policy != parent.policy:
        raise ValueError("FHE child changed policy or crypto context")
    bindings = json.loads(child.transition.bindings_json or "{}")
    request = bindings["request"]
    expected_request = bind_request(parent, request["spec"], code_hash, flow_hash)
    if canonical_json(request) != canonical_json(expected_request):
        raise ValueError("FHE request does not bind exact parent, code, policy, or context")
    spec = request["spec"]
    if (
        child.id != OUTPUT_STATE_ID
        or child.room_id != parent.room_id
        or child.parent_state_ids != (parent.id,)
        or len(child.artifacts) != 1
        or child.artifacts[0].id != OUTPUT_ARTIFACT_ID
    ):
        raise ValueError("Invalid M6 child state lineage or output")
    validate_artifact(
        child.artifacts[0],
        state_id=child.id,
        holder=EVALUATOR,
        context=child.crypto_context,
    )
    expected_transition = make_transition(parent, expected_request, child.artifacts[0])
    if child.transition.to_dict() != expected_transition.to_dict():
        raise ValueError("Invalid M6 transition commitment")
    return spec
