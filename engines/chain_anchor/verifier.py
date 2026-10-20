"""Independent M7 verification layers for chain inclusion and package matching."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Crypto.Hash import keccak

from engines.chain_anchor.commitment import (
    EVIDENCE_NONE,
    EVIDENCE_STATE_PROOF_V1,
    ZERO32,
    anchor_commitment,
    state_proof_document_commitment,
    validate_state_proof_document,
)
from engines.chain_anchor.model import AnchorStatus, AnchorStatusRecord, ChainAnchor
from engines.chain_anchor.rpc import RpcClient
from engines.mpc.room_state import canonical_json, room_state_from_dict


BASE_SEPOLIA_CHAIN_ID = 84532
EVENT_SIGNATURE = b"AnchorRecorded(bytes32,address)"


def keccak256(value: bytes) -> bytes:
    digest = keccak.new(digest_bits=256)
    digest.update(value)
    return digest.digest()


ANCHOR_RECORDED_TOPIC = "0x" + keccak256(EVENT_SIGNATURE).hex()


class ChainVerificationError(ValueError):
    def __init__(self, message: str, status: AnchorStatus = AnchorStatus.FAILED):
        super().__init__(message)
        self.status = status


@dataclass(frozen=True)
class PackageMatchResult:
    anchor_commitment: str
    subject_commitment: str
    evidence_commitment: str
    m5_proof_validation_required: bool


def _quantity(value: str, name: str) -> int:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ChainVerificationError(f"{name} is not an Ethereum quantity")
    try:
        return int(value, 16)
    except ValueError as error:
        raise ChainVerificationError(f"{name} is not an Ethereum quantity") from error


def _normalized_address(value: str, name: str) -> str:
    normalized = value.lower()
    if not normalized.startswith("0x") or len(normalized) != 42:
        raise ChainVerificationError(f"{name} is not an Ethereum address")
    try:
        bytes.fromhex(normalized[2:])
    except ValueError as error:
        raise ChainVerificationError(f"{name} is not an Ethereum address") from error
    return normalized


def _block_timestamp(block: dict[str, Any]) -> str:
    value = datetime.fromtimestamp(_quantity(block["timestamp"], "block timestamp"), timezone.utc)
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ancestor_matches(
    rpc: RpcClient,
    descendant: dict[str, Any],
    ancestor_number: int,
    ancestor_hash: str,
    *,
    max_depth: int = 4096,
) -> bool:
    current = descendant
    current_number = _quantity(current["number"], "block number")
    if current_number < ancestor_number or current_number - ancestor_number > max_depth:
        return False
    while current_number > ancestor_number:
        previous_number = current_number
        current = rpc.call("eth_getBlockByHash", [current["parentHash"], False])
        if current is None:
            return False
        current_number = _quantity(current["number"], "block number")
        if current_number != previous_number - 1:
            return False
    return current.get("hash", "").lower() == ancestor_hash.lower()


def _chain_status(anchor: ChainAnchor, rpc: RpcClient) -> AnchorStatus:
    finalized = rpc.call("eth_getBlockByNumber", ["finalized", False])
    if finalized is not None and _ancestor_matches(
        rpc, finalized, anchor.block_number, anchor.block_hash
    ):
        return AnchorStatus.FINALIZED
    safe = rpc.call("eth_getBlockByNumber", ["safe", False])
    if safe is not None and _ancestor_matches(rpc, safe, anchor.block_number, anchor.block_hash):
        return AnchorStatus.CONFIRMED
    return AnchorStatus.PENDING


def verify_chain_layer(
    anchor: ChainAnchor,
    rpc: RpcClient,
    *,
    expected_chain_id: int = BASE_SEPOLIA_CHAIN_ID,
    expected_contract_address: str,
    expected_runtime_code_hash: str,
    require_finalized: bool = True,
    observed_at: str,
) -> AnchorStatusRecord:
    """Layer A: verify one exact canonical event inclusion and Base finality."""

    anchor.verify_identity()
    if anchor.chain_id != expected_chain_id:
        raise ChainVerificationError("ChainAnchor targets the wrong chainId")
    if _quantity(rpc.call("eth_chainId", []), "chainId") != expected_chain_id:
        raise ChainVerificationError("RPC reports the wrong chainId")
    trusted_contract = _normalized_address(expected_contract_address, "expected contract")
    if anchor.contract_address != trusted_contract:
        raise ChainVerificationError("ChainAnchor targets the wrong contract")
    if anchor.contract_runtime_code_hash != expected_runtime_code_hash.lower():
        raise ChainVerificationError("ChainAnchor runtime hash differs from deployment manifest")

    receipt = rpc.call("eth_getTransactionReceipt", [anchor.transaction_hash])
    if receipt is None:
        raise ChainVerificationError("Transaction receipt disappeared", AnchorStatus.ORPHANED)
    if receipt.get("transactionHash", "").lower() != anchor.transaction_hash.lower():
        raise ChainVerificationError("Transaction hash mismatch")
    if _normalized_address(receipt.get("to", ""), "receipt destination") != trusted_contract:
        raise ChainVerificationError("Anchor transaction targeted the wrong contract")
    if _quantity(receipt.get("status", "0x0"), "receipt status") != 1:
        raise ChainVerificationError("Anchor transaction failed", AnchorStatus.FAILED)
    if _quantity(receipt["blockNumber"], "receipt block number") != anchor.block_number:
        raise ChainVerificationError("Receipt block number mismatch")
    if receipt.get("blockHash", "").lower() != anchor.block_hash.lower():
        raise ChainVerificationError("Receipt block hash mismatch", AnchorStatus.ORPHANED)

    matching = [
        entry
        for entry in receipt.get("logs", [])
        if _quantity(entry.get("logIndex", "0x0"), "log index") == anchor.log_index
    ]
    if len(matching) != 1:
        raise ChainVerificationError("Expected AnchorRecorded log is missing")
    entry = matching[0]
    if entry.get("removed") is True:
        raise ChainVerificationError("Anchor event was removed by a reorg", AnchorStatus.ORPHANED)
    if _normalized_address(entry.get("address", ""), "event address") != anchor.contract_address:
        raise ChainVerificationError("Anchor event came from the wrong contract")
    if entry.get("transactionHash", "").lower() != anchor.transaction_hash.lower():
        raise ChainVerificationError("Anchor event transaction hash mismatch")
    if entry.get("blockHash", "").lower() != anchor.block_hash.lower():
        raise ChainVerificationError("Anchor event block hash mismatch", AnchorStatus.ORPHANED)
    if _quantity(entry.get("blockNumber", "0x0"), "event block number") != anchor.block_number:
        raise ChainVerificationError("Anchor event block number mismatch")
    topics = entry.get("topics", [])
    if len(topics) != 3 or topics[0].lower() != ANCHOR_RECORDED_TOPIC:
        raise ChainVerificationError("AnchorRecorded event signature mismatch")
    if topics[1].lower() != anchor.anchor_commitment.lower():
        raise ChainVerificationError("AnchorRecorded commitment mismatch")
    submitter = _normalized_address(anchor.submitter, "submitter")
    expected_submitter_topic = "0x" + (bytes(12) + bytes.fromhex(submitter[2:])).hex()
    if topics[2].lower() != expected_submitter_topic:
        raise ChainVerificationError("AnchorRecorded submitter mismatch")
    if entry.get("data", "0x") != "0x":
        raise ChainVerificationError("AnchorRecorded unexpectedly contains event data")

    canonical = rpc.call("eth_getBlockByNumber", [hex(anchor.block_number), False])
    if canonical is None or canonical.get("hash", "").lower() != anchor.block_hash.lower():
        raise ChainVerificationError("Inclusion is not in the canonical block", AnchorStatus.ORPHANED)
    if _block_timestamp(canonical) != anchor.block_timestamp:
        raise ChainVerificationError("Block timestamp mismatch")

    runtime = rpc.call("eth_getCode", [anchor.contract_address, hex(anchor.block_number)])
    try:
        runtime_bytes = bytes.fromhex(runtime.removeprefix("0x"))
    except (AttributeError, ValueError) as error:
        raise ChainVerificationError("RPC returned malformed runtime bytecode") from error
    if not runtime_bytes:
        raise ChainVerificationError("Expected contract has no runtime bytecode")
    actual_runtime_hash = "0x" + keccak256(runtime_bytes).hex()
    if actual_runtime_hash != expected_runtime_code_hash.lower():
        raise ChainVerificationError("Runtime bytecode hash mismatch")

    status = _chain_status(anchor, rpc)
    if require_finalized and status is not AnchorStatus.FINALIZED:
        raise ChainVerificationError("Anchor inclusion is not finalized", status)
    return AnchorStatusRecord(
        anchor_id=anchor.anchor_id,
        status=status,
        observed_at=observed_at,
        detail="canonical event and runtime code verified",
    )


def verify_package_layer(
    anchor: ChainAnchor,
    room_state: dict[str, Any],
    state_proof: dict[str, Any] | None,
) -> PackageMatchResult:
    """Layer B: match exact public metadata without validating an SP1 proof."""

    state = room_state_from_dict(room_state)
    state.verify()
    if canonical_json(state.to_dict()) != canonical_json(room_state):
        raise ValueError("RoomState contains unknown or discarded structure")
    if anchor.subject_type != "ROOM_STATE_V1":
        raise ValueError("Unsupported ChainAnchor subject type")
    if state.commitment.value != anchor.subject_commitment:
        raise ValueError("RoomState commitment does not match ChainAnchor")
    if (state.room_id, state.transition.id, state.id) != (
        anchor.room_id,
        anchor.transition_id,
        anchor.output_state_id,
    ):
        raise ValueError("RoomState identity does not match ChainAnchor metadata")

    if anchor.evidence_type == "NONE":
        if state_proof is not None:
            raise ValueError("NONE ChainAnchor cannot receive a StateProof")
        evidence_type = EVIDENCE_NONE
        evidence_commitment = ZERO32.hex()
        requires_m5 = False
    elif anchor.evidence_type == "STATE_PROOF_V1":
        if state_proof is None:
            raise ValueError("STATE_PROOF_V1 ChainAnchor requires a StateProof")
        validate_state_proof_document(state_proof)
        if (
            state_proof["roomId"],
            state_proof["transitionId"],
            state_proof["outputStateId"],
            state_proof["outputStateCommitment"],
        ) != (state.room_id, state.transition.id, state.id, state.commitment.value):
            raise ValueError("StateProof does not bind the supplied output RoomState")
        evidence_type = EVIDENCE_STATE_PROOF_V1
        evidence_commitment = state_proof_document_commitment(state_proof)
        requires_m5 = True
    else:
        raise ValueError("Unsupported ChainAnchor evidence type")

    if evidence_commitment != anchor.evidence_commitment:
        raise ValueError("Evidence commitment does not match ChainAnchor")
    recomputed = anchor_commitment(
        output_state_commitment=state.commitment.value,
        evidence_type=evidence_type,
        evidence_commitment=evidence_commitment,
    )
    if recomputed != anchor.anchor_commitment:
        raise ValueError("AnchorCommitment does not match the supplied package")
    return PackageMatchResult(
        anchor_commitment=recomputed,
        subject_commitment=state.commitment.value,
        evidence_commitment=evidence_commitment,
        m5_proof_validation_required=requires_m5,
    )


def m5_verifier_command(
    *,
    verifier: str | Path,
    receipt: str | Path,
    state_proof: str | Path,
    proof: str | Path,
    room_id: str,
    transition_id: str,
) -> list[str]:
    """Layer C command: explicit and separate from document-hash matching."""

    return [
        str(verifier),
        "verify",
        "--receipt",
        str(receipt),
        "--state-proof",
        str(state_proof),
        "--proof",
        str(proof),
        "--expect-room",
        room_id,
        "--expect-transition",
        transition_id,
    ]


def run_m5_verifier(command: list[str]) -> None:
    result = subprocess.run(
        command,
        check=False,
        text=True,
        capture_output=True,
        timeout=300,
    )
    verified = any(line.strip() == "VERIFIED" for line in result.stdout.splitlines())
    if result.returncode != 0 or not verified:
        raise ValueError("Existing M5 standalone verifier rejected the proof package")
