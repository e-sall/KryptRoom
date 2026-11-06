"""Native Linux Docker regression: actual service UIDs and real PG bootstrap negatives."""

import json
import os
import secrets
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCKER = shutil.which("docker")
PG = (
    "postgres:17.11-bookworm@"
    "sha256:839fbb5a4942a7758dd93e18b42ea5649807491a0545b5eeeb8f0b8bb11857a5"
)
if DOCKER is None or os.name != "posix":
    raise SystemExit("Native Linux Docker is required")


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(  # noqa: S603 — fixed executable and internally constructed arguments
        [DOCKER, *args], cwd=ROOT, capture_output=True, text=True, timeout=90
    )
    if check and result.returncode:
        raise AssertionError("Native secret acceptance Docker operation failed")
    return result


def wait_running(name: str) -> None:
    for _ in range(60):
        if run("exec", name, "pg_isready", "-U", "postgres", check=False).returncode == 0:
            return
        time.sleep(0.25)
    raise AssertionError("Inspection PostgreSQL did not become ready")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


probe = """
import errno, os, stat
from pathlib import Path
assert os.getuid() == 10001
directory = Path('/run/secrets')
expected = set(__import__('sys').argv[1:])
assert {p.name for p in directory.iterdir()} == expected
assert directory.stat().st_uid == 10001 and stat.S_IMODE(directory.stat().st_mode) == 0o700
assert os.statvfs(directory).f_flag & os.ST_RDONLY
for name in expected:
    p = directory / name
    assert p.stat().st_uid == 10001 and stat.S_IMODE(p.stat().st_mode) == 0o400
    with p.open('rb') as f: assert 24 <= len(f.read(129)) <= 128
print('UID 10001, scoped owner-only credentials, read-only mount: PASS')
"""
for service, names in (
    ("migrate", ["migrator_password"]),
    ("api", ["app_password"]),
    ("tests", ["migrator_password", "app_password"]),
):
    run(
        "compose",
        "run",
        "--rm",
        "--no-deps",
        "--entrypoint",
        "python",
        service,
        "-c",
        probe,
        *names,
    )
    denial = """
from pathlib import Path
import sys
try:
    Path('/run/secrets', sys.argv[1]).open('rb').close()
except PermissionError:
    print('Foreign UID refused: PASS')
else:
    raise AssertionError('Foreign UID could read a credential')
"""
    run(
        "compose",
        "run",
        "--rm",
        "--no-deps",
        "--user",
        "10002:10002",
        "--entrypoint",
        "python",
        service,
        "-c",
        denial,
        names[0],
    )

scram = run(
    "compose",
    "exec",
    "-T",
    "postgres",
    "psql",
    "-U",
    "postgres",
    "-d",
    "postgres",
    "-Atc",
    "SELECT count(*) FROM pg_authid WHERE rolname IN ('kryptroom_app','kryptroom_migrator') "
    "AND rolpassword LIKE 'SCRAM-SHA-256$%'",
).stdout.strip()
require(scram == "2", "Application roles must have SCRAM credentials")

container = run("compose", "ps", "-a", "-q", "prepare-secrets").stdout.strip()
image = run("inspect", container, "--format", "{{.Image}}").stdout.strip()
source_results = []
for case in ("missing", "unreadable", "empty", "invalid", "permissions"):
    with tempfile.TemporaryDirectory(prefix="kryptroom-source-negative-") as temporary:
        source = Path(temporary)
        for name in ("postgres_password", "migrator_password", "app_password"):
            p = source / name
            p.write_text(secrets.token_urlsafe(36), encoding="utf-8")
            p.chmod(0o600)
        p = source / "app_password"
        if case == "missing":
            p.unlink()
        elif case == "empty":
            p.write_bytes(b"")
        elif case == "invalid":
            p.write_bytes(b"invalid credential with spaces 0123456789")
        else:
            p.chmod(0 if case == "unreadable" else 0o640)
        result = run(
            "run",
            "--rm",
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--cap-add",
            "CHOWN",
            "--cap-add",
            "DAC_OVERRIDE",
            "--mount",
            f"type=bind,source={source},target=/run/secrets,readonly",
            "--tmpfs",
            "/output/postgres:mode=0755",
            "--tmpfs",
            "/output/migrate:mode=0755",
            "--tmpfs",
            "/output/api:mode=0755",
            "--tmpfs",
            "/output/tests:mode=0755",
            image,
            check=False,
        )
        require(
            result.returncode != 0 and "Local secret projection refused" in result.stderr,
            "Invalid source did not fail closed",
        )
        source_results.append({"case": case, "projection_refused": True})
results = []
for case in ("missing", "unreadable", "empty", "invalid", "permissions", "owner"):
    prefix = "kr-m9-negative-" + uuid.uuid4().hex[:12]
    credential_volume, data_volume = prefix + "-secrets", prefix + "-data"
    bootstrap, inspection = prefix + "-bootstrap", prefix + "-inspect"
    with tempfile.TemporaryDirectory(prefix="kryptroom-secret-negative-") as temporary:
        source = Path(temporary)
        values = {
            name: secrets.token_urlsafe(36)
            for name in ("postgres_password", "migrator_password", "app_password")
        }
        for name, value in values.items():
            p = source / name
            p.write_text(value, encoding="utf-8")
            p.chmod(0o600)
        try:
            run("volume", "create", credential_volume)
            run("volume", "create", data_volume)
            mounts = []
            for name in values:
                mounts += [
                    "--mount",
                    f"type=bind,source={source / name},target=/run/secrets/{name},readonly",
                ]
            run(
                "run",
                "--rm",
                "--network",
                "none",
                "--read-only",
                "--cap-drop",
                "ALL",
                "--cap-add",
                "CHOWN",
                "--cap-add",
                "DAC_OVERRIDE",
                "--security-opt",
                "no-new-privileges:true",
                *mounts,
                "--mount",
                f"type=volume,source={credential_volume},target=/output/postgres",
                "--tmpfs",
                "/output/migrate:mode=0755",
                "--tmpfs",
                "/output/api:mode=0755",
                "--tmpfs",
                "/output/tests:mode=0755",
                image,
            )
            mutate = """
import os, sys
from pathlib import Path
case = sys.argv[1]
name = 'app_password' if case in ('empty', 'invalid', 'permissions') else 'migrator_password'
p = Path('/fault', name)
value = p.read_bytes()
p.unlink()
if case != 'missing':
    mode = 0 if case == 'unreadable' else (0o640 if case == 'permissions' else 0o400)
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    payload = b'' if case == 'empty' else value
    if case == 'invalid': payload = b'invalid credential with spaces 0123456789'
    os.write(fd, payload)
    os.fchown(fd, 10001 if case == 'owner' else 999, 999)
    os.close(fd)
"""
            run(
                "run",
                "--rm",
                "--network",
                "none",
                "--read-only",
                "--cap-drop",
                "ALL",
                "--cap-add",
                "CHOWN",
                "--cap-add",
                "DAC_OVERRIDE",
                "--mount",
                f"type=volume,source={credential_volume},target=/fault",
                "--entrypoint",
                "python",
                image,
                "-c",
                mutate,
                case,
            )
            run(
                "run",
                "-d",
                "--name",
                bootstrap,
                "--network",
                "none",
                "--mount",
                f"type=volume,source={data_volume},target=/var/lib/postgresql/data",
                "--mount",
                f"type=volume,source={credential_volume},target=/run/secrets,readonly",
                "--mount",
                f"type=bind,source={ROOT / 'scripts/init-db.sh'},"
                "target=/docker-entrypoint-initdb.d/10-control.sh,readonly",
                "-e",
                "POSTGRES_USER=postgres",
                "-e",
                "POSTGRES_DB=kryptroom",
                "-e",
                "POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password",
                "-e",
                "POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256 --auth-local=trust",
                PG,
            )
            code = run("wait", bootstrap).stdout.strip()
            result = run("logs", bootstrap)
            logs = result.stdout + result.stderr
            require(
                code != "0" and "bootstrap refused an invalid credential" in logs,
                "Invalid bootstrap did not fail closed",
            )
            require(
                "CREATE ROLE" not in logs and "clearing password" not in logs,
                "Bootstrap reached SQL despite invalid credentials",
            )
            require(
                all(value not in logs for value in values.values()), "Credential leaked in logs"
            )
            run(
                "run",
                "-d",
                "--name",
                inspection,
                "--network",
                "none",
                "--mount",
                f"type=volume,source={data_volume},target=/var/lib/postgresql/data",
                PG,
            )
            wait_running(inspection)
            count = run(
                "exec",
                inspection,
                "psql",
                "-U",
                "postgres",
                "-d",
                "postgres",
                "-Atc",
                "SELECT count(*) FROM pg_roles "
                "WHERE rolname IN ('kryptroom_app','kryptroom_migrator')",
            ).stdout.strip()
            require(count == "0", "A role was created despite invalid bootstrap credentials")
            results.append({"case": case, "bootstrap_refused": True, "application_roles": 0})
        finally:
            for name in (bootstrap, inspection):
                run("rm", "-f", name, check=False)
            for name in (credential_volume, data_volume):
                run("volume", "rm", name, check=False)
print(
    json.dumps(
        {
            "consumer_uid_isolation": ["migrate", "api", "tests"],
            "foreign_uid_refused": True,
            "scram_roles": 2,
            "source_negatives": source_results,
            "native_postgres_negatives": results,
        }
    )
)
