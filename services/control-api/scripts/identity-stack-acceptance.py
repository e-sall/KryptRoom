"""Disposable native-Linux PR2 stack; no cryptographic runtime or public listener."""

import argparse
import json
import os
import runpy
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

here = Path(__file__).resolve().parent
acceptance = runpy.run_path(str(here / "identity-acceptance.py"))
compose = acceptance["compose"]
service = here.parent


def wait_ready() -> None:
    context = ssl.create_default_context(cafile=str(service / ".runtime/identity/tls/ca.crt"))
    endpoints = (
        "http://127.0.0.1:8001/health/ready",
        "https://127.0.0.1:8444/realms/kryptroom-dev/.well-known/openid-configuration",
    )
    for _ in range(120):
        try:
            for endpoint in endpoints:
                # Fixed loopback listeners belonging to this disposable fixture.
                with urllib.request.urlopen(endpoint, context=context, timeout=2) as response:  # noqa: S310
                    if response.status != 200:
                        raise OSError("Not ready")
            break
        except (OSError, urllib.error.URLError):
            time.sleep(0.5)
    else:
        raise RuntimeError("Real identity stack did not become ready")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--disposable",
        action="store_true",
        required=True,
        help="Explicitly permit removal of this synthetic PR2 stack/volume",
    )
    parser.parse_args()
    if os.name != "posix" or os.geteuid() != 0 or str(service).startswith("/mnt/"):
        raise RuntimeError("Use an isolated native Linux checkout and fixture controller")
    # Root is used only for offline fixture ownership and host orchestration.
    # PostgreSQL/API/migrator/Keycloak/BFF/browser keep their separate UIDs/roles.
    try:
        compose("down", "--volumes", "--remove-orphans")
        runpy.run_path(str(here / "local-secrets.py"), run_name="__main__")
        compose("config", "--quiet")
        compose("build")
        compose("run", "--rm", "identity-prepare")
        compose("up", "-d", "api", "keycloak", "bff")
        wait_ready()
        acceptance["browser_acceptance"]()
        privacy = runpy.run_path(str(here / "identity-privacy.py"))
        print(json.dumps(privacy["verify"]()))
        print(json.dumps({"real_stack_acceptance": "passed", "core_execution": False}))
    finally:
        print(acceptance["sanitized_browser_log"]())
        compose("--profile", "operator", "down", "--volumes", "--remove-orphans")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("PR2 real acceptance failed; inspect sanitized evidence", file=sys.stderr)
        raise SystemExit(1) from None
