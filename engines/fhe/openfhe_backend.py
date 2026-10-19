"""Small, pinned OpenFHE serialization boundary used by M6."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import uuid
from pathlib import Path
from typing import Any

OPENFHE_PACKAGE_VERSION = "1.5.1.0.24.4"


def load_openfhe():
    import openfhe

    actual = importlib.metadata.version("openfhe")
    if actual != OPENFHE_PACKAGE_VERSION:
        raise RuntimeError(
            f"OpenFHE runtime version mismatch: expected {OPENFHE_PACKAGE_VERSION}"
        )
    return openfhe


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_exclusive(path: Path, value: Any, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
            json.dump(value, output, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def serialize_exclusive(fhe, value: Any, path: Path, mode: int = 0o600) -> None:
    """Serialize through OpenFHE and atomically claim a new immutable path."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".{path.name}.{uuid.uuid4().hex}.tmp"
    try:
        if not fhe.SerializeToFile(str(temporary), value, fhe.BINARY):
            raise RuntimeError("OpenFHE serialization failed")
        os.chmod(temporary, mode)
        with temporary.open("rb") as source:
            os.fsync(source.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def release_contexts(fhe) -> None:
    fhe.ClearEvalMultKeys()
    fhe.ReleaseAllContexts()


def deserialize_context(fhe, path: Path):
    release_contexts(fhe)
    context, ok = fhe.DeserializeCryptoContext(str(path), fhe.BINARY)
    if not ok:
        raise ValueError("OpenFHE crypto context deserialization failed")
    return context


def deserialize_public_key(fhe, path: Path):
    key, ok = fhe.DeserializePublicKey(str(path), fhe.BINARY)
    if not ok:
        raise ValueError("OpenFHE public key deserialization failed")
    return key


def deserialize_private_key(fhe, path: Path):
    key, ok = fhe.DeserializePrivateKey(str(path), fhe.BINARY)
    if not ok:
        raise ValueError("OpenFHE private key deserialization failed")
    return key


def deserialize_ciphertext(fhe, path: Path):
    ciphertext, ok = fhe.DeserializeCiphertext(str(path), fhe.BINARY)
    if not ok:
        raise ValueError("OpenFHE ciphertext deserialization failed")
    return ciphertext
