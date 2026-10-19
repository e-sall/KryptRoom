"""Create the public manifest for the single authoritative M7 deployment."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engines.chain_anchor.commitment import strict_json_load
from engines.chain_anchor.rpc import JsonRpcClient
from engines.chain_anchor.verifier import BASE_SEPOLIA_CHAIN_ID, keccak256
from engines.mpc.room_state import canonical_json


def quantity(value: str) -> int:
    return int(value, 16)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract-address", required=True)
    parser.add_argument("--deployment-transaction", required=True)
    parser.add_argument("--foundry-artifact", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rpc_url = os.environ.get("BASE_SEPOLIA_RPC_URL")
    if not rpc_url:
        raise SystemExit("BASE_SEPOLIA_RPC_URL is required")
    rpc = JsonRpcClient(rpc_url)
    if quantity(rpc.call("eth_chainId", [])) != BASE_SEPOLIA_CHAIN_ID:
        raise SystemExit("RPC is not Base Sepolia")
    receipt = rpc.call("eth_getTransactionReceipt", [args.deployment_transaction])
    if receipt is None or quantity(receipt.get("status", "0x0")) != 1:
        raise SystemExit("Deployment receipt is missing or failed")
    block_number = quantity(receipt["blockNumber"])
    if receipt.get("contractAddress", "").lower() != args.contract_address.lower():
        raise SystemExit("Deployment receipt contract address mismatch")
    runtime = bytes.fromhex(
        rpc.call("eth_getCode", [args.contract_address, hex(block_number)]).removeprefix("0x")
    )
    if not runtime:
        raise SystemExit("Deployment has no runtime bytecode")
    artifact = json.loads(Path(args.foundry_artifact).read_text(encoding="utf-8"))
    expected_runtime = bytes.fromhex(
        artifact["deployedBytecode"]["object"].removeprefix("0x")
    )
    if runtime != expected_runtime:
        raise SystemExit("Deployed runtime differs from the pinned Foundry build")
    block = rpc.call("eth_getBlockByNumber", [hex(block_number), False])
    if block is None or block.get("hash", "").lower() != receipt["blockHash"].lower():
        raise SystemExit("Deployment receipt is not in the canonical block")
    deployed_at = (
        datetime.fromtimestamp(quantity(block["timestamp"]), timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    manifest = {
        "version": "1",
        "chainId": BASE_SEPOLIA_CHAIN_ID,
        "contractAddress": args.contract_address.lower(),
        "deploymentTransactionHash": args.deployment_transaction.lower(),
        "deploymentBlockNumber": block_number,
        "runtimeBytecodeHash": "0x" + keccak256(runtime).hex(),
        "solidityVersion": "0.8.37",
        "foundryVersion": "1.8.5",
        "deployedAt": deployed_at,
    }
    schema = strict_json_load(ROOT / "packages/manifests/public-chain-deployment.schema.json")
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(manifest)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as target:
        target.write(canonical_json(manifest) + b"\n")


if __name__ == "__main__":
    main()
