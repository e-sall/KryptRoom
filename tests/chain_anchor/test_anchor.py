from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.chain_anchor.commitment import (
    ANCHOR_DOMAIN,
    EVIDENCE_NONE,
    EVIDENCE_STATE_PROOF_V1,
    STATE_PROOF_DOCUMENT_DOMAIN,
    ZERO32,
    CommitmentError,
    anchor_commitment,
    state_proof_document_commitment,
    strict_json_load,
)
from engines.chain_anchor.model import AnchorStatus, ChainAnchor, derive_anchor_id
from engines.chain_anchor.verifier import (
    ANCHOR_RECORDED_TOPIC,
    BASE_SEPOLIA_CHAIN_ID,
    ChainVerificationError,
    keccak256,
    m5_verifier_command,
    verify_chain_layer,
    verify_package_layer,
)
from engines.mpc.room_state import canonical_json
from vector_builder import build_vectors, representative_state_proof


CONTRACT = "0x" + "11" * 20
SUBMITTER = "0x" + "22" * 20
TRANSACTION = "0x" + "33" * 32
BLOCK_HASH = "0x" + "44" * 32
BLOCK_101_HASH = "0x" + "55" * 32
FINALIZED_HASH = "0x" + "66" * 32
RUNTIME = bytes.fromhex("6080604052600080fd")
RUNTIME_HASH = "0x" + keccak256(RUNTIME).hex()
OBSERVED_AT = "2026-10-19T05:00:00Z"


def fixture(name: str):
    return strict_json_load(ROOT / "tests/state_proof/fixtures" / name)


class FakeRpc:
    def __init__(self, anchor: ChainAnchor):
        topic_submitter = "0x" + (bytes(12) + bytes.fromhex(SUBMITTER[2:])).hex()
        self.receipt = {
            "transactionHash": TRANSACTION,
            "to": CONTRACT,
            "status": "0x1",
            "blockNumber": hex(anchor.block_number),
            "blockHash": BLOCK_HASH,
            "logs": [
                {
                    "address": CONTRACT,
                    "logIndex": hex(anchor.log_index),
                    "transactionHash": TRANSACTION,
                    "blockNumber": hex(anchor.block_number),
                    "blockHash": BLOCK_HASH,
                    "topics": [ANCHOR_RECORDED_TOPIC, anchor.anchor_commitment, topic_submitter],
                    "data": "0x",
                    "removed": False,
                }
            ],
        }
        self.blocks = {
            BLOCK_HASH: {
                "number": "0x64",
                "hash": BLOCK_HASH,
                "parentHash": "0x" + "77" * 32,
                "timestamp": "0x69043440"
            },
            BLOCK_101_HASH: {
                "number": "0x65",
                "hash": BLOCK_101_HASH,
                "parentHash": BLOCK_HASH,
                "timestamp": "0x69043442"
            },
            FINALIZED_HASH: {
                "number": "0x66",
                "hash": FINALIZED_HASH,
                "parentHash": BLOCK_101_HASH,
                "timestamp": "0x69043444"
            },
        }
        self.finalized = self.blocks[FINALIZED_HASH]
        self.safe = self.blocks[FINALIZED_HASH]
        self.code = "0x" + RUNTIME.hex()

    def call(self, method, params):
        if method == "eth_chainId":
            return hex(BASE_SEPOLIA_CHAIN_ID)
        if method == "eth_getTransactionReceipt":
            return self.receipt if params[0] == TRANSACTION else None
        if method == "eth_getBlockByNumber":
            if params[0] == "finalized":
                return self.finalized
            if params[0] == "safe":
                return self.safe
            if params[0] == "0x64":
                return self.blocks[BLOCK_HASH]
            return None
        if method == "eth_getBlockByHash":
            return self.blocks.get(params[0])
        if method == "eth_getCode":
            return self.code
        raise AssertionError((method, params))


def make_anchor(state: dict, proof: dict | None) -> ChainAnchor:
    if proof is None:
        evidence_type = "NONE"
        evidence_number = EVIDENCE_NONE
        evidence_commitment = ZERO32.hex()
    else:
        evidence_type = "STATE_PROOF_V1"
        evidence_number = EVIDENCE_STATE_PROOF_V1
        evidence_commitment = state_proof_document_commitment(proof)
    commitment = anchor_commitment(
        output_state_commitment=state["commitment"]["value"],
        evidence_type=evidence_number,
        evidence_commitment=evidence_commitment,
    )
    return ChainAnchor(
        version="1",
        anchor_id=derive_anchor_id(
            chain_id=BASE_SEPOLIA_CHAIN_ID,
            contract_address=CONTRACT,
            transaction_hash=TRANSACTION,
            log_index=7,
        ),
        anchor_commitment=commitment,
        subject_type="ROOM_STATE_V1",
        subject_commitment=state["commitment"]["value"],
        evidence_type=evidence_type,
        evidence_commitment=evidence_commitment,
        room_id=state["roomId"],
        transition_id=state["transition"]["id"],
        output_state_id=state["id"],
        backend="base-op-stack",
        chain_id=BASE_SEPOLIA_CHAIN_ID,
        contract_address=CONTRACT,
        contract_runtime_code_hash=RUNTIME_HASH,
        transaction_hash=TRANSACTION,
        log_index=7,
        submitter=SUBMITTER,
        block_number=100,
        block_hash=BLOCK_HASH,
        block_timestamp="2025-10-31T04:00:00Z",
        created_at="2026-10-19T04:59:00Z",
    )


class CommitmentTests(unittest.TestCase):
    def setUp(self):
        self.state = fixture("S4_eval.json")
        self.proof = representative_state_proof(self.state)

    def test_exact_anchor_formula_without_evidence(self):
        state_hash = self.state["commitment"]["value"]
        manual = hashlib.sha256(
            ANCHOR_DOMAIN
            + b"\x00\x01"
            + bytes.fromhex(state_hash)
            + b"\x00"
            + ZERO32
        ).hexdigest()
        self.assertEqual(
            anchor_commitment(output_state_commitment=state_hash, evidence_type=EVIDENCE_NONE),
            "0x" + manual,
        )

    def test_exact_state_proof_document_formula_and_canonical_order(self):
        expected = hashlib.sha256(
            STATE_PROOF_DOCUMENT_DOMAIN + b"\x00" + canonical_json(self.proof)
        ).hexdigest()
        self.assertEqual(state_proof_document_commitment(self.proof), expected)
        reordered = dict(reversed(list(self.proof.items())))
        self.assertEqual(state_proof_document_commitment(reordered), expected)

    def test_exact_anchor_formula_with_state_proof(self):
        evidence = state_proof_document_commitment(self.proof)
        manual = hashlib.sha256(
            ANCHOR_DOMAIN
            + b"\x00\x01"
            + bytes.fromhex(self.state["commitment"]["value"])
            + b"\x01"
            + bytes.fromhex(evidence)
        ).hexdigest()
        self.assertEqual(
            anchor_commitment(
                output_state_commitment=self.state["commitment"]["value"],
                evidence_type=EVIDENCE_STATE_PROOF_V1,
                evidence_commitment=evidence,
            ),
            "0x" + manual,
        )

    def test_wrong_evidence_contract_rejected(self):
        with self.assertRaises(CommitmentError):
            anchor_commitment(
                output_state_commitment=self.state["commitment"]["value"],
                evidence_type=EVIDENCE_NONE,
                evidence_commitment="11" * 32,
            )
        with self.assertRaises(CommitmentError):
            anchor_commitment(
                output_state_commitment=self.state["commitment"]["value"],
                evidence_type=9,
            )

    def test_committed_vectors_reproduce_exactly(self):
        proof, vectors = build_vectors()
        self.assertEqual(proof, strict_json_load(ROOT / "tests/chain_anchor/fixtures/state-proof.json"))
        self.assertEqual(vectors, strict_json_load(ROOT / "tests/chain_anchor/fixtures/vectors.json"))

    def test_anchor_id_fixed_width_binding(self):
        first = derive_anchor_id(
            chain_id=84532,
            contract_address=CONTRACT,
            transaction_hash=TRANSACTION,
            log_index=7,
        )
        second = derive_anchor_id(
            chain_id=84532,
            contract_address=CONTRACT,
            transaction_hash="0x" + "34" * 32,
            log_index=7,
        )
        self.assertNotEqual(first, second)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.state = fixture("S4_eval.json")
        self.proof = representative_state_proof(self.state)

    def test_state_with_proof_matches_but_does_not_claim_sp1_validation(self):
        anchor = make_anchor(self.state, self.proof)
        result = verify_package_layer(anchor, self.state, self.proof)
        self.assertTrue(result.m5_proof_validation_required)

    def test_state_only_anchor_does_not_resolve_artifact_uris(self):
        anchor = make_anchor(self.state, None)
        result = verify_package_layer(anchor, self.state, None)
        self.assertFalse(result.m5_proof_validation_required)

    def test_wrong_state_commitment_and_mutated_state_rejected(self):
        anchor = make_anchor(self.state, None)
        wrong_anchor = replace(anchor, subject_commitment="00" * 32)
        with self.assertRaisesRegex(ValueError, "RoomState commitment"):
            verify_package_layer(wrong_anchor, self.state, None)
        mutated = copy.deepcopy(self.state)
        mutated["roomId"] = "other-room"
        with self.assertRaisesRegex(ValueError, "commitment verification"):
            verify_package_layer(anchor, mutated, None)

    def test_wrong_state_proof_document_and_evidence_commitment_rejected(self):
        anchor = make_anchor(self.state, self.proof)
        mutated = copy.deepcopy(self.proof)
        mutated["createdAt"] = "2026-10-19T04:31:51Z"
        with self.assertRaisesRegex(ValueError, "Evidence commitment"):
            verify_package_layer(anchor, self.state, mutated)
        wrong = replace(anchor, evidence_commitment="00" * 32)
        with self.assertRaisesRegex(ValueError, "Evidence commitment"):
            verify_package_layer(wrong, self.state, self.proof)

    def test_wrong_evidence_type_rejected(self):
        state_only = make_anchor(self.state, None)
        with self.assertRaisesRegex(ValueError, "cannot receive"):
            verify_package_layer(state_only, self.state, self.proof)
        proof_anchor = make_anchor(self.state, self.proof)
        with self.assertRaisesRegex(ValueError, "requires"):
            verify_package_layer(proof_anchor, self.state, None)

    def test_layer_c_command_is_explicit_and_separate(self):
        command = m5_verifier_command(
            verifier="kryptroom-proof",
            receipt="receipt.json",
            state_proof="state-proof.json",
            proof="proof.bin",
            room_id=self.state["roomId"],
            transition_id=self.state["transition"]["id"],
        )
        self.assertEqual(command[1], "verify")
        self.assertIn("--proof", command)
        self.assertIn("--expect-transition", command)


class ChainTests(unittest.TestCase):
    def setUp(self):
        self.state = fixture("S4_eval.json")
        self.anchor = make_anchor(self.state, None)
        self.rpc = FakeRpc(self.anchor)

    def verify(self, anchor=None, rpc=None, require_finalized=True):
        return verify_chain_layer(
            anchor or self.anchor,
            rpc or self.rpc,
            expected_contract_address=CONTRACT,
            expected_runtime_code_hash=RUNTIME_HASH,
            require_finalized=require_finalized,
            observed_at=OBSERVED_AT,
        )

    def test_finalized_chain_event_and_runtime_pass(self):
        self.assertEqual(self.verify().status, AnchorStatus.FINALIZED)

    def test_wrong_chain_id(self):
        changed = replace(self.anchor, chain_id=8453)
        changed = replace(
            changed,
            anchor_id=derive_anchor_id(
                chain_id=8453,
                contract_address=CONTRACT,
                transaction_hash=TRANSACTION,
                log_index=7,
            ),
        )
        with self.assertRaisesRegex(ChainVerificationError, "wrong chainId"):
            self.verify(anchor=changed)

    def test_wrong_contract_address(self):
        other = "0x" + "12" * 20
        changed = replace(self.anchor, contract_address=other)
        changed = replace(
            changed,
            anchor_id=derive_anchor_id(
                chain_id=84532,
                contract_address=other,
                transaction_hash=TRANSACTION,
                log_index=7,
            ),
        )
        with self.assertRaisesRegex(ChainVerificationError, "wrong contract"):
            self.verify(anchor=changed)

    def test_wrong_runtime_bytecode(self):
        self.rpc.code = "0x6001"
        with self.assertRaisesRegex(ChainVerificationError, "Runtime bytecode"):
            self.verify()

    def test_anchor_runtime_hash_must_match_trusted_deployment_manifest(self):
        changed = replace(self.anchor, contract_runtime_code_hash="0x" + "99" * 32)
        with self.assertRaisesRegex(ChainVerificationError, "deployment manifest"):
            self.verify(anchor=changed)

    def test_wrong_transaction_hash(self):
        other_tx = "0x" + "35" * 32
        changed = replace(self.anchor, transaction_hash=other_tx)
        changed = replace(
            changed,
            anchor_id=derive_anchor_id(
                chain_id=84532,
                contract_address=CONTRACT,
                transaction_hash=other_tx,
                log_index=7,
            ),
        )
        with self.assertRaisesRegex(ChainVerificationError, "disappeared"):
            self.verify(anchor=changed)

    def test_wrong_log_index_and_missing_event(self):
        changed = replace(self.anchor, log_index=8)
        changed = replace(
            changed,
            anchor_id=derive_anchor_id(
                chain_id=84532,
                contract_address=CONTRACT,
                transaction_hash=TRANSACTION,
                log_index=8,
            ),
        )
        with self.assertRaisesRegex(ChainVerificationError, "missing"):
            self.verify(anchor=changed)
        self.rpc.receipt["logs"] = []
        with self.assertRaisesRegex(ChainVerificationError, "missing"):
            self.verify()

    def test_wrong_block_hash_and_orphaned_inclusion(self):
        changed = replace(self.anchor, block_hash="0x" + "99" * 32)
        with self.assertRaises(ChainVerificationError) as result:
            self.verify(anchor=changed)
        self.assertEqual(result.exception.status, AnchorStatus.ORPHANED)
        self.rpc.receipt["logs"][0]["removed"] = True
        with self.assertRaises(ChainVerificationError) as removed:
            self.verify()
        self.assertEqual(removed.exception.status, AnchorStatus.ORPHANED)

    def test_failed_transaction(self):
        self.rpc.receipt["status"] = "0x0"
        with self.assertRaises(ChainVerificationError) as result:
            self.verify()
        self.assertEqual(result.exception.status, AnchorStatus.FAILED)

    def test_nonfinalized_inclusion_rejected_when_required(self):
        self.rpc.finalized = {
            "number": "0x63",
            "hash": "0x" + "aa" * 32,
            "parentHash": "0x" + "bb" * 32,
            "timestamp": "0x6904343e",
        }
        self.rpc.safe = self.rpc.blocks[BLOCK_101_HASH]
        self.assertEqual(self.verify(require_finalized=False).status, AnchorStatus.CONFIRMED)
        with self.assertRaises(ChainVerificationError) as result:
            self.verify(require_finalized=True)
        self.assertEqual(result.exception.status, AnchorStatus.CONFIRMED)

    def test_wrong_anchor_commitment_event(self):
        self.rpc.receipt["logs"][0]["topics"][1] = "0x" + "00" * 32
        with self.assertRaisesRegex(ChainVerificationError, "commitment mismatch"):
            self.verify()

    def test_duplicate_commitment_gets_distinct_anchor_id(self):
        first = self.anchor.anchor_id
        second = derive_anchor_id(
            chain_id=84532,
            contract_address=CONTRACT,
            transaction_hash="0x" + "ab" * 32,
            log_index=0,
        )
        self.assertNotEqual(first, second)


class SchemaTests(unittest.TestCase):
    def test_chain_anchor_and_status_schemas(self):
        state = fixture("S4_eval.json")
        anchor = make_anchor(state, None)
        for name, value in (
            ("chain-anchor.schema.json", anchor.to_dict()),
            (
                "chain-anchor-status.schema.json",
                {
                    "anchorId": anchor.anchor_id,
                    "status": "FINALIZED",
                    "observedAt": OBSERVED_AT,
                    "detail": "verified",
                },
            ),
        ):
            schema = strict_json_load(ROOT / "packages/manifests" / name)
            Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)

    def test_deployment_manifest_schema(self):
        value = {
            "version": "1",
            "chainId": BASE_SEPOLIA_CHAIN_ID,
            "contractAddress": CONTRACT,
            "deploymentTransactionHash": TRANSACTION,
            "deploymentBlockNumber": 100,
            "runtimeBytecodeHash": RUNTIME_HASH,
            "solidityVersion": "0.8.37",
            "foundryVersion": "1.8.5",
            "deployedAt": "2025-10-31T04:00:00Z",
        }
        schema = strict_json_load(
            ROOT / "packages/manifests/public-chain-deployment.schema.json"
        )
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)


if __name__ == "__main__":
    unittest.main()
