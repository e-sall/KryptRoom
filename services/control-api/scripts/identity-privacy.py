"""Scan actual synthetic session secrets against runtime logs and served client assets."""

import base64
import io
import json
import re
import shutil
import subprocess
import tarfile
from pathlib import Path

import psycopg
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SERVICE = Path(__file__).resolve().parents[1]


def b64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def verify() -> dict[str, object]:
    docker = shutil.which("docker")
    if docker is None:
        raise RuntimeError("Docker required")
    source = SERVICE / ".runtime/secrets"
    values = [p.read_text() for p in source.iterdir() if p.is_file()]
    key = b64((source / "bff_encryption_key").read_text())
    count = 0
    with psycopg.connect(
        host="127.0.0.1",
        port=5435,
        dbname="kryptroom",
        user="kryptroom_bff",
        password=(source / "bff_password").read_text(),
        connect_timeout=2,
    ) as db:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id_hash,encryption_key_id,encrypted_access_token,"
                "encrypted_refresh_token FROM bff_auth.sessions"
            )
            for sid, key_id, access, refresh in cursor.fetchall():
                if not re.fullmatch(r"[0-9a-f]{64}", sid):
                    raise RuntimeError("Invalid keyed session lookup")
                for purpose, value in (("access", access), ("refresh", refresh)):
                    if value is None:
                        continue
                    parts = value.split(".")
                    if len(parts) != 4 or parts[0] != key_id:
                        raise RuntimeError("Invalid encrypted session envelope")
                    raw = (
                        AESGCM(key)
                        .decrypt(
                            b64(parts[1]),
                            b64(parts[2]) + b64(parts[3]),
                            f"{key_id}:{purpose}:{sid}".encode(),
                        )
                        .decode()
                    )
                    if raw in value:
                        raise RuntimeError("Plain token found in persisted envelope")
                    values.append(raw)
                    count += 1
    if count < 8:
        raise RuntimeError("Real session token evidence incomplete")
    logs = subprocess.check_output(  # noqa: S603 — fixed trusted local log query, no shell
        [  # noqa: S603 — fixed local project/container log query
            docker,
            "compose",
            "-p",
            "kr-m9-pr2-real",
            "-f",
            str(SERVICE / "compose.identity.yml"),
            "logs",
            "--no-color",
        ],
        cwd=SERVICE,
        stderr=subprocess.STDOUT,
    )
    if any(value.encode() in logs for value in values) or re.search(
        rb"eyJ[\w-]+\.[\w-]+\.[\w-]+", logs
    ):
        raise RuntimeError("Session credential appeared in runtime logs")
    assets = subprocess.check_output(  # noqa: S603 — fixed trusted client archive query
        [  # noqa: S603 — fixed client-only output path, never extracts files
            docker,
            "cp",
            "kr-m9-pr2-real-bff-1:/app/.next/static",
            "-",
        ],
        stderr=subprocess.DEVNULL,
    )
    if len(assets) > 64 * 1024 * 1024:
        raise RuntimeError("Client asset scan exceeded bound")
    files = 0
    with tarfile.open(fileobj=io.BytesIO(assets)) as bundle:
        for member in bundle.getmembers():
            if not member.isfile():
                continue
            stream = bundle.extractfile(member)
            if stream is None:
                raise RuntimeError("Client asset unavailable")
            content = stream.read(16 * 1024 * 1024 + 1)
            if len(content) > 16 * 1024 * 1024 or any(
                value.encode() in content for value in values
            ):
                raise RuntimeError("Session credential appeared in served client artifacts")
            files += 1
    result = {
        "encrypted_tokens_verified": count,
        "runtime_credential_log_scan": "passed",
        "served_client_files_scanned": files,
        "client_credential_scan": "passed",
        "tokens_or_credentials_printed": False,
    }
    (SERVICE / ".runtime/qa-channel/privacy.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    print(json.dumps(verify()))
