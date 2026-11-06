"""Local-only lifecycle acceptance. Never connects to Core, an IdP or a chain."""

import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[1]
docker = shutil.which("docker")


def compose(*arguments: str) -> None:
    # Arguments are fixed local calls, never HTTP/CLI input.
    subprocess.run([docker, "compose", *arguments], cwd=root, check=True)  # noqa: S603


def status(path: str) -> int:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8001" + path, timeout=5) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code
    except OSError:
        return 0


def expect(ready: int) -> None:
    for _ in range(40):
        if status("/health/ready") == ready and status("/health/live") == 200:
            return
        time.sleep(0.5)
    raise AssertionError(f"Expected readiness {ready} and independent liveness 200")


def container_logs(*, diagnostic: bool = False) -> str:
    arguments = [docker, "compose", "logs", "--no-color"]
    if diagnostic:
        arguments += ["--tail", "200"]
    result = subprocess.run(  # noqa: S603 — fixed local log collection, never visitor input
        arguments, cwd=root, text=True, capture_output=True, check=True
    )
    return result.stdout + result.stderr


def credentials() -> list[str]:
    return [
        path.read_text(encoding="utf-8").strip()
        for path in (root / ".runtime" / "secrets").iterdir()
        if path.is_file()
    ]


def assert_no_credentials(logs: str, values: list[str]) -> None:
    """Scan the complete available cycle; do not print logs or credential values."""
    if any(value and value in logs for value in values):
        raise AssertionError("A local credential appeared in container logs")


def main() -> None:
    if docker is None:
        raise SystemExit("Docker Compose v2 is required for container acceptance")
    try:
        compose("up", "--build", "-d", "api")
        expect(200)
        compose("--profile", "test", "run", "--build", "--rm", "tests")
        subprocess.run(  # noqa: S603 — fixed local acceptance script
            [sys.executable, "scripts/secret-acceptance.py"], cwd=root, check=True
        )
        compose("stop", "postgres")
        expect(503)
        compose("start", "postgres")
        expect(200)
        compose("restart", "api")
        expect(200)
        compose("run", "--rm", "migrate")
        expect(200)
        assert_no_credentials(container_logs(), credentials())
    except (OSError, AssertionError, subprocess.CalledProcessError):
        # Only displayed diagnostics are bounded; the confidentiality scan is complete.
        try:
            diagnostic = container_logs(diagnostic=True)
            for value in credentials():
                if value:
                    diagnostic = diagnostic.replace(value, "[REDACTED-LOCAL-CREDENTIAL]")
            print(diagnostic[-12000:], file=sys.stderr)
        except (OSError, subprocess.CalledProcessError):
            print("Container diagnostics unavailable", file=sys.stderr)
        raise
    print(
        json.dumps(
            {
                "ready": 200,
                "database_stopped_ready": 503,
                "live_during_outage": 200,
                "database_restart": 200,
                "api_restart": 200,
                "migration_repeat": 200,
                "credential_log_scan": "passed",
                "native_secret_acceptance": "passed",
            }
        )
    )


if __name__ == "__main__":
    main()
