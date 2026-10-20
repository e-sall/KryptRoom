"""Immutable M7 inclusion record and separate dynamic status snapshots."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Any


ANCHOR_ID_DOMAIN = b"KRYPTROOM-CHAIN-ANCHOR-ID-V1\x00"


def _hex_bytes(value: str, length: int, name: str) -> bytes:
    normalized = value.removeprefix("0x")
    if len(normalized) != length * 2 or normalized.lower() != normalized:
        raise ValueError(f"{name} must be {length} lowercase hexadecimal bytes")
    try:
        return bytes.fromhex(normalized)
    except ValueError as error:
        raise ValueError(f"{name} must be {length} lowercase hexadecimal bytes") from error


def derive_anchor_id(
    *, chain_id: int, contract_address: str, transaction_hash: str, log_index: int
) -> str:
    """Bind one exact chain inclusion with fixed-width, domain-separated bytes."""

    if chain_id <= 0 or chain_id >= 1 << 256:
        raise ValueError("chainId is outside uint256")
    if log_index < 0 or log_index >= 1 << 64:
        raise ValueError("logIndex is outside uint64")
    material = (
        ANCHOR_ID_DOMAIN
        + chain_id.to_bytes(32, "big")
        + _hex_bytes(contract_address, 20, "contractAddress")
        + _hex_bytes(transaction_hash, 32, "transactionHash")
        + log_index.to_bytes(8, "big")
    )
    return "anchor-" + hashlib.sha256(material).hexdigest()


class AnchorStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FINALIZED = "FINALIZED"
    ORPHANED = "ORPHANED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class ChainAnchor:
    version: str
    anchor_id: str
    anchor_commitment: str
    subject_type: str
    subject_commitment: str
    evidence_type: str
    evidence_commitment: str
    room_id: str
    transition_id: str
    output_state_id: str
    backend: str
    chain_id: int
    contract_address: str
    contract_runtime_code_hash: str
    transaction_hash: str
    log_index: int
    submitter: str
    block_number: int
    block_hash: str
    block_timestamp: str
    created_at: str

    def verify_identity(self) -> None:
        if self.version != "1":
            raise ValueError("Unsupported ChainAnchor version")
        expected = derive_anchor_id(
            chain_id=self.chain_id,
            contract_address=self.contract_address,
            transaction_hash=self.transaction_hash,
            log_index=self.log_index,
        )
        if self.anchor_id != expected:
            raise ValueError("ChainAnchor identity mismatch")

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "anchorId": self.anchor_id,
            "anchorCommitment": self.anchor_commitment,
            "subjectType": self.subject_type,
            "subjectCommitment": self.subject_commitment,
            "evidenceType": self.evidence_type,
            "evidenceCommitment": self.evidence_commitment,
            "roomId": self.room_id,
            "transitionId": self.transition_id,
            "outputStateId": self.output_state_id,
            "backend": self.backend,
            "chainId": self.chain_id,
            "contractAddress": self.contract_address,
            "contractRuntimeCodeHash": self.contract_runtime_code_hash,
            "transactionHash": self.transaction_hash,
            "logIndex": self.log_index,
            "submitter": self.submitter,
            "blockNumber": self.block_number,
            "blockHash": self.block_hash,
            "blockTimestamp": self.block_timestamp,
            "createdAt": self.created_at,
        }
    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ChainAnchor":
        anchor = cls(
            version=value["version"],
            anchor_id=value["anchorId"],
            anchor_commitment=value["anchorCommitment"],
            subject_type=value["subjectType"],
            subject_commitment=value["subjectCommitment"],
            evidence_type=value["evidenceType"],
            evidence_commitment=value["evidenceCommitment"],
            room_id=value["roomId"],
            transition_id=value["transitionId"],
            output_state_id=value["outputStateId"],
            backend=value["backend"],
            chain_id=value["chainId"],
            contract_address=value["contractAddress"],
            contract_runtime_code_hash=value["contractRuntimeCodeHash"],
            transaction_hash=value["transactionHash"],
            log_index=value["logIndex"],
            submitter=value["submitter"],
            block_number=value["blockNumber"],
            block_hash=value["blockHash"],
            block_timestamp=value["blockTimestamp"],
            created_at=value["createdAt"],
        )
        anchor.verify_identity()
        return anchor


@dataclass(frozen=True)
class AnchorStatusRecord:
    anchor_id: str
    status: AnchorStatus
    observed_at: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {
            "anchorId": self.anchor_id,
            "status": self.status.value,
            "observedAt": self.observed_at,
            "detail": self.detail,
        }
