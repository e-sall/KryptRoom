"""Offline private fixture provisioning, for the explicit native-Linux local stack only."""

import json
import os
import secrets
import stat
from pathlib import Path

from keycloak.local_tls import generate
from keycloak.render_realm import render_realm

root = Path(__file__).resolve().parents[1]
runtime = root / ".runtime"
source = runtime / "secrets"
names = (
    "oidc_bff_secret",
    "oidc_api_secret",
    "alice_password",
    "bob_password",
    "charlie_password",
    "dora_password",
    "bff_encryption_key",
    "bff_hash_key",
)
if os.name != "posix":
    raise SystemExit("Identity stack requires native Linux permissions")
for directory in (runtime, source):
    info = directory.lstat()
    if not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o700 or info.st_uid != 0:
        raise SystemExit("Invalid local source directory")
for name in names:
    path = source / name
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except FileExistsError:
        continue
    with os.fdopen(fd, "w") as stream:
        stream.write(secrets.token_urlsafe(32 if name.startswith("bff_") else 36))
values = {}
for path in source.iterdir():
    info = path.lstat()
    if (
        not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) != 0o600
        or info.st_uid != 0
        or info.st_nlink != 1
    ):
        raise SystemExit("Invalid source credential metadata")
    value = path.read_text()
    if not 24 <= len(value) <= 128 or any(
        c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-" for c in value
    ):
        raise SystemExit("Invalid source credential content")
    values[path.name] = value


def write(directory: Path, name: str, content: str, uid: int) -> None:
    path = directory / name
    if path.exists():
        info = path.lstat()
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or info.st_uid != uid
            or stat.S_IMODE(info.st_mode) != 0o400
            or path.read_text() != content
        ):
            raise SystemExit("Existing fixture differs; explicit rotation required")
        return
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o400)
    with os.fdopen(fd, "w") as stream:
        stream.write(content)
        os.fchown(stream.fileno(), uid, uid)


target = runtime / "identity"
target.mkdir(mode=0o700, exist_ok=True)
for scope, uid, selected in [
    ("api", 10001, ("oidc_api_secret",)),
    ("bff", 10001, ("oidc_bff_secret", "bff_password", "bff_encryption_key", "bff_hash_key")),
    ("operator", 10001, ("operator_password",)),
    ("keycloak", 1000, ("keycloak_password",)),
]:
    directory = target / scope
    directory.mkdir(mode=0o700, exist_ok=True)
    if directory.is_symlink() or not directory.is_dir():
        raise SystemExit("Invalid fixture directory")
    for name in selected:
        write(directory, name, values[name], uid)
    if scope == "keycloak":
        supplied = {
            "KR_BFF_CLIENT_SECRET": values["oidc_bff_secret"],
            "KR_API_CLIENT_SECRET": values["oidc_api_secret"],
        }
        for user in ("alice", "bob", "charlie", "dora"):
            supplied[f"KR_{user.upper()}_PASSWORD"] = values[user + "_password"]
        template = json.loads((root / "scripts/keycloak/realm.template.json").read_text())
        # Local host-network fixture: all inbound services bind loopback exclusively.
        template["clients"][0]["attributes"]["backchannel.logout.url"] = (
            "http://127.0.0.1:3004/auth/backchannel-logout"
        )
        write(
            directory, "kryptroom-dev-realm.json", json.dumps(render_realm(template, supplied)), uid
        )
    os.chown(directory, uid, uid)
tls = target / "tls"
tls.mkdir(mode=0o700, exist_ok=True)
if not any(tls.iterdir()):
    generate(tls)
print("Private identity fixtures provisioned; no values displayed")
