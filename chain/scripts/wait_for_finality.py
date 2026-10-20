"""Poll an immutable ChainAnchor until Base reports finalized or it is orphaned."""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engines.chain_anchor.commitment import strict_json_load
from engines.chain_anchor.model import AnchorStatus, ChainAnchor
from engines.chain_anchor.rpc import JsonRpcClient
from engines.chain_anchor.verifier import ChainVerificationError, verify_chain_layer
from engines.mpc.room_state import canonical_json


def _now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _write_exclusive(path: Path, value: dict[str, str]) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as target:
        target.write(canonical_json(value) + b"\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Wait for Base finalized ancestry")
    parser.add_argument("--chain-anchor", required=True)
    parser.add_argument("--deployment-manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--poll-seconds", type=int, default=15)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    args = parser.parse_args()
    if args.poll_seconds < 1 or args.timeout_seconds < 1:
        parser.error("poll and timeout must be positive")
    rpc_url = os.environ.get("BASE_SEPOLIA_RPC_URL")
    if not rpc_url:
        raise SystemExit("BASE_SEPOLIA_RPC_URL is required")

    anchor = ChainAnchor.from_dict(strict_json_load(args.chain_anchor))
    deployment = strict_json_load(args.deployment_manifest)
    rpc = JsonRpcClient(rpc_url)
    deadline = time.monotonic() + args.timeout_seconds
    latest = None
    while time.monotonic() < deadline:
        observed_at = _now()
        try:
            latest = verify_chain_layer(
                anchor,
                rpc,
                expected_contract_address=deployment["contractAddress"],
                expected_runtime_code_hash=deployment["runtimeBytecodeHash"],
                require_finalized=False,
                observed_at=observed_at,
            )
        except ChainVerificationError as error:
            if error.status in (AnchorStatus.ORPHANED, AnchorStatus.FAILED):
                latest = {
                    "anchorId": anchor.anchor_id,
                    "status": error.status.value,
                    "observedAt": observed_at,
                    "detail": str(error),
                }
                break
            raise
        if latest.status is AnchorStatus.FINALIZED:
            break
        time.sleep(args.poll_seconds)
    else:
        raise SystemExit("Timed out before the anchor reached finalized")

    value = latest if isinstance(latest, dict) else latest.to_dict()
    schema = strict_json_load(ROOT / "packages/manifests/chain-anchor-status.schema.json")
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)
    _write_exclusive(Path(args.output), value)
    if value["status"] != AnchorStatus.FINALIZED.value:
        raise SystemExit(f"Anchor ended in {value['status']}: {value['detail']}")


if __name__ == "__main__":
    main()
