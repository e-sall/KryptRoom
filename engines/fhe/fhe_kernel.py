"""Secret-key-free OpenFHE evaluation kernel for the single M6 operation."""
from __future__ import annotations

from pathlib import Path

from openfhe_backend import (
    deserialize_ciphertext,
    deserialize_context,
    load_openfhe,
    serialize_exclusive,
)


def evaluate_vector_add(
    *, context_path: Path, left_path: Path, right_path: Path, output_path: Path
) -> None:
    fhe = load_openfhe()
    context = deserialize_context(fhe, context_path)
    left = deserialize_ciphertext(fhe, left_path)
    right = deserialize_ciphertext(fhe, right_path)
    result = context.EvalAdd(left, right)
    serialize_exclusive(fhe, result, output_path)