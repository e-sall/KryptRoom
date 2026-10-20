"""Deterministic public M7 vectors derived from existing metadata fixtures."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engines.chain_anchor.commitment import (
    EVIDENCE_NONE,
    EVIDENCE_STATE_PROOF_V1,
    ZERO32,
    anchor_commitment,
    state_proof_document_commitment,
)
from engines.mpc.room_state import canonical_json


def load_fixture(name: str):
    return json.loads((ROOT / "tests/state_proof/fixtures" / name).read_text())


def representative_state_proof(state: dict, *, created_at="2026-10-19T04:31:50Z"):
    receipt = load_fixture("receipt.json")
    receipt_hash = hashlib.sha256(
        b"KRYPTROOM-TRANSITION-RECEIPT-V1\x00" + canonical_json(receipt)
    ).hexdigest()
    public_claim = hashlib.sha256(b"KRYPTROOM-STATE-PROOF-V1").digest() + bytes.fromhex(
        receipt_hash
    )
    proof_hash = "bfc8784ddcde6af464fecb02da33dc12642f804c28bbaa2ecca9eca37a9608bc"
    program_vkey = "0x003eba0b114a21d954c4714393c0eedf6833406b8e9b6b70ae828b3a466ea2e3"
    proof_id_material = (
        b"KRYPTROOM-STATE-PROOF-ID-V1\x00"
        + bytes.fromhex(receipt_hash)
        + bytes.fromhex(program_vkey[2:])
        + bytes.fromhex(proof_hash)
    )
    proof_id = "stateproof-" + hashlib.sha256(proof_id_material).hexdigest()[:32]
    return {
        "version": "1",
        "proofId": proof_id,
        "proofSystem": "sp1-groth16",
        "proofSystemVersion": "6.9.0",
        "programVersion": "kryptroom-m5-evaluation-v1",
        "roomId": state["roomId"],
        "transitionId": state["transition"]["id"],
        "transitionCommitment": receipt["transitionCommitment"],
        "outputStateId": state["id"],
        "outputStateCommitment": state["commitment"]["value"],
        "receiptHash": receipt_hash,
        "programVKey": program_vkey,
        "elfSha256": "e6e06afd460d31db211d3eff84c031b14ebb2019b71256b651e6932e4e9c4c03",
        "publicValuesSha256": hashlib.sha256(public_claim).hexdigest(),
        "proofArtifact": {
            "mediaType": "application/vnd.kryptroom.sp1-groth16-proof",
            "uri": f"proofs/rooms/{state['roomId']}/transitions/{state['transition']['id']}/{proof_id}/proof.bin",
            "sha256": proof_hash,
            "sizeBytes": 1758,
        },
        "createdAt": created_at,
    }


def build_vectors() -> tuple[dict, dict]:
    state = load_fixture("S4_eval.json")
    proof = representative_state_proof(state)
    evidence = state_proof_document_commitment(proof)
    vectors = {
        "version": "1",
        "subjectType": "ROOM_STATE_V1",
        "subjectCommitment": state["commitment"]["value"],
        "stateProofDocumentCommitment": evidence,
        "stateOnlyEvidenceCommitment": ZERO32.hex(),
        "stateOnlyAnchorCommitment": anchor_commitment(
            output_state_commitment=state["commitment"]["value"],
            evidence_type=EVIDENCE_NONE,
        ),
        "stateProofAnchorCommitment": anchor_commitment(
            output_state_commitment=state["commitment"]["value"],
            evidence_type=EVIDENCE_STATE_PROOF_V1,
            evidence_commitment=evidence,
        ),
    }
    return proof, vectors
