"""Encrypt one participant-local exact integer vector with public OpenFHE material."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from fhe_setup import BATCH_SIZE, CONTEXT_FILE, PUBLIC_KEY_FILE
from openfhe_backend import (
    deserialize_context,
    deserialize_public_key,
    load_openfhe,
    serialize_exclusive,
    sha256_file,
)


def read_private_input(path: Path) -> list[int]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(value, list)
        or len(value) != BATCH_SIZE
        or any(type(item) is not int or not -(2**15) <= item < 2**15 for item in value)
    ):
        raise ValueError("M6 requires exactly four bounded signed integers")
    return value


def encrypt(public_dir: Path, input_path: Path, output_path: Path) -> None:
    fhe = load_openfhe()
    context = deserialize_context(fhe, public_dir / CONTEXT_FILE)
    public_key = deserialize_public_key(fhe, public_dir / PUBLIC_KEY_FILE)
    plaintext = context.MakePackedPlaintext(read_private_input(input_path))
    ciphertext = context.Encrypt(public_key, plaintext)
    serialize_exclusive(fhe, ciphertext, output_path)
    print(
        json.dumps(
            {
                "artifactSha256": sha256_file(output_path),
                "artifactSizeBytes": output_path.stat().st_size,
                "encryptedElementCount": BATCH_SIZE,
                "plaintextLogged": False,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-dir", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    encrypt(args.public_dir, args.input, args.output)


if __name__ == "__main__":
    main()
