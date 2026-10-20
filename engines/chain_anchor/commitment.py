"""Exact domain-separated M7 commitment formulas.

This module imports the existing RoomState canonical JSON function. M7 does not
define or silently substitute another JSON canonicalization format.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from engines.mpc.room_state import canonical_json, room_state_from_dict


ANCHOR_DOMAIN = b"KRYPTROOM-CHAIN-ANCHOR-V1"
STATE_PROOF_DOCUMENT_DOMAIN = b"KRYPTROOM-STATE-PROOF-DOCUMENT-V1"
SUBJECT_ROOM_STATE_V1 = 0x01
EVIDENCE_NONE = 0x00
EVIDENCE_STATE_PROOF_V1 = 0x01
ZERO32 = bytes(32)
ROOT = Path(__file__).resolve().parents[2]


class CommitmentError(ValueError):
    """An input cannot be represented by the exact M7 commitment contract."""


def strict_json_load(path: str | Path) -> dict[str, Any]:
    """Load one explicit metadata JSON object and reject ambiguous JSON."""

    target = Path(path)
    if target.suffix != ".json" or target.is_symlink() or not target.is_file():
        raise CommitmentError("Only explicit regular JSON metadata files are accepted")

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise CommitmentError("Duplicate JSON key")
            result[key] = value
        return result

    value = json.loads(
        target.read_text(encoding="utf-8"),
        object_pairs_hook=pairs,
        parse_constant=lambda item: (_ for _ in ()).throw(
            CommitmentError(f"Non-finite JSON value: {item}")
        ),
    )
    if not isinstance(value, dict):
        raise CommitmentError("Metadata document must be a JSON object")
    return value


def _raw_hex32(value: str, name: str) -> bytes:
    normalized = value.removeprefix("0x")
    if len(normalized) != 64 or normalized.lower() != normalized:
        raise CommitmentError(f"{name} must be 32 lowercase hexadecimal bytes")
    try:
        return bytes.fromhex(normalized)
    except ValueError as error:
        raise CommitmentError(f"{name} must be 32 lowercase hexadecimal bytes") from error


def validate_state_proof_document(value: dict[str, Any]) -> None:
    schema = strict_json_load(ROOT / "packages/manifests/state-proof.schema.json")
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)


def load_verified_room_state(path: str | Path):
    """Verify only committed RoomState metadata; never resolve artifact URIs."""

    value = strict_json_load(path)
    state = room_state_from_dict(value)
    state.verify()
    if canonical_json(state.to_dict()) != canonical_json(value):
        raise CommitmentError("RoomState contains unknown or discarded structure")
    return state


def state_proof_document_commitment(state_proof: dict[str, Any]) -> str:
    """Return lowercase SHA-256 hex for the exact canonical StateProof document."""

    validate_state_proof_document(state_proof)
    return hashlib.sha256(
        STATE_PROOF_DOCUMENT_DOMAIN + b"\x00" + canonical_json(state_proof)
    ).hexdigest()


def anchor_commitment(
    *,
    output_state_commitment: str,
    evidence_type: int,
    evidence_commitment: str | None = None,
    subject_type: int = SUBJECT_ROOM_STATE_V1,
) -> str:
    """Return the exact V1 EVM bytes32 as a 0x-prefixed lowercase value."""

    if subject_type != SUBJECT_ROOM_STATE_V1:
        raise CommitmentError("Unsupported M7 subject type")
    subject = _raw_hex32(output_state_commitment, "outputStateCommitment")
    if evidence_type == EVIDENCE_NONE:
        evidence = ZERO32
        if evidence_commitment not in (None, ZERO32.hex()):
            raise CommitmentError("NONE evidence requires ZERO32")
    elif evidence_type == EVIDENCE_STATE_PROOF_V1:
        if evidence_commitment is None:
            raise CommitmentError("STATE_PROOF_V1 requires an evidence commitment")
        evidence = _raw_hex32(evidence_commitment, "evidenceCommitment")
    else:
        raise CommitmentError("Unsupported M7 evidence type")

    payload = (
        ANCHOR_DOMAIN
        + b"\x00"
        + bytes([subject_type])
        + subject
        + bytes([evidence_type])
        + evidence
    )
    digest = hashlib.sha256(payload).hexdigest()
    if digest == ZERO32.hex():
        raise CommitmentError("Anchor commitment unexpectedly resolved to zero")
    return "0x" + digest
