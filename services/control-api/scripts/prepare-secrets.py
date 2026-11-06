"""One-shot, offline projection of private host credentials to isolated UID-owned volumes."""

import os
import re
import stat
import sys
from pathlib import Path

NAMES = ("postgres_password", "migrator_password", "app_password")
SCOPES = {
    "postgres": (999, ("postgres_password", "migrator_password", "app_password")),
    "migrate": (10001, ("migrator_password",)),
    "api": (10001, ("app_password",)),
    "tests": (10001, ("migrator_password", "app_password")),
}


class SecretPolicyError(ValueError):
    """Contains no credential value."""


def validate_content(value: bytes) -> bytes:
    if re.fullmatch(rb"[A-Za-z0-9_-]{24,128}", value) is None:
        raise SecretPolicyError("Invalid local credential content")
    return value


def validate_file(info: os.stat_result, mode: int, uid: int | None = None) -> None:
    if (
        not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) != mode
        or info.st_nlink != 1
        or not 24 <= info.st_size <= 128
        or (uid is not None and info.st_uid != uid)
    ):
        raise SecretPolicyError("Invalid local credential metadata")


def read_source(path: Path) -> bytes:
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        validate_file(os.fstat(descriptor), 0o600)
        return validate_content(os.read(descriptor, 129))
    finally:
        os.close(descriptor)


def provision(source: Path = Path("/run/secrets"), output: Path = Path("/output")) -> None:
    if os.name != "posix":
        raise SecretPolicyError("Native POSIX storage is required")
    # Read and validate every source before creating any consumer credential.
    values = {name: read_source(source / name) for name in NAMES}
    for scope, (uid, names) in SCOPES.items():
        directory = output / scope
        info = directory.lstat()
        if not stat.S_ISDIR(info.st_mode):
            raise SecretPolicyError("Invalid credential volume")
        existing = set(p.name for p in directory.iterdir())
        if not existing <= set(names):
            raise SecretPolicyError("Unexpected credential in consumer volume")
        fresh = not existing and info.st_uid == 0 and info.st_gid == 0
        if fresh:
            if stat.S_IMODE(info.st_mode) not in (0o700, 0o755):
                raise SecretPolicyError("Invalid empty credential volume permissions")
        elif (info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode)) != (uid, uid, 0o700):
            raise SecretPolicyError("Invalid consumer directory permissions")
        # An existing projection must match its original credential and metadata.
        for name in existing:
            path = directory / name
            descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                validate_file(os.fstat(descriptor), 0o400, uid)
                if os.read(descriptor, 129) != values[name]:
                    raise SecretPolicyError("Credential rotation requires an explicit operation")
            finally:
                os.close(descriptor)
        if fresh:
            directory.chmod(0o700)
        for name in names:
            if name in existing:
                continue
            path = directory / name
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o400)
            try:
                os.write(descriptor, values[name])
                os.fsync(descriptor)
                os.fchown(descriptor, uid, uid)
            finally:
                os.close(descriptor)
        if fresh:
            os.chown(directory, uid, uid)


def main() -> int:
    try:
        provision()
    except (OSError, SecretPolicyError):
        print("Local secret projection refused; inspect credential metadata", file=sys.stderr)
        return 1
    print("Local UID-isolated secret volumes prepared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
