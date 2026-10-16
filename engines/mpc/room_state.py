"""Immutable RoomState domain model and encrypted local share storage.

The public RoomState document is duplicated at each participant. Each
ArtifactRef names one logical SPU value, while its encrypted share remains in
the local KryptNode state directory. AES-256-GCM additional authenticated data
binds every encrypted share to its room, state, artifact, party, and crypto
context.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


ENVELOPE_MAGIC = b"KRYPTROOM-ROOMSTATE-AES256GCM-V1\x00"
NONCE_BYTES = 12
KEY_BYTES = 32
CANONICALIZATION = "json-sort-keys-v1"


def canonical_json(value: Any) -> bytes:
    """Return the repository's deterministic JSON commitment encoding."""

    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def artifact_aad(
    *, room_id: str, state_id: str, artifact_id: str, party: str, crypto_context_id: str
) -> bytes:
    return canonical_json(
        {
            "artifactId": artifact_id,
            "cipher": "AES-256-GCM",
            "cryptoContextId": crypto_context_id,
            "party": party,
            "roomId": room_id,
            "stateId": state_id,
        }
    )


def _read_key(path: str) -> bytes:
    key = Path(path).read_bytes()
    if len(key) != KEY_BYTES:
        raise ValueError("KryptNode state key is not a 256-bit AES key")
    return key


def ensure_local_state_key(path: str) -> None:
    """Create the node-local at-rest key once, without replacing an old key."""

    key_path = Path(path)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(
            key_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
    except FileExistsError:
        _read_key(path)
        return

    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(AESGCM.generate_key(bit_length=256))
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        key_path.unlink(missing_ok=True)
        raise


class _EncryptedWriteContext:
    def __init__(self, path: str, key_path: str, aad: bytes):
        self._path = Path(path)
        self._key_path = key_path
        self._aad = aad
        self._buffer = io.BytesIO()

    def __enter__(self) -> io.BytesIO:
        return self._buffer

    def __exit__(self, error_type: Any, error: Any, traceback: Any) -> bool:
        if error_type is not None:
            self._buffer.close()
            return False

        plaintext = self._buffer.getvalue()
        self._buffer.close()
        nonce = os.urandom(NONCE_BYTES)
        ciphertext = AESGCM(_read_key(self._key_path)).encrypt(
            nonce, plaintext, self._aad
        )
        envelope = ENVELOPE_MAGIC + nonce + ciphertext

        self._path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(
            self._path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        try:
            with os.fdopen(descriptor, "wb") as output:
                output.write(envelope)
                output.flush()
                os.fsync(output.fileno())
        except BaseException:
            self._path.unlink(missing_ok=True)
            raise
        return False


class _EncryptedReadContext:
    def __init__(self, path: str, key_path: str, aad: bytes):
        self._path = Path(path)
        self._key_path = key_path
        self._aad = aad
        self._buffer: io.BytesIO | None = None

    def __enter__(self) -> io.BytesIO:
        envelope = self._path.read_bytes()
        prefix_length = len(ENVELOPE_MAGIC)
        if not envelope.startswith(ENVELOPE_MAGIC):
            raise ValueError("Persisted share has an invalid encrypted envelope")
        if len(envelope) <= prefix_length + NONCE_BYTES:
            raise ValueError("Persisted share has a truncated encrypted envelope")
        nonce = envelope[prefix_length : prefix_length + NONCE_BYTES]
        ciphertext = envelope[prefix_length + NONCE_BYTES :]
        try:
            plaintext = AESGCM(_read_key(self._key_path)).decrypt(
                nonce, ciphertext, self._aad
            )
        except InvalidTag as error:
            raise ValueError("Persisted share authentication failed") from error
        self._buffer = io.BytesIO(plaintext)
        return self._buffer

    def __exit__(self, error_type: Any, error: Any, traceback: Any) -> bool:
        if self._buffer is not None:
            self._buffer.close()
        return False


@dataclass(frozen=True)
class EncryptedShareWriter:
    path: str
    key_path: str
    aad: bytes

    def __call__(self) -> _EncryptedWriteContext:
        return _EncryptedWriteContext(self.path, self.key_path, self.aad)


@dataclass(frozen=True)
class EncryptedShareReader:
    path: str
    key_path: str
    aad: bytes

    def __call__(self) -> _EncryptedReadContext:
        return _EncryptedReadContext(self.path, self.key_path, self.aad)


@dataclass(frozen=True)
class CryptoContext:
    id: str
    backend: str
    backend_version: str
    protocol: str
    field: str
    security_model: str
    participants: tuple[str, ...]
    artifact_cipher: str
    key_scope: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "backend": self.backend,
            "backendVersion": self.backend_version,
            "protocol": self.protocol,
            "field": self.field,
            "securityModel": self.security_model,
            "participants": list(self.participants),
            "artifactCipher": self.artifact_cipher,
            "keyScope": self.key_scope,
        }


@dataclass(frozen=True)
class AuthorizedReveal:
    name: str
    recipients: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "recipients": list(self.recipients)}


@dataclass(frozen=True)
class StatePolicy:
    default_reveal: str
    plaintext_materialization: str
    matched_identifier_reveal: str
    future_identifier_disclosure_requires_opt_in: bool
    authorized_reveals: tuple[AuthorizedReveal, ...]
    allowed_operators: tuple[str, ...] = ()
    allowed_input_artifact_ids: tuple[str, ...] = ()

    def authorizes(self, name: str, recipients: tuple[str, ...]) -> bool:
        return any(
            reveal.name == name and set(reveal.recipients) == set(recipients)
            for reveal in self.authorized_reveals
        )

    def to_dict(self) -> dict[str, Any]:
        value = {
            "defaultReveal": self.default_reveal,
            "plaintextMaterialization": self.plaintext_materialization,
            "matchedIdentifierReveal": self.matched_identifier_reveal,
            "futureIdentifierDisclosure": {
                "requiresExplicitOptIn": self.future_identifier_disclosure_requires_opt_in
            },
            "authorizedReveals": [
                reveal.to_dict() for reveal in self.authorized_reveals
            ],
        }
        if self.allowed_operators or self.allowed_input_artifact_ids:
            value["allowedOperators"] = list(self.allowed_operators)
            value["allowedInputArtifactIds"] = list(self.allowed_input_artifact_ids)
        return value


@dataclass(frozen=True)
class CiphertextRef:
    party: str
    uri: str
    sha256: str
    size_bytes: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "party": self.party,
            "uri": self.uri,
            "sha256": self.sha256,
            "sizeBytes": self.size_bytes,
        }


@dataclass(frozen=True)
class ArtifactRef:
    id: str
    kind: str
    media_type: str
    visibility: str
    crypto_context_id: str
    shape: tuple[int, ...]
    dtype: str
    includes_identifiers: bool
    ciphertexts: tuple[CiphertextRef, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "mediaType": self.media_type,
            "visibility": self.visibility,
            "cryptoContextId": self.crypto_context_id,
            "shape": list(self.shape),
            "dtype": self.dtype,
            "includesIdentifiers": self.includes_identifiers,
            "ciphertexts": [ciphertext.to_dict() for ciphertext in self.ciphertexts],
        }


@dataclass(frozen=True)
class StateTransition:
    id: str
    operation: str
    parent_state_ids: tuple[str, ...]
    input_job_id: str
    output_artifact_ids: tuple[str, ...]
    effective_at: str
    # Canonical JSON keeps the optional extension immutable and legacy encodings unchanged.
    bindings_json: str | None = None

    def to_dict(self) -> dict[str, Any]:
        value = {
            "id": self.id,
            "operation": self.operation,
            "parentStateIds": list(self.parent_state_ids),
            "inputJobId": self.input_job_id,
            "outputArtifactIds": list(self.output_artifact_ids),
            "effectiveAt": self.effective_at,
        }
        if self.bindings_json is not None:
            value["bindings"] = json.loads(self.bindings_json)
        return value


@dataclass(frozen=True)
class StateCommitment:
    algorithm: str
    canonicalization: str
    value: str

    def to_dict(self) -> dict[str, str]:
        return {
            "algorithm": self.algorithm,
            "canonicalization": self.canonicalization,
            "value": self.value,
        }


@dataclass(frozen=True)
class RoomState:
    schema_version: str
    id: str
    room_id: str
    parent_state_ids: tuple[str, ...]
    artifacts: tuple[ArtifactRef, ...]
    transition: StateTransition
    policy: StatePolicy
    crypto_context: CryptoContext
    commitment: StateCommitment

    def content_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": self.schema_version,
            "id": self.id,
            "roomId": self.room_id,
            "parentStateIds": list(self.parent_state_ids),
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "transition": self.transition.to_dict(),
            "policy": self.policy.to_dict(),
            "cryptoContext": self.crypto_context.to_dict(),
        }

    def to_dict(self) -> dict[str, Any]:
        value = self.content_dict()
        value["commitment"] = self.commitment.to_dict()
        return value

    def verify(self) -> None:
        if self.schema_version != "1":
            raise ValueError("Unsupported RoomState schema version")
        if not self.id or not self.room_id:
            raise ValueError("RoomState and room identifiers are required")
        if len(set(self.parent_state_ids)) != len(self.parent_state_ids):
            raise ValueError("RoomState parent identifiers must be unique")
        if len({artifact.id for artifact in self.artifacts}) != len(self.artifacts):
            raise ValueError("RoomState artifact identifiers must be unique")
        expected = sha256_hex(canonical_json(self.content_dict()))
        if self.commitment != StateCommitment(
            algorithm="SHA-256",
            canonicalization=CANONICALIZATION,
            value=expected,
        ):
            raise ValueError("RoomState commitment verification failed")
        if self.parent_state_ids != self.transition.parent_state_ids:
            raise ValueError("RoomState parents do not match its transition")
        if any(
            artifact.crypto_context_id != self.crypto_context.id
            for artifact in self.artifacts
        ):
            raise ValueError("RoomState artifact is bound to another crypto context")


def create_room_state(
    *,
    state_id: str,
    room_id: str,
    parent_state_ids: tuple[str, ...],
    artifacts: tuple[ArtifactRef, ...],
    transition: StateTransition,
    policy: StatePolicy,
    crypto_context: CryptoContext,
) -> RoomState:
    placeholder = StateCommitment("SHA-256", CANONICALIZATION, "")
    state = RoomState(
        schema_version="1",
        id=state_id,
        room_id=room_id,
        parent_state_ids=parent_state_ids,
        artifacts=artifacts,
        transition=transition,
        policy=policy,
        crypto_context=crypto_context,
        commitment=placeholder,
    )
    commitment = StateCommitment(
        algorithm="SHA-256",
        canonicalization=CANONICALIZATION,
        value=sha256_hex(canonical_json(state.content_dict())),
    )
    committed = RoomState(
        schema_version=state.schema_version,
        id=state.id,
        room_id=state.room_id,
        parent_state_ids=state.parent_state_ids,
        artifacts=state.artifacts,
        transition=state.transition,
        policy=state.policy,
        crypto_context=state.crypto_context,
        commitment=commitment,
    )
    committed.verify()
    return committed


def write_room_state_exclusive(state: RoomState, path: Path) -> None:
    """Commit an immutable state document; existing state IDs cannot change."""

    state.verify()
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(canonical_json(state.to_dict()) + b"\n")
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def room_state_from_dict(value: dict[str, Any]) -> RoomState:
    context_value = value["cryptoContext"]
    policy_value = value["policy"]
    transition_value = value["transition"]
    commitment_value = value["commitment"]

    context = CryptoContext(
        id=context_value["id"],
        backend=context_value["backend"],
        backend_version=context_value["backendVersion"],
        protocol=context_value["protocol"],
        field=context_value["field"],
        security_model=context_value["securityModel"],
        participants=tuple(context_value["participants"]),
        artifact_cipher=context_value["artifactCipher"],
        key_scope=context_value["keyScope"],
    )
    policy = StatePolicy(
        default_reveal=policy_value["defaultReveal"],
        plaintext_materialization=policy_value["plaintextMaterialization"],
        matched_identifier_reveal=policy_value["matchedIdentifierReveal"],
        future_identifier_disclosure_requires_opt_in=policy_value[
            "futureIdentifierDisclosure"
        ]["requiresExplicitOptIn"],
        authorized_reveals=tuple(
            AuthorizedReveal(item["name"], tuple(item["recipients"]))
            for item in policy_value["authorizedReveals"]
        ),
        allowed_operators=tuple(policy_value.get("allowedOperators", [])),
        allowed_input_artifact_ids=tuple(policy_value.get("allowedInputArtifactIds", [])),
    )
    artifacts = tuple(
        ArtifactRef(
            id=artifact["id"],
            kind=artifact["kind"],
            media_type=artifact["mediaType"],
            visibility=artifact["visibility"],
            crypto_context_id=artifact["cryptoContextId"],
            shape=tuple(artifact["shape"]),
            dtype=artifact["dtype"],
            includes_identifiers=artifact["includesIdentifiers"],
            ciphertexts=tuple(
                CiphertextRef(
                    party=ciphertext["party"],
                    uri=ciphertext["uri"],
                    sha256=ciphertext["sha256"],
                    size_bytes=ciphertext["sizeBytes"],
                )
                for ciphertext in artifact["ciphertexts"]
            ),
        )
        for artifact in value["artifacts"]
    )
    transition = StateTransition(
        id=transition_value["id"],
        operation=transition_value["operation"],
        parent_state_ids=tuple(transition_value["parentStateIds"]),
        input_job_id=transition_value["inputJobId"],
        output_artifact_ids=tuple(transition_value["outputArtifactIds"]),
        effective_at=transition_value["effectiveAt"],
        bindings_json=(canonical_json(transition_value["bindings"]).decode("utf-8")
                       if "bindings" in transition_value else None),
    )
    state = RoomState(
        schema_version=value["schemaVersion"],
        id=value["id"],
        room_id=value["roomId"],
        parent_state_ids=tuple(value["parentStateIds"]),
        artifacts=artifacts,
        transition=transition,
        policy=policy,
        crypto_context=context,
        commitment=StateCommitment(
            algorithm=commitment_value["algorithm"],
            canonicalization=commitment_value["canonicalization"],
            value=commitment_value["value"],
        ),
    )
    state.verify()
    return state


def load_room_state(path: Path) -> RoomState:
    return room_state_from_dict(json.loads(path.read_text(encoding="utf-8")))


def inspect_ciphertexts(paths: dict[str, str]) -> dict[str, dict[str, Any]]:
    """Return non-secret integrity metadata for explicitly authorized sharing."""

    result: dict[str, dict[str, Any]] = {}
    for artifact_id, path in paths.items():
        payload = Path(path).read_bytes()
        if not payload.startswith(ENVELOPE_MAGIC):
            raise ValueError("Persisted share is not encrypted with the approved envelope")
        result[artifact_id] = {
            "sha256": sha256_hex(payload),
            "sizeBytes": len(payload),
        }
    return result
