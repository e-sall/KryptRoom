"""Participant-owned M6 key generation; the private key never enters RoomState."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from openfhe_backend import (
    OPENFHE_PACKAGE_VERSION,
    load_openfhe,
    serialize_exclusive,
    sha256_file,
    write_json_exclusive,
)

PLAINTEXT_MODULUS = 65537
MULTIPLICATIVE_DEPTH = 0
BATCH_SIZE = 4
SECURITY_LEVEL = "HEStd_128_classic"
CONTEXT_FILE = "openfhe-bgv-context.bin"
PUBLIC_KEY_FILE = "openfhe-bgv-public-key.bin"


def create_material(public_dir: Path, private_key_path: Path, report_path: Path) -> None:
    fhe = load_openfhe()
    parameters = fhe.CCParamsBGVRNS()
    parameters.SetPlaintextModulus(PLAINTEXT_MODULUS)
    parameters.SetMultiplicativeDepth(MULTIPLICATIVE_DEPTH)
    parameters.SetBatchSize(BATCH_SIZE)
    parameters.SetSecurityLevel(fhe.HEStd_128_classic)

    context = fhe.GenCryptoContext(parameters)
    context.Enable(fhe.PKESchemeFeature.PKE)
    context.Enable(fhe.PKESchemeFeature.LEVELEDSHE)
    key_pair = context.KeyGen()

    context_path = public_dir / CONTEXT_FILE
    public_key_path = public_dir / PUBLIC_KEY_FILE
    serialize_exclusive(fhe, context, context_path, 0o644)
    serialize_exclusive(fhe, key_pair.publicKey, public_key_path, 0o644)
    serialize_exclusive(fhe, key_pair.secretKey, private_key_path, 0o600)

    report = {
        "backend": "OpenFHE",
        "backendVersion": OPENFHE_PACKAGE_VERSION,
        "scheme": "BGV-RNS",
        "keyEpoch": "fhe-key-epoch-1",
        "keyOwner": "lab-a",
        "parameters": {
            "plaintextModulus": PLAINTEXT_MODULUS,
            "multiplicativeDepth": MULTIPLICATIVE_DEPTH,
            "batchSize": BATCH_SIZE,
            "securityLevel": SECURITY_LEVEL,
            "ringDimension": int(context.GetRingDimension()),
            "serialization": "BINARY",
            "operationSet": ["EvalAdd"],
        },
        "publicMaterials": [
            {
                "id": "openfhe-bgv-context",
                "kind": "crypto-context",
                "fileName": CONTEXT_FILE,
                "sha256": sha256_file(context_path),
                "sizeBytes": context_path.stat().st_size,
            },
            {
                "id": "openfhe-bgv-public-key",
                "kind": "public-key",
                "fileName": PUBLIC_KEY_FILE,
                "sha256": sha256_file(public_key_path),
                "sizeBytes": public_key_path.stat().st_size,
            },
        ],
        "evaluationMaterials": [],
    }
    write_json_exclusive(report_path, report, 0o644)
    print(
        json.dumps(
            {
                "backend": "OpenFHE",
                "backendVersion": OPENFHE_PACKAGE_VERSION,
                "scheme": "BGV-RNS",
                "ringDimension": report["parameters"]["ringDimension"],
                "privateKeyOwner": "lab-a",
                "privateKeyPersistedNodeLocally": True,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-dir", type=Path, required=True)
    parser.add_argument("--private-key", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    create_material(args.public_dir, args.private_key, args.report)


if __name__ == "__main__":
    main()