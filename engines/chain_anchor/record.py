"""Build an immutable ChainAnchor from one successful public-chain inclusion."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Callable

from engines.chain_anchor.model import AnchorStatus, ChainAnchor, derive_anchor_id
from engines.chain_anchor.rpc import RpcClient
from engines.chain_anchor.verifier import (
    ANCHOR_RECORDED_TOPIC,
    BASE_SEPOLIA_CHAIN_ID,
    ChainVerificationError,
    keccak256,
    verify_chain_layer,
)


def _quantity(value: str, name: str) -> int:
    try:
        return int(value, 16)
    except (TypeError, ValueError) as error:
        raise ChainVerificationError(f"Malformed {name}") from error


def _iso_timestamp(value: str) -> str:
    return (
        datetime.fromtimestamp(_quantity(value, "block timestamp"), timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _matching_anchor_logs(
    *,
    rpc: RpcClient,
    contract_address: str,
    anchor_commitment: str,
    from_block: int,
) -> list[dict[str, Any]]:
    chain_id = _quantity(rpc.call("eth_chainId", []), "chainId")
    if chain_id != BASE_SEPOLIA_CHAIN_ID:
        raise ChainVerificationError("Authoritative M7 deployment must use Base Sepolia")
    latest_block = _quantity(rpc.call("eth_blockNumber", []), "latest block number")
    if from_block < 0 or latest_block < from_block:
        raise ChainVerificationError("Deployment block is ahead of the current chain head")

    matching: list[dict[str, Any]] = []
    for first in range(from_block, latest_block + 1, 100):
        last = min(first + 99, latest_block)
        logs = rpc.call(
            "eth_getLogs",
            [
                {
                    "address": contract_address.lower(),
                    "fromBlock": hex(first),
                    "toBlock": hex(last),
                    "topics": [ANCHOR_RECORDED_TOPIC, anchor_commitment.lower()],
                }
            ],
        )
        if not isinstance(logs, list) or any(not isinstance(entry, dict) for entry in logs):
            raise ChainVerificationError("RPC returned malformed AnchorRecorded logs")
        matching.extend(logs)
    return matching


def assert_anchor_absent(
    *,
    rpc: RpcClient,
    contract_address: str,
    anchor_commitment: str,
    from_block: int,
) -> None:
    """Fail closed if this contract already emitted the exact commitment."""

    if _matching_anchor_logs(
        rpc=rpc,
        contract_address=contract_address,
        anchor_commitment=anchor_commitment,
        from_block=from_block,
    ):
        raise ChainVerificationError(
            "This AnchorCommitment is already recorded; refusing a duplicate transaction"
        )


def assert_unique_anchor_inclusion(
    *,
    rpc: RpcClient,
    contract_address: str,
    anchor_commitment: str,
    transaction_hash: str,
    log_index: int,
    from_block: int,
) -> None:
    """Require exactly one canonical event and bind it to the supplied inclusion."""

    logs = _matching_anchor_logs(
        rpc=rpc,
        contract_address=contract_address,
        anchor_commitment=anchor_commitment,
        from_block=from_block,
    )
    if len(logs) != 1:
        raise ChainVerificationError(
            f"Expected exactly one canonical AnchorRecorded event; found {len(logs)}"
        )
    entry = logs[0]
    if entry.get("removed") is True:
        raise ChainVerificationError(
            "Anchor event was removed by a reorg", AnchorStatus.ORPHANED
        )
    if (
        entry.get("address", "").lower() != contract_address.lower()
        or entry.get("transactionHash", "").lower() != transaction_hash.lower()
        or _quantity(entry.get("logIndex"), "logIndex") != log_index
    ):
        raise ChainVerificationError("Canonical anchor event does not match the supplied inclusion")
    block_number = _quantity(entry.get("blockNumber"), "event block number")
    block_hash = entry.get("blockHash", "").lower()
    canonical = rpc.call("eth_getBlockByNumber", [hex(block_number), False])
    if canonical is None or canonical.get("hash", "").lower() != block_hash:
        raise ChainVerificationError(
            "Anchor event is not in the canonical block", AnchorStatus.ORPHANED
        )


def wait_for_canonical_receipt(
    *,
    rpc: RpcClient,
    transaction_hash: str,
    timeout_seconds: float = 300,
    poll_seconds: float = 5,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Wait for one stable receipt whose block hash is the canonical hash at its height."""

    if timeout_seconds < 0 or poll_seconds <= 0:
        raise ValueError("Canonical receipt timeout must be nonnegative and polling positive")
    deadline = monotonic() + timeout_seconds
    observed_inclusion: tuple[int, str] | None = None
    while True:
        receipt = rpc.call("eth_getTransactionReceipt", [transaction_hash])
        if receipt is None:
            if observed_inclusion is not None:
                raise ChainVerificationError(
                    "Transaction receipt disappeared after inclusion was observed",
                    AnchorStatus.ORPHANED,
                )
        elif not isinstance(receipt, dict):
            raise ChainVerificationError("RPC returned a malformed transaction receipt")
        else:
            if receipt.get("transactionHash", "").lower() != transaction_hash.lower():
                raise ChainVerificationError("Transaction hash mismatch")
            block_number = _quantity(receipt.get("blockNumber"), "receipt block number")
            block_hash = receipt.get("blockHash", "").lower()
            if not block_hash.startswith("0x") or len(block_hash) != 66:
                raise ChainVerificationError("Malformed receipt block hash")
            inclusion = (block_number, block_hash)
            if observed_inclusion is None:
                observed_inclusion = inclusion
            elif inclusion != observed_inclusion:
                raise ChainVerificationError(
                    "Transaction receipt changed to an incompatible inclusion",
                    AnchorStatus.ORPHANED,
                )
            canonical = rpc.call("eth_getBlockByNumber", [hex(block_number), False])
            if canonical is not None and canonical.get("hash", "").lower() == block_hash:
                return receipt, canonical

        if monotonic() >= deadline:
            status = AnchorStatus.ORPHANED if observed_inclusion else AnchorStatus.PENDING
            raise ChainVerificationError(
                "Timed out waiting for a stable canonical transaction receipt", status
            )
        sleep(poll_seconds)


def create_chain_anchor_record(
    *,
    rpc: RpcClient,
    anchor_commitment: str,
    subject_commitment: str,
    evidence_type: str,
    evidence_commitment: str,
    room_id: str,
    transition_id: str,
    output_state_id: str,
    contract_address: str,
    transaction_hash: str,
    log_index: int,
    created_at: str,
    canonical_timeout_seconds: float = 300,
    canonical_poll_seconds: float = 5,
) -> ChainAnchor:
    """Record one exact inclusion; dynamic finality remains a separate snapshot."""

    chain_id = _quantity(rpc.call("eth_chainId", []), "chainId")
    if chain_id != BASE_SEPOLIA_CHAIN_ID:
        raise ChainVerificationError("Authoritative M7 deployment must use Base Sepolia")
    receipt, block = wait_for_canonical_receipt(
        rpc=rpc,
        transaction_hash=transaction_hash,
        timeout_seconds=canonical_timeout_seconds,
        poll_seconds=canonical_poll_seconds,
    )
    if _quantity(receipt.get("status", "0x0"), "receipt status") != 1:
        raise ChainVerificationError("Cannot record a missing or failed transaction")
    if receipt.get("to", "").lower() != contract_address.lower():
        raise ChainVerificationError("Anchor transaction targeted the wrong contract")
    candidates = [
        entry
        for entry in receipt.get("logs", [])
        if _quantity(entry.get("logIndex"), "logIndex") == log_index
    ]
    if len(candidates) != 1:
        raise ChainVerificationError("Cannot record a missing or ambiguous event")
    entry = candidates[0]
    topics = entry.get("topics", [])
    if (
        entry.get("address", "").lower() != contract_address.lower()
        or len(topics) != 3
        or topics[0].lower() != ANCHOR_RECORDED_TOPIC
        or topics[1].lower() != anchor_commitment.lower()
        or entry.get("data", "0x") != "0x"
    ):
        raise ChainVerificationError("Receipt does not contain the expected AnchorRecorded event")
    submitter_word = topics[2].removeprefix("0x")
    if len(submitter_word) != 64 or submitter_word[:24] != "0" * 24:
        raise ChainVerificationError("AnchorRecorded submitter topic is malformed")
    submitter = "0x" + submitter_word[24:]
    block_number = _quantity(receipt["blockNumber"], "block number")
    block_hash = receipt["blockHash"].lower()
    runtime = rpc.call("eth_getCode", [contract_address, hex(block_number)])
    runtime_bytes = bytes.fromhex(runtime.removeprefix("0x"))
    if not runtime_bytes:
        raise ChainVerificationError("Anchor contract runtime bytecode is missing")

    normalized_contract = contract_address.lower()
    normalized_tx = transaction_hash.lower()
    anchor = ChainAnchor(
        version="1",
        anchor_id=derive_anchor_id(
            chain_id=chain_id,
            contract_address=normalized_contract,
            transaction_hash=normalized_tx,
            log_index=log_index,
        ),
        anchor_commitment=anchor_commitment.lower(),
        subject_type="ROOM_STATE_V1",
        subject_commitment=subject_commitment,
        evidence_type=evidence_type,
        evidence_commitment=evidence_commitment,
        room_id=room_id,
        transition_id=transition_id,
        output_state_id=output_state_id,
        backend="base-op-stack",
        chain_id=chain_id,
        contract_address=normalized_contract,
        contract_runtime_code_hash="0x" + keccak256(runtime_bytes).hex(),
        transaction_hash=normalized_tx,
        log_index=log_index,
        submitter=submitter,
        block_number=block_number,
        block_hash=block_hash,
        block_timestamp=_iso_timestamp(block["timestamp"]),
        created_at=created_at,
    )
    anchor.verify_identity()
    verify_chain_layer(
        anchor,
        rpc,
        expected_contract_address=normalized_contract,
        expected_runtime_code_hash=anchor.contract_runtime_code_hash,
        require_finalized=False,
        observed_at=created_at,
    )
    return anchor
