from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engines.chain_anchor.record import assert_anchor_absent
from engines.chain_anchor.verifier import (
    ANCHOR_RECORDED_TOPIC,
    BASE_SEPOLIA_CHAIN_ID,
    ChainVerificationError,
)


CONTRACT = "0x" + "11" * 20
COMMITMENT = "0x" + "22" * 32
TRANSACTION = "0x" + "33" * 32


class LogRpc:
    def __init__(self, logs, latest_block=100):
        self.logs = logs
        self.latest_block = latest_block
        self.calls = []

    def call(self, method, params):
        self.calls.append((method, params))
        if method == "eth_chainId":
            return hex(BASE_SEPOLIA_CHAIN_ID)
        if method == "eth_blockNumber":
            return hex(self.latest_block)
        if method == "eth_getLogs":
            return self.logs
        raise AssertionError((method, params))


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


if __name__ == "__main__":
    unittest.main()
