from __future__ import annotations

import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engines.chain_anchor.model import AnchorStatus
from engines.chain_anchor.record import (
    assert_anchor_absent,
    assert_unique_anchor_inclusion,
    create_chain_anchor_record,
    wait_for_canonical_receipt,
)
from engines.chain_anchor.verifier import (
    ANCHOR_RECORDED_TOPIC,
    BASE_SEPOLIA_CHAIN_ID,
    ChainVerificationError,
)


CONTRACT = "0x" + "11" * 20
COMMITMENT = "0x" + "22" * 32
TRANSACTION = "0x" + "33" * 32
BLOCK_HASH = "0x" + "44" * 32
OTHER_BLOCK_HASH = "0x" + "55" * 32
SUBMITTER = "0x" + "66" * 20


class LogRpc:
    def __init__(self, logs, latest_block=100, canonical_hash=BLOCK_HASH):
        self.logs = logs
        self.latest_block = latest_block
        self.canonical_hash = canonical_hash
        self.calls = []

    def call(self, method, params):
        self.calls.append((method, params))
        if method == "eth_chainId":
            return hex(BASE_SEPOLIA_CHAIN_ID)
        if method == "eth_blockNumber":
            return hex(self.latest_block)
        if method == "eth_getLogs":
            return self.logs
        if method == "eth_getBlockByNumber":
            return {"hash": self.canonical_hash}
        raise AssertionError((method, params))


def mined_receipt(*, block_hash=BLOCK_HASH, block_number=100):
    return {
        "transactionHash": TRANSACTION,
        "status": "0x1",
        "to": CONTRACT,
        "blockNumber": hex(block_number),
        "blockHash": block_hash,
        "logs": [
            {
                "address": CONTRACT,
                "transactionHash": TRANSACTION,
                "blockNumber": hex(block_number),
                "blockHash": block_hash,
                "logIndex": "0x7",
                "removed": False,
                "topics": [
                    ANCHOR_RECORDED_TOPIC,
                    COMMITMENT,
                    "0x" + "00" * 12 + SUBMITTER[2:],
                ],
                "data": "0x",
            }
        ],
    }


class CanonicalRpc:
    def __init__(self, receipts, blocks, runtime="0x6000"):
        self.receipts = list(receipts)
        self.blocks = list(blocks)
        self.runtime = runtime

    @staticmethod
    def _next(values):
        if len(values) > 1:
            return values.pop(0)
        return values[0]

    def call(self, method, params):
        if method == "eth_chainId":
            return hex(BASE_SEPOLIA_CHAIN_ID)
        if method == "eth_getTransactionReceipt":
            return self._next(self.receipts)
        if method == "eth_getBlockByNumber":
            return self._next(self.blocks)
        if method == "eth_getCode":
            return self.runtime
        raise AssertionError((method, params))


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class RecoveryTests(unittest.TestCase):
    def test_absent_commitment_passes_with_exact_filter(self):
        rpc = LogRpc([])
        assert_anchor_absent(
            rpc=rpc,
            contract_address=CONTRACT,
            anchor_commitment=COMMITMENT,
            from_block=100,
        )
        self.assertEqual(
            rpc.calls[2],
            (
                "eth_getLogs",
                [{
                    "address": CONTRACT,
                    "fromBlock": "0x64",
                    "toBlock": "0x64",
                    "topics": [ANCHOR_RECORDED_TOPIC, COMMITMENT],
                }],
            ),
        )

    def test_existing_commitment_fails_closed(self):
        rpc = LogRpc([{"transactionHash": TRANSACTION}])
        with self.assertRaisesRegex(ChainVerificationError, "already recorded"):
            assert_anchor_absent(
                rpc=rpc,
                contract_address=CONTRACT,
                anchor_commitment=COMMITMENT,
                from_block=100,
            )

    def test_wrong_chain_and_malformed_log_result_fail_closed(self):
        wrong_chain = LogRpc([])
        wrong_chain.call = lambda method, params: "0x1"
        with self.assertRaisesRegex(ChainVerificationError, "Base Sepolia"):
            assert_anchor_absent(
                rpc=wrong_chain,
                contract_address=CONTRACT,
                anchor_commitment=COMMITMENT,
                from_block=100,
            )

        malformed = LogRpc({"unexpected": "object"})
        with self.assertRaisesRegex(ChainVerificationError, "malformed"):
            assert_anchor_absent(
                rpc=malformed,
                contract_address=CONTRACT,
                anchor_commitment=COMMITMENT,
                from_block=100,
            )

    def test_log_queries_are_bounded_for_public_rpc_compatibility(self):
        rpc = LogRpc([], latest_block=305)
        assert_anchor_absent(
            rpc=rpc,
            contract_address=CONTRACT,
            anchor_commitment=COMMITMENT,
            from_block=100,
        )
        ranges = [
            (params[0]["fromBlock"], params[0]["toBlock"])
            for method, params in rpc.calls
            if method == "eth_getLogs"
        ]
        self.assertEqual(ranges, [("0x64", "0xc7"), ("0xc8", "0x12b"), ("0x12c", "0x131")])

    def test_existing_anchor_requires_one_exact_canonical_inclusion(self):
        event = mined_receipt()["logs"][0]
        rpc = LogRpc([event])
        assert_unique_anchor_inclusion(
            rpc=rpc,
            contract_address=CONTRACT,
            anchor_commitment=COMMITMENT,
            transaction_hash=TRANSACTION,
            log_index=7,
            from_block=100,
        )

        with self.assertRaisesRegex(ChainVerificationError, "exactly one"):
            assert_unique_anchor_inclusion(
                rpc=LogRpc([event, deepcopy(event)]),
                contract_address=CONTRACT,
                anchor_commitment=COMMITMENT,
                transaction_hash=TRANSACTION,
                log_index=7,
                from_block=100,
            )

    def test_immediate_canonical_receipt(self):
        receipt = mined_receipt()
        block = {"hash": BLOCK_HASH, "timestamp": "0x1"}
        result_receipt, result_block = wait_for_canonical_receipt(
            rpc=CanonicalRpc([receipt], [block]),
            transaction_hash=TRANSACTION,
            timeout_seconds=0,
        )
        self.assertIs(result_receipt, receipt)
        self.assertIs(result_block, block)

    def test_temporary_hash_mismatch_then_match(self):
        receipt = mined_receipt()
        clock = FakeClock()
        result_receipt, _ = wait_for_canonical_receipt(
            rpc=CanonicalRpc(
                [receipt, receipt],
                [{"hash": OTHER_BLOCK_HASH}, {"hash": BLOCK_HASH, "timestamp": "0x1"}],
            ),
            transaction_hash=TRANSACTION,
            timeout_seconds=2,
            poll_seconds=1,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )
        self.assertIs(result_receipt, receipt)
        self.assertEqual(clock.now, 1)

    def test_missing_canonical_block_then_match(self):
        receipt = mined_receipt()
        clock = FakeClock()
        _, result_block = wait_for_canonical_receipt(
            rpc=CanonicalRpc(
                [receipt, receipt],
                [None, {"hash": BLOCK_HASH, "timestamp": "0x1"}],
            ),
            transaction_hash=TRANSACTION,
            timeout_seconds=2,
            poll_seconds=1,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )
        self.assertEqual(result_block["hash"], BLOCK_HASH)

    def test_receipt_disappearance_is_orphaned(self):
        receipt = mined_receipt()
        clock = FakeClock()
        with self.assertRaisesRegex(ChainVerificationError, "disappeared") as raised:
            wait_for_canonical_receipt(
                rpc=CanonicalRpc([receipt, None], [{"hash": OTHER_BLOCK_HASH}]),
                transaction_hash=TRANSACTION,
                timeout_seconds=2,
                poll_seconds=1,
                monotonic=clock.monotonic,
                sleep=clock.sleep,
            )
        self.assertIs(raised.exception.status, AnchorStatus.ORPHANED)

    def test_permanent_hash_mismatch_times_out_as_orphaned(self):
        receipt = mined_receipt()
        clock = FakeClock()
        with self.assertRaisesRegex(ChainVerificationError, "Timed out") as raised:
            wait_for_canonical_receipt(
                rpc=CanonicalRpc([receipt], [{"hash": OTHER_BLOCK_HASH}]),
                transaction_hash=TRANSACTION,
                timeout_seconds=2,
                poll_seconds=1,
                monotonic=clock.monotonic,
                sleep=clock.sleep,
            )
        self.assertIs(raised.exception.status, AnchorStatus.ORPHANED)

    def test_incompatible_receipt_change_is_orphaned(self):
        first = mined_receipt()
        second = mined_receipt(block_hash=OTHER_BLOCK_HASH, block_number=101)
        clock = FakeClock()
        with self.assertRaisesRegex(ChainVerificationError, "incompatible") as raised:
            wait_for_canonical_receipt(
                rpc=CanonicalRpc([first, second], [{"hash": OTHER_BLOCK_HASH}]),
                transaction_hash=TRANSACTION,
                timeout_seconds=2,
                poll_seconds=1,
                monotonic=clock.monotonic,
                sleep=clock.sleep,
            )
        self.assertIs(raised.exception.status, AnchorStatus.ORPHANED)

    @patch("engines.chain_anchor.record.verify_chain_layer")
    def test_event_and_runtime_validation_remain_strict(self, verify_chain_layer):
        block = {"hash": BLOCK_HASH, "timestamp": "0x1"}
        anchor = create_chain_anchor_record(
            rpc=CanonicalRpc([mined_receipt()], [block]),
            anchor_commitment=COMMITMENT,
            subject_commitment="77" * 32,
            evidence_type="NONE",
            evidence_commitment="00" * 32,
            room_id="room-test",
            transition_id="transition-test",
            output_state_id="state-test",
            contract_address=CONTRACT,
            transaction_hash=TRANSACTION,
            log_index=7,
            created_at="2026-10-20T00:00:00Z",
            canonical_timeout_seconds=0,
        )
        self.assertEqual(anchor.contract_address, CONTRACT)
        verify_chain_layer.assert_called_once()

        wrong_event = mined_receipt()
        wrong_event["logs"][0]["topics"][1] = "0x" + "99" * 32
        with self.assertRaisesRegex(ChainVerificationError, "expected AnchorRecorded"):
            create_chain_anchor_record(
                rpc=CanonicalRpc([wrong_event], [block]),
                anchor_commitment=COMMITMENT,
                subject_commitment="77" * 32,
                evidence_type="NONE",
                evidence_commitment="00" * 32,
                room_id="room-test",
                transition_id="transition-test",
                output_state_id="state-test",
                contract_address=CONTRACT,
                transaction_hash=TRANSACTION,
                log_index=7,
                created_at="2026-10-20T00:00:00Z",
                canonical_timeout_seconds=0,
            )

        with self.assertRaisesRegex(ChainVerificationError, "runtime bytecode is missing"):
            create_chain_anchor_record(
                rpc=CanonicalRpc([mined_receipt()], [block], runtime="0x"),
                anchor_commitment=COMMITMENT,
                subject_commitment="77" * 32,
                evidence_type="NONE",
                evidence_commitment="00" * 32,
                room_id="room-test",
                transition_id="transition-test",
                output_state_id="state-test",
                contract_address=CONTRACT,
                transaction_hash=TRANSACTION,
                log_index=7,
                created_at="2026-10-20T00:00:00Z",
                canonical_timeout_seconds=0,
            )


if __name__ == "__main__":
    unittest.main()
