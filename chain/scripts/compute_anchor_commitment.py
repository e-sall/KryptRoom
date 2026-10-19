"""Compute one exact M7 commitment from verified off-chain metadata."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engines.chain_anchor.commitment import (
    EVIDENCE_NONE,
    EVIDENCE_STATE_PROOF_V1,
    anchor_commitment,
    load_verified_room_state,
    state_proof_document_commitment,
    strict_json_load,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute exact M7 AnchorCommitment")
    parser.add_argument("--room-state", required=True)
    parser.add_argument("--state-proof")
    args = parser.parse_args()
    state = load_verified_room_state(args.room_state)
    if args.state_proof:
        proof_commitment = state_proof_document_commitment(strict_json_load(args.state_proof))
        commitment = anchor_commitment(
            output_state_commitment=state.commitment.value,
            evidence_type=EVIDENCE_STATE_PROOF_V1,
            evidence_commitment=proof_commitment,
        )
    else:
        commitment = anchor_commitment(
            output_state_commitment=state.commitment.value,
            evidence_type=EVIDENCE_NONE,
        )
    print(commitment)


if __name__ == "__main__":
    main()
