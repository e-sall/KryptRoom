"""Local-only lifecycle acceptance. Never connects to Core, an IdP or a chain."""

import json
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[1]
docker = shutil.which("docker")
if docker is None:
    raise SystemExit("Docker Compose v2 is required for container acceptance")


def compose(*arguments: str) -> None:
    # Arguments come exclusively from the fixed local calls below; never an HTTP/CLI input.
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


compose("up", "--build", "-d", "api")
expect(200)
compose("--profile", "test", "run", "--build", "--rm", "tests")
compose("stop", "postgres")
expect(503)
compose("start", "postgres")
expect(200)
compose("restart", "api")
expect(200)
compose("run", "--rm", "migrate")
expect(200)
logs = subprocess.check_output([docker, "compose", "logs", "--no-color"], cwd=root, text=True)  # noqa: S603
for path in (root / ".runtime" / "secrets").iterdir():
    if path.read_text(encoding="utf-8").strip() in logs:
        raise AssertionError("A local credential appeared in container logs")
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
        }
    )
)
