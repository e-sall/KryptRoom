"""Compute the M7 state-only commitment and refuse a duplicate publication."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engines.chain_anchor.commitment import EVIDENCE_NONE, anchor_commitment, load_verified_room_state
from engines.chain_anchor.record import assert_anchor_absent
from engines.chain_anchor.rpc import JsonRpcClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract-address", required=True)
    parser.add_argument("--deployment-block", required=True, type=int)
    parser.add_argument("--room-state", required=True)
    args = parser.parse_args()

    rpc_url = os.environ.get("BASE_SEPOLIA_RPC_URL")
    if not rpc_url:
        raise SystemExit("BASE_SEPOLIA_RPC_URL is required")
    state = load_verified_room_state(args.room_state)
    commitment = anchor_commitment(
        output_state_commitment=state.commitment.value,
        evidence_type=EVIDENCE_NONE,
    )
    assert_anchor_absent(
        rpc=JsonRpcClient(rpc_url),
        contract_address=args.contract_address,
        anchor_commitment=commitment,
        from_block=args.deployment_block,
    )
    print(commitment)


if __name__ == "__main__":
    main()
