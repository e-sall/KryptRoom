"""Generate local-only credentials with exclusive creation; never overwrite existing secrets."""

import os
import secrets
from pathlib import Path

directory = Path(__file__).resolve().parents[1] / ".runtime" / "secrets"
directory.mkdir(mode=0o700, parents=True, exist_ok=True)
for name in ("postgres_password", "migrator_password", "app_password"):
    path = directory / name
    if path.exists():
        continue
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(secrets.token_urlsafe(36))
print("Local credentials prepared; restrict directory ACLs on Windows. Values are not displayed.")
