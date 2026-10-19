"""Standalone three-layer M7 verifier."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from engines.chain_anchor.commitment import strict_json_load
from engines.chain_anchor.model import ChainAnchor
from engines.chain_anchor.rpc import JsonRpcClient
from engines.chain_anchor.verifier import (
    m5_verifier_command,
    run_m5_verifier,
    verify_chain_layer,
    verify_package_layer,
)
from engines.mpc.room_state import canonical_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a finalized KryptRoom public anchor")
    parser.add_argument("--rpc-url", required=True)
    parser.add_argument("--deployment-manifest", required=True)
    parser.add_argument("--chain-anchor", required=True)
    parser.add_argument("--room-state", required=True)
    parser.add_argument("--state-proof")
    parser.add_argument("--m5-verifier")
    parser.add_argument("--m5-receipt")
    parser.add_argument("--m5-proof-bin")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    anchor_document = strict_json_load(args.chain_anchor)
    anchor_schema = strict_json_load(root / "packages/manifests/chain-anchor.schema.json")
    Draft202012Validator(anchor_schema, format_checker=FormatChecker()).validate(
        anchor_document
    )
    anchor = ChainAnchor.from_dict(anchor_document)
    deployment = strict_json_load(args.deployment_manifest)
    deployment_schema = strict_json_load(
        root / "packages/manifests/public-chain-deployment.schema.json"
    )
    Draft202012Validator(deployment_schema, format_checker=FormatChecker()).validate(
        deployment
    )
    if deployment.get("chainId") != anchor.chain_id:
        parser.error("Deployment manifest chainId differs from ChainAnchor")
    state = strict_json_load(args.room_state)
    proof_document = strict_json_load(args.state_proof) if args.state_proof else None
    package = verify_package_layer(anchor, state, proof_document)
    observed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    status = verify_chain_layer(
        anchor,
        JsonRpcClient(args.rpc_url),
        expected_contract_address=deployment["contractAddress"],
        expected_runtime_code_hash=deployment["runtimeBytecodeHash"],
        require_finalized=True,
        observed_at=observed_at,
    )

    m5_status = "not-applicable"
    if package.m5_proof_validation_required:
        supplied = [args.m5_verifier, args.m5_receipt, args.m5_proof_bin, args.state_proof]
        if any(supplied[:3]) and not all(supplied):
            parser.error("Layer C requires --m5-verifier, --m5-receipt and --m5-proof-bin")
        if all(supplied):
            command = m5_verifier_command(
                verifier=args.m5_verifier,
                receipt=args.m5_receipt,
                state_proof=args.state_proof,
                proof=args.m5_proof_bin,
                room_id=anchor.room_id,
                transition_id=anchor.transition_id,
            )
            run_m5_verifier(command)
            m5_status = "verified-separately"
        else:
            m5_status = "required-separate-step"

    print(
        canonical_json(
            {
                "anchorId": anchor.anchor_id,
                "anchorCommitment": package.anchor_commitment,
                "chainStatus": status.status.value,
                "layerA": "verified",
                "layerB": "verified",
                "layerC": m5_status,
            }
        ).decode("utf-8")
    )


if __name__ == "__main__":
    main()
