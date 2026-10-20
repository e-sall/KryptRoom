"""Persist one immutable ChainAnchor from an already-mined transaction."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engines.chain_anchor.commitment import (
    EVIDENCE_NONE,
    EVIDENCE_STATE_PROOF_V1,
    ZERO32,
    anchor_commitment,
    load_verified_room_state,
    state_proof_document_commitment,
    strict_json_load,
)
from engines.chain_anchor.record import (
    assert_unique_anchor_inclusion,
    create_chain_anchor_record,
)
from engines.chain_anchor.rpc import JsonRpcClient
from engines.mpc.room_state import canonical_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract-address", required=True)
    parser.add_argument("--transaction-hash", required=True)
    parser.add_argument("--log-index", required=True, type=int)
    parser.add_argument("--room-state", required=True)
    parser.add_argument("--state-proof")
    parser.add_argument("--deployment-manifest", required=True)
    parser.add_argument("--canonical-timeout-seconds", type=float, default=300)
    parser.add_argument("--canonical-poll-seconds", type=float, default=5)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rpc_url = os.environ.get("BASE_SEPOLIA_RPC_URL")
    if not rpc_url:
        raise SystemExit("BASE_SEPOLIA_RPC_URL is required")

    state = load_verified_room_state(args.room_state)
    if args.state_proof:
        proof = strict_json_load(args.state_proof)
        evidence_type = "STATE_PROOF_V1"
        evidence_number = EVIDENCE_STATE_PROOF_V1
        evidence_commitment = state_proof_document_commitment(proof)
    else:
        evidence_type = "NONE"
        evidence_number = EVIDENCE_NONE
        evidence_commitment = ZERO32.hex()
    commitment = anchor_commitment(
        output_state_commitment=state.commitment.value,
        evidence_type=evidence_number,
        evidence_commitment=evidence_commitment,
    )
    deployment = strict_json_load(args.deployment_manifest)
    if deployment.get("contractAddress", "").lower() != args.contract_address.lower():
        raise SystemExit("Deployment manifest contract does not match the requested anchor")
    deployment_block = deployment.get("deploymentBlockNumber")
    if not isinstance(deployment_block, int) or deployment_block < 0:
        raise SystemExit("Deployment manifest has an invalid deployment block")
    rpc = JsonRpcClient(rpc_url)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    anchor = create_chain_anchor_record(
        rpc=rpc,
        anchor_commitment=commitment,
        subject_commitment=state.commitment.value,
        evidence_type=evidence_type,
        evidence_commitment=evidence_commitment,
        room_id=state.room_id,
        transition_id=state.transition.id,
        output_state_id=state.id,
        contract_address=args.contract_address,
        transaction_hash=args.transaction_hash,
        log_index=args.log_index,
        created_at=now,
        canonical_timeout_seconds=args.canonical_timeout_seconds,
        canonical_poll_seconds=args.canonical_poll_seconds,
    )
    assert_unique_anchor_inclusion(
        rpc=rpc,
        contract_address=args.contract_address,
        anchor_commitment=commitment,
        transaction_hash=args.transaction_hash,
        log_index=args.log_index,
        from_block=deployment_block,
    )
    schema = strict_json_load(ROOT / "packages/manifests/chain-anchor.schema.json")
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(anchor.to_dict())
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as target:
        target.write(canonical_json(anchor.to_dict()) + b"\n")


if __name__ == "__main__":
    main()
