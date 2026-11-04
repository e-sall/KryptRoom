"""Verify committed hash exports from uv.lock without changing them."""

import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
uv = shutil.which("uv")
if uv is None:
    raise SystemExit("Install the pinned dev toolchain first")
for name, options in (("requirements.lock", ["--no-dev"]), ("requirements-dev.lock", [])):
    expected = subprocess.check_output(  # noqa: S603 — fixed executable/options, no shell/input
        [
            uv,
            "export",
            "--frozen",
            "--no-header",
            "--no-emit-project",
            "--format",
            "requirements-txt",
            *options,
        ],
        cwd=root,
        text=True,
    )
    if (root / name).read_text(encoding="utf-8") != expected:
        raise SystemExit(f"{name} differs from uv.lock; regenerate the documented export")
print("Both committed hash exports match uv.lock")
