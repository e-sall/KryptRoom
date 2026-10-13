"""M2.5 persistence and restart validation for the M2 private join handoff."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import jax.numpy as jnp
import numpy as np
import secretflow as sf
from secretflow.device import SPUCompilerNumReturnsPolicy

from private_join import (
    PARTIES,
    build_private_join_handoff,
    create_devices,
    intersection_cardinality,
    load_job,
    load_local_dataset,
)
from room_state import (
    ArtifactRef,
    AuthorizedReveal,
    CiphertextRef,
    CryptoContext,
    EncryptedShareReader,
    EncryptedShareWriter,
    StatePolicy,
    StateTransition,
    artifact_aad,
    create_room_state,
    ensure_local_state_key,
    inspect_ciphertexts,
    load_room_state,
    write_room_state_exclusive,
)


SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
ARTIFACT_IDS = ("match-mask", "lab-a-features", "lab-b-features")
STATE_KEY_RELATIVE_PATH = "keys/room-state-v1.key"


def _require_safe_component(name: str, value: Any) -> str:
    if not isinstance(value, str) or SAFE_COMPONENT.fullmatch(value) is None:
        raise ValueError(f"{name} is not a safe state-store component")
    return value


def load_state_job(path: Path, private_join_job: dict[str, Any]) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    room_id = _require_safe_component("roomId", manifest.get("roomId"))
    state_id = _require_safe_component("stateId", manifest.get("stateId"))
    transition = manifest.get("transition", {})
    context = manifest.get("cryptoContext", {})
    policy = manifest.get("statePolicy", {})

    if manifest.get("version") != "1" or manifest.get("operation") != "persist-private-join":
        raise ValueError("Unsupported persistent-state job")
    if manifest.get("sourceJobId") != private_join_job["jobId"]:
        raise ValueError("Persistent state is not bound to the private-join job")
    if transition.get("operation") != "private-join":
        raise ValueError("State transition operation is invalid")
    _require_safe_component("transition.id", transition.get("id"))
    parents = transition.get("parentStateIds")
    if not isinstance(parents, list) or any(
        not isinstance(parent, str) or SAFE_COMPONENT.fullmatch(parent) is None
        for parent in parents
    ):
        raise ValueError("parentStateIds must be a list of state identifiers")
    if parents:
        raise ValueError("The initial S1 transition cannot have a parent")
    if transition.get("outputArtifactIds") != list(ARTIFACT_IDS):
        raise ValueError("State transition artifacts do not match the M2 handoff")
    if not isinstance(transition.get("effectiveAt"), str):
        raise ValueError("State transition effectiveAt is required")

    approved_backend = private_join_job["backend"]
    if context != {
        "id": "secretflow-spu-cheetah-fm128-v1",
        "backend": approved_backend["name"],
        "backendVersion": approved_backend["version"],
        "protocol": approved_backend["protocol"],
        "field": approved_backend["field"],
        "securityModel": approved_backend["securityModel"],
        "participants": list(PARTIES),
        "artifactCipher": "AES-256-GCM",
        "keyScope": "per-kryptnode-local",
    }:
        raise ValueError("Persistent-state crypto context is not approved")

    expected_reveals = [
        {"name": "intersection-cardinality", "recipients": [*PARTIES, "ui"]},
        {"name": "ciphertext-metadata", "recipients": list(PARTIES)},
        {"name": "matched-feature-sum", "recipients": list(PARTIES)},
    ]
    if policy != {
        "defaultReveal": "deny",
        "plaintextMaterialization": "forbidden",
        "matchedIdentifierReveal": "forbidden",
        "futureIdentifierDisclosure": {"requiresExplicitOptIn": True},
        "authorizedReveals": expected_reveals,
    }:
        raise ValueError("Persistent-state disclosure policy is not approved")

    _require_safe_component("roomId", room_id)
    _require_safe_component("stateId", state_id)
    return manifest


def build_crypto_context(manifest: dict[str, Any]) -> CryptoContext:
    value = manifest["cryptoContext"]
    return CryptoContext(
        id=value["id"],
        backend=value["backend"],
        backend_version=value["backendVersion"],
        protocol=value["protocol"],
        field=value["field"],
        security_model=value["securityModel"],
        participants=tuple(value["participants"]),
        artifact_cipher=value["artifactCipher"],
        key_scope=value["keyScope"],
    )


def build_policy(manifest: dict[str, Any]) -> StatePolicy:
    value = manifest["statePolicy"]
    return StatePolicy(
        default_reveal=value["defaultReveal"],
        plaintext_materialization=value["plaintextMaterialization"],
        matched_identifier_reveal=value["matchedIdentifierReveal"],
        future_identifier_disclosure_requires_opt_in=value[
            "futureIdentifierDisclosure"
        ]["requiresExplicitOptIn"],
        authorized_reveals=tuple(
            AuthorizedReveal(item["name"], tuple(item["recipients"]))
            for item in value["authorizedReveals"]
        ),
    )


def require_authorized_reveal(
    policy: StatePolicy, name: str, recipients: tuple[str, ...]
) -> None:
    if policy.default_reveal != "deny" or not policy.authorizes(name, recipients):
        raise PermissionError(f"State policy does not authorize reveal: {name}")


def state_directory(state_root: Path, room_id: str, state_id: str) -> Path:
    return state_root / "rooms" / room_id / "states" / state_id


def artifact_paths(state_root: Path, room_id: str, state_id: str) -> dict[str, str]:
    directory = state_directory(state_root, room_id, state_id) / "artifacts"
    return {
        artifact_id: str(directory / f"{artifact_id}.share.enc")
        for artifact_id in ARTIFACT_IDS
    }


def share_io(
    *,
    reader: bool,
    state_root: Path,
    room_id: str,
    state_id: str,
    artifact_id: str,
    crypto_context_id: str,
) -> list[EncryptedShareReader] | list[EncryptedShareWriter]:
    paths = artifact_paths(state_root, room_id, state_id)
    key_path = str(state_root / STATE_KEY_RELATIVE_PATH)
    entries: list[EncryptedShareReader] | list[EncryptedShareWriter]
    if reader:
        entries = [
            EncryptedShareReader(
                path=paths[artifact_id],
                key_path=key_path,
                aad=artifact_aad(
                    room_id=room_id,
                    state_id=state_id,
                    artifact_id=artifact_id,
                    party=party,
                    crypto_context_id=crypto_context_id,
                ),
            )
            for party in PARTIES
        ]
    else:
        entries = [
            EncryptedShareWriter(
                path=paths[artifact_id],
                key_path=key_path,
                aad=artifact_aad(
                    room_id=room_id,
                    state_id=state_id,
                    artifact_id=artifact_id,
                    party=party,
                    crypto_context_id=crypto_context_id,
                ),
            )
            for party in PARTIES
        ]
    return entries


def _reconstruct_scalar_for_participants(
    secret_value: Any,
    parties: dict[str, sf.PYU],
    policy: StatePolicy,
    reveal_name: str,
    recipients: tuple[str, ...],
) -> int:
    require_authorized_reveal(policy, reveal_name, recipients)
    participant_values = [secret_value.to(parties[party]) for party in PARTIES]
    reconstructed = [
        int(np.asarray(value).item()) for value in sf.reveal(participant_values)
    ]
    if len(set(reconstructed)) != 1:
        raise RuntimeError("Participants reconstructed different authorized outputs")
    return reconstructed[0]


def _build_artifact_refs(
    manifest: dict[str, Any],
    metadata: list[dict[str, dict[str, Any]]],
    max_rows: int,
) -> tuple[ArtifactRef, ...]:
    room_id = manifest["roomId"]
    state_id = manifest["stateId"]
    context_id = manifest["cryptoContext"]["id"]
    artifact_shapes = {
        "match-mask": (max_rows, max_rows),
        "lab-a-features": (max_rows, max_rows, 1),
        "lab-b-features": (max_rows, max_rows, 1),
    }
    artifacts: list[ArtifactRef] = []
    for artifact_id in ARTIFACT_IDS:
        ciphertexts = tuple(
            CiphertextRef(
                party=party,
                uri=(
                    f"local://{party}/rooms/{room_id}/states/{state_id}/"
                    f"artifacts/{artifact_id}.share.enc"
                ),
                sha256=metadata[index][artifact_id]["sha256"],
                size_bytes=metadata[index][artifact_id]["sizeBytes"],
            )
            for index, party in enumerate(PARTIES)
        )
        artifacts.append(
            ArtifactRef(
                id=artifact_id,
                kind="spu-secret-share",
                media_type="application/vnd.kryptroom.spu-share+encrypted",
                visibility="secret-shared",
                crypto_context_id=context_id,
                shape=artifact_shapes[artifact_id],
                dtype="int32",
                includes_identifiers=False,
                ciphertexts=ciphertexts,
            )
        )
    return tuple(artifacts)


def persist_private_join(
    self_party: str,
    private_join_manifest_path: Path,
    state_manifest_path: Path,
    local_input_path: str,
    state_root: Path,
) -> dict[str, Any]:
    private_join_job = load_job(private_join_manifest_path)
    manifest = load_state_job(state_manifest_path, private_join_job)
    context = build_crypto_context(manifest)
    policy = build_policy(manifest)
    room_id = manifest["roomId"]
    state_id = manifest["stateId"]
    local_state_path = state_directory(state_root, room_id, state_id) / "state.json"
    if local_state_path.exists():
        raise FileExistsError("RoomState is immutable and already exists")
    ensure_local_state_key(str(state_root / STATE_KEY_RELATIVE_PATH))

    participants = {entry["id"]: entry for entry in private_join_job["participants"]}
    join = private_join_job["join"]
    parties, secure_device = create_devices(
        self_party, f"{private_join_job['jobId']}-persist"
    )
    try:
        left_payload = parties["lab-a"](load_local_dataset)(
            local_input_path,
            participants["lab-a"]["featureColumn"],
            join["maxRowsPerParticipant"],
            join["maxIdentifierBytes"],
        )
        right_payload = parties["lab-b"](load_local_dataset)(
            local_input_path,
            participants["lab-b"]["featureColumn"],
            join["maxRowsPerParticipant"],
            join["maxIdentifierBytes"],
        )
        handoff = secure_device(
            build_private_join_handoff,
            num_returns_policy=SPUCompilerNumReturnsPolicy.FROM_USER,
            user_specified_num_returns=3,
        )(left_payload, right_payload)

        for artifact_id, secret_artifact in zip(ARTIFACT_IDS, handoff, strict=True):
            secure_device.dump(
                secret_artifact,
                share_io(
                    reader=False,
                    state_root=state_root,
                    room_id=room_id,
                    state_id=state_id,
                    artifact_id=artifact_id,
                    crypto_context_id=context.id,
                ),
            )

        secret_cardinality = secure_device(intersection_cardinality)(handoff[0])
        cardinality = _reconstruct_scalar_for_participants(
            secret_cardinality,
            parties,
            policy,
            "intersection-cardinality",
            (*PARTIES, "ui"),
        )

        require_authorized_reveal(policy, "ciphertext-metadata", PARTIES)
        local_paths = artifact_paths(state_root, room_id, state_id)
        encrypted_metadata = [
            parties[party](inspect_ciphertexts)(local_paths) for party in PARTIES
        ]
        metadata = sf.reveal(encrypted_metadata)

        artifacts = _build_artifact_refs(
            manifest,
            metadata,
            join["maxRowsPerParticipant"],
        )
        transition_value = manifest["transition"]
        transition = StateTransition(
            id=transition_value["id"],
            operation=transition_value["operation"],
            parent_state_ids=tuple(transition_value["parentStateIds"]),
            input_job_id=private_join_job["jobId"],
            output_artifact_ids=tuple(transition_value["outputArtifactIds"]),
            effective_at=transition_value["effectiveAt"],
        )
        state = create_room_state(
            state_id=state_id,
            room_id=room_id,
            parent_state_ids=transition.parent_state_ids,
            artifacts=artifacts,
            transition=transition,
            policy=policy,
            crypto_context=context,
        )
        write_room_state_exclusive(state, local_state_path)
        return {
            "intersectionCardinality": cardinality,
            "matchedIdentifiersRevealed": False,
            "plaintextJoinMaterialized": False,
            "roomStateId": state.id,
            "stateCommitment": state.commitment.value,
            "statePersisted": True,
        }
    finally:
        sf.shutdown()


def private_matched_feature_sum(
    secret_match_mask: jnp.ndarray,
    secret_left_features: jnp.ndarray,
    secret_right_features: jnp.ndarray,
) -> jnp.ndarray:
    """Minimal post-restart MPC consumer; not the Milestone 3 analytics API."""

    mask = secret_match_mask[:, :, jnp.newaxis]
    return jnp.sum(
        (secret_left_features + secret_right_features) * mask,
        dtype=jnp.int32,
    )


def _verify_local_artifacts(
    *, self_party: str, state: Any, state_root: Path
) -> None:
    paths = artifact_paths(state_root, state.room_id, state.id)
    metadata = inspect_ciphertexts(paths)
    for artifact in state.artifacts:
        expected = next(
            ciphertext
            for ciphertext in artifact.ciphertexts
            if ciphertext.party == self_party
        )
        actual = metadata[artifact.id]
        if actual["sha256"] != expected.sha256 or actual["sizeBytes"] != expected.size_bytes:
            raise ValueError("Local encrypted share does not match its ArtifactRef")


def run_private_analytics(
    self_party: str,
    private_join_manifest_path: Path,
    state_manifest_path: Path,
    state_root: Path,
) -> dict[str, Any]:
    private_join_job = load_job(private_join_manifest_path)
    manifest = load_state_job(state_manifest_path, private_join_job)
    state_path = state_directory(
        state_root, manifest["roomId"], manifest["stateId"]
    ) / "state.json"
    state = load_room_state(state_path)
    if state.id != manifest["stateId"] or state.room_id != manifest["roomId"]:
        raise ValueError("Persisted RoomState identity does not match the requested state")
    expected_context = build_crypto_context(manifest)
    if state.crypto_context != expected_context:
        raise ValueError("Persisted RoomState crypto context does not match the runtime")
    if state.policy != build_policy(manifest):
        raise ValueError("Persisted RoomState policy does not match the requested operation")
    if tuple(artifact.id for artifact in state.artifacts) != ARTIFACT_IDS:
        raise ValueError("Persisted RoomState artifacts do not match the M2 handoff")
    _verify_local_artifacts(
        self_party=self_party,
        state=state,
        state_root=state_root,
    )

    parties, secure_device = create_devices(
        self_party, f"{private_join_job['jobId']}-analytics"
    )
    try:
        artifacts_by_id = {artifact.id: artifact for artifact in state.artifacts}
        loaded = {
            artifact_id: secure_device.load(
                share_io(
                    reader=True,
                    state_root=state_root,
                    room_id=state.room_id,
                    state_id=state.id,
                    artifact_id=artifact_id,
                    crypto_context_id=artifacts_by_id[
                        artifact_id
                    ].crypto_context_id,
                )
            )
            for artifact_id in ARTIFACT_IDS
        }
        secret_aggregate = secure_device(private_matched_feature_sum)(
            loaded["match-mask"],
            loaded["lab-a-features"],
            loaded["lab-b-features"],
        )
        aggregate = _reconstruct_scalar_for_participants(
            secret_aggregate,
            parties,
            state.policy,
            "matched-feature-sum",
            PARTIES,
        )
        return {
            "matchedIdentifiersRevealed": False,
            "plaintextJoinMaterialized": False,
            "privateAggregate": aggregate,
            "roomStateId": state.id,
            "stateCommitment": state.commitment.value,
            "stateReloaded": True,
        }
    finally:
        sf.shutdown()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("persist", "analytics"), required=True)
    parser.add_argument("--party", choices=PARTIES, required=True)
    parser.add_argument("--private-join-manifest", type=Path, required=True)
    parser.add_argument("--state-manifest", type=Path, required=True)
    parser.add_argument("--local-input")
    parser.add_argument("--state-root", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.phase == "persist":
        if not args.local_input:
            raise ValueError("The persist phase requires a local input")
        result = persist_private_join(
            args.party,
            args.private_join_manifest,
            args.state_manifest,
            args.local_input,
            args.state_root,
        )
    else:
        result = run_private_analytics(
            args.party,
            args.private_join_manifest,
            args.state_manifest,
            args.state_root,
        )
    print(json.dumps(result, separators=(",", ":"), sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
