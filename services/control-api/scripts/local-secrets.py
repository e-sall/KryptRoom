"""Create private local credentials on native POSIX storage; never overwrite values."""

import os
import re
import secrets
import stat
from pathlib import Path

root = Path(__file__).resolve().parents[1]
if os.name != "posix":
    raise SystemExit("Compose credentials require native Linux storage and POSIX permissions")

for directory in (root / ".runtime", root / ".runtime" / "secrets"):
    directory.mkdir(mode=0o700, exist_ok=True)
    info = directory.lstat()
    if (
        not stat.S_ISDIR(info.st_mode)
        or info.st_uid != os.geteuid()
        or stat.S_IMODE(info.st_mode) != 0o700
    ):
        raise SystemExit("Refusing non-private local credential directory")

for name in ("postgres_password", "migrator_password", "app_password"):
    path = directory / name
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except FileExistsError:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            info = os.fstat(descriptor)
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_uid != os.geteuid()
                or stat.S_IMODE(info.st_mode) != 0o600
                or info.st_nlink != 1
                or not 24 <= info.st_size <= 128
                or re.fullmatch(rb"[A-Za-z0-9_-]{24,128}", os.read(descriptor, 129)) is None
            ):
                raise SystemExit("Refusing invalid existing local credential")
        finally:
            os.close(descriptor)
    else:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(secrets.token_urlsafe(36))
print("Private local credentials prepared; values are not displayed")
