from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.mpc.room_state import canonical_json
from vector_builder import build_vectors


def main() -> None:
    proof, vectors = build_vectors()
    destination = ROOT / "tests/chain_anchor/fixtures"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "state-proof.json").write_bytes(canonical_json(proof) + b"\n")
    (destination / "vectors.json").write_bytes(canonical_json(vectors) + b"\n")


if __name__ == "__main__":
    main()
