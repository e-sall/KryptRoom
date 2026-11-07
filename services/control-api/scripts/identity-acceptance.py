"""Real local PR2 acceptance; host orchestrates, browser has no Docker/SQL authority."""

import argparse
import base64
import hashlib
import json
import os
import re
import secrets
import shutil
import stat
import subprocess
import time
from pathlib import Path
from uuid import UUID

import psycopg
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from psycopg import sql

SERVICE = Path(__file__).resolve().parents[1]
WEB = SERVICE.parents[1] / "apps/web"
PROJECT = "kr-m9-pr2-real"


def run(*args: str) -> None:
    # Fixed trusted programs/actions. Resource IDs below are normalized UUIDs.
    subprocess.run(args, check=True, timeout=300)  # noqa: S603


def compose(*args: str) -> None:
    docker = shutil.which("docker")
    if docker is None:
        raise RuntimeError("Docker Compose required")
    run(
        docker,
        "compose",
        "--project-directory",
        str(SERVICE),
        "-p",
        PROJECT,
        "-f",
        str(SERVICE / "compose.identity.yml"),
        *args,
    )


def operator(*args: str) -> None:
    compose(
        "--profile",
        "operator",
        "run",
        "--rm",
        "operator",
        *args,
        "--operator",
        "synthetic-acceptance-operator",
        "--case",
        "PR2-E2E",
    )


def public_spki() -> str:
    cert = x509.load_pem_x509_certificate(
        (SERVICE / ".runtime/identity/tls/server.crt").read_bytes()
    )
    public = cert.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return base64.b64encode(hashlib.sha256(public).digest()).decode()


def private_fixture() -> tuple[Path, Path]:
    runtime = SERVICE / ".runtime"
    browser = runtime / "browser-users"
    channel = runtime / "qa-channel"
    for directory in (browser, channel):
        directory.mkdir(mode=0o700, exist_ok=True)
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError("Invalid private fixture directory")
        if directory == channel and any(directory.iterdir()):
            raise ValueError("QA channel must be fresh; preserve old evidence separately")
        os.chown(directory, 10001, 10001)
    for user in ("alice", "bob", "charlie", "dora"):
        source = runtime / "secrets" / (user + "_password")
        info = source.lstat()
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != 0
            or info.st_nlink != 1
            or stat.S_IMODE(info.st_mode) != 0o600
        ):
            raise ValueError("Invalid synthetic account credential")
        target = browser / source.name
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o400)
        with os.fdopen(fd, "wb") as stream:
            stream.write(source.read_bytes())
            os.fchown(stream.fileno(), 10001, 10001)
    channel_guards(channel)
    return browser, channel


def acknowledge(channel: Path, name: str) -> None:
    fd = os.open(
        channel / (name + ".ack"), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o444
    )
    with os.fdopen(fd, "w") as stream:
        stream.write("completed")


def channel_guards(channel: Path) -> None:
    sentinel, supplied, ack = (
        channel / name for name in ("guard-sentinel", "guard-probe.json", "guard-probe.ack")
    )
    fd = os.open(sentinel, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as stream:
        stream.write("preserved")
    try:
        supplied.symlink_to(sentinel)
        ack.symlink_to(sentinel)
        try:
            checkpoint(channel, "guard-probe")
        except OSError:
            pass
        else:
            raise RuntimeError("Controller followed browser metadata symlink")
        try:
            acknowledge(channel, "guard-probe")
        except FileExistsError:
            pass
        else:
            raise RuntimeError("Controller replaced preexisting acknowledgement")
        if sentinel.read_text() != "preserved":
            raise RuntimeError("Controller altered protected sentinel")
    finally:
        # These are the three exact files created above inside a fresh private
        # channel. Never recursively delete a workspace or caller-supplied path.
        supplied.unlink(missing_ok=True)
        ack.unlink(missing_ok=True)
        sentinel.unlink(missing_ok=True)
    print(json.dumps({"qa_channel_no_follow": "passed", "acknowledgement_exclusive": "passed"}))


def checkpoint(channel: Path, name: str) -> dict[str, str] | None:
    path = channel / (name + ".json")
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except FileNotFoundError:
        return None
    try:
        info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or info.st_uid != 10001
            or info.st_size > 1024
        ):
            raise ValueError("Invalid bounded QA metadata")
        value = json.loads(os.read(descriptor, 1025).decode())
    finally:
        os.close(descriptor)
    if not isinstance(value, dict):
        raise ValueError("Invalid QA metadata")
    expected = {
        "01-enrollment": {"organizationA", "organizationB", "charlie", "dora"},
        "05-refresh": {"alice", "charlie"},
        "07-invalid-refresh": {"dora"},
        "08-idle-expiry": {"dora"},
        "09-absolute-expiry": {"dora"},
        "10-backchannel-check": {"bob"},
    }
    if name in expected:
        if set(value) != expected[name]:
            raise ValueError("Invalid enrollment metadata")
        for key, item in value.items():
            parsed = UUID(item)
            if parsed.version != 7 or str(parsed) != item:
                raise ValueError("Expected exact synthetic business identifiers")
            value[key] = str(parsed)
    elif value:
        raise ValueError("Lifecycle checkpoints contain no commands or arguments")
    return value


def bff_probe():
    """Synthetic test controller only. Restricted BFF credential, never a browser capability."""
    return psycopg.connect(
        host="127.0.0.1",
        port=5435,
        dbname="kryptroom",
        user="kryptroom_bff",
        password=(SERVICE / ".runtime/secrets/bff_password").read_text(),
        connect_timeout=2,
        options="-c statement_timeout=5000",
    )


def session_probe(name: str, metadata: dict[str, str], baseline: dict[str, int]) -> None:
    if name == "10-backchannel-check":
        # Verify persisted provider notification before a browser request could
        # invalidate the session via API introspection instead.
        for _ in range(50):
            with bff_probe() as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT bool_and(revoked_at IS NOT NULL),count(*) "
                    "FROM bff_auth.sessions WHERE user_id=%s",
                    (UUID(metadata["bob"]),),
                )
                row = cursor.fetchone()
                cursor.execute("SELECT count(*) FROM bff_auth.logout_replays")
                replay = cursor.fetchone()
                if row is not None and row[0] is True and row[1] > 0 and replay and replay[0] > 0:
                    return
            time.sleep(0.2)
        raise RuntimeError("Signed provider logout did not persist local revocation")
    with bff_probe() as connection, connection.cursor() as cursor:
        if name == "06-refresh-check":
            for sid, version in baseline.items():
                cursor.execute(
                    "SELECT version,revoked_at FROM bff_auth.sessions WHERE id_hash=%s", (sid,)
                )
                row = cursor.fetchone()
                if row is None or row[0] != version + 1 or row[1] is not None:
                    raise RuntimeError("Concurrent refresh did not commit exactly once")
            return
        for uid in metadata.values():
            cursor.execute(
                "SELECT id_hash,version,encryption_key_id FROM bff_auth.sessions "
                "WHERE user_id=%s AND revoked_at IS NULL FOR UPDATE",
                (UUID(uid),),
            )
            rows = cursor.fetchall()
            if len(rows) != 1:
                raise RuntimeError("Expected one active synthetic session")
            sid, version, key_id = rows[0]
            if name == "05-refresh":
                baseline[sid] = version
                cursor.execute(
                    "UPDATE bff_auth.sessions SET token_expires_at=now()-interval '1 second' "
                    "WHERE id_hash=%s",
                    (sid,),
                )
            elif name == "07-invalid-refresh":
                encoded = (SERVICE / ".runtime/secrets/bff_encryption_key").read_text()
                key = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
                nonce = secrets.token_bytes(12)
                ciphertext = AESGCM(key).encrypt(
                    nonce, secrets.token_urlsafe(32).encode(), f"{key_id}:refresh:{sid}".encode()
                )

                def b64(value: bytes) -> str:
                    return base64.urlsafe_b64encode(value).decode().rstrip("=")

                envelope = ".".join(
                    (key_id, b64(nonce), b64(ciphertext[:-16]), b64(ciphertext[-16:]))
                )
                cursor.execute(
                    "UPDATE bff_auth.sessions SET encrypted_refresh_token=%s, "
                    "token_expires_at=now()-interval '1 second' WHERE id_hash=%s",
                    (envelope, sid),
                )
            else:
                # Column comes solely from this fixed mapping, never checkpoint text.
                column = {
                    "08-idle-expiry": "idle_expires_at",
                    "09-absolute-expiry": "absolute_expires_at",
                }[name]
                cursor.execute(
                    sql.SQL(
                        "UPDATE bff_auth.sessions SET {}=now()-interval '1 second' WHERE id_hash=%s"
                    ).format(sql.Identifier(column)),
                    (sid,),
                )


def browser_acceptance() -> None:
    if os.name != "posix" or os.geteuid() != 0:
        raise RuntimeError(
            "Native local fixture controller required; runtime services stay nonroot"
        )
    docker = shutil.which("docker")
    if docker is None:
        raise RuntimeError("Docker required")
    browser, channel = private_fixture()
    run(
        docker,
        "build",
        "--target",
        "acceptance",
        "-f",
        str(WEB / "Dockerfile.identity"),
        "-t",
        "kr-m9-pr2-real-browser",
        str(WEB),
    )
    log_path = channel / "browser.log"
    with log_path.open("xb") as log:
        # Browser sees only four synthetic user passwords and a bounded metadata
        # channel. No Docker socket, host CLI, DB password, operator secret or key.
        process = subprocess.Popen(  # noqa: S603 — fixed trusted local executable/image, no shell
            [
                docker,
                "run",
                "--rm",
                "--name",
                "kr-m9-pr2-real-browser-run",
                "--network",
                "host",
                "--user",
                "10001:10001",
                "--read-only",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges:true",
                "--shm-size",
                "256m",
                "--tmpfs",
                "/run/browser-tmp:uid=10001,gid=10001,mode=0700",
                "--mount",
                f"type=bind,source={browser},target=/run/test-users,readonly",
                "--mount",
                f"type=bind,source={channel},target=/run/qa",
                "-e",
                "CONTROL_TEST_IDENTITY=1",
                "-e",
                "KR_TEST_QA_CHANNEL=/run/qa",
                "-e",
                "KR_TEST_TLS_SPKI=" + public_spki(),
                "kr-m9-pr2-real-browser",
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        phases = [
            "01-enrollment",
            "05-refresh",
            "06-refresh-check",
            "07-invalid-refresh",
            "08-idle-expiry",
            "09-absolute-expiry",
            "02-restart",
            "03-idp-stop",
            "04-idp-start",
            "10-backchannel-check",
        ]
        refresh_versions: dict[str, int] = {}
        completed = []
        deadline = time.monotonic() + 600
        try:
            while process.poll() is None:
                if time.monotonic() > deadline:
                    raise RuntimeError("Bounded browser acceptance timed out")
                if phases:
                    name = phases[0]
                    metadata = checkpoint(channel, name)
                    if metadata is not None:
                        if name == "01-enrollment":
                            operator("approve", "--organization", metadata["organizationA"])
                            operator("approve", "--organization", metadata["organizationB"])
                            operator(
                                "provision",
                                "--organization",
                                metadata["organizationA"],
                                "--user",
                                metadata["charlie"],
                            )
                            operator(
                                "provision",
                                "--organization",
                                metadata["organizationA"],
                                "--user",
                                metadata["dora"],
                                "--role",
                                "ORG_ADMIN",
                            )
                        elif name.startswith(("05-", "06-", "07-", "08-", "09-", "10-")):
                            session_probe(name, metadata, refresh_versions)
                        elif name == "02-restart":
                            compose("restart", "postgres", "api", "keycloak", "bff")
                        elif name == "03-idp-stop":
                            compose("stop", "keycloak")
                        else:
                            compose("start", "keycloak")
                        acknowledge(channel, name)
                        completed.append(phases.pop(0))
                time.sleep(0.2)
            if process.returncode != 0 or phases:
                raise RuntimeError(
                    "Real browser acceptance failed; inspect private sanitized evidence"
                )
        finally:
            if process.poll() is None:
                run(docker, "stop", "-t", "1", "kr-m9-pr2-real-browser-run")
    print(
        json.dumps(
            {
                "real_browser_acceptance": "passed",
                "checkpoints": completed,
                "browser_docker_access": False,
                "browser_uid": 10001,
            }
        )
    )


def sanitized_browser_log() -> str:
    path = SERVICE / ".runtime/qa-channel/browser.log"
    if not path.exists():
        return "Browser log unavailable"
    value = path.read_text(errors="replace")
    for secret in (SERVICE / ".runtime/secrets").iterdir():
        if secret.is_file():
            value = value.replace(secret.read_text(), "[REDACTED-FIXTURE-CREDENTIAL]")
    value = re.sub(r"eyJ[\w-]+\.[\w-]+\.[\w-]+", "[REDACTED-TOKEN]", value)
    value = re.sub(r"([?&](?:code|state|session_state)=)[^&\s]+", r"\1[REDACTED]", value)
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser-only", action="store_true", required=True)
    parser.parse_args()
    try:
        browser_acceptance()
    finally:
        print(sanitized_browser_log())
