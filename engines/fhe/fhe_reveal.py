"""Explicit participant-owned decryption boundary for the M6 result only."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fhe_contract import (
    EVALUATOR,
    PARTIES,
    REVEAL_NAME,
    source_hash,
    validate_child,
    verify_artifact_file,
    verify_public_materials,
    workflow_hash,
)
from openfhe_backend import (
    deserialize_ciphertext,
    deserialize_context,
    deserialize_private_key,
    load_openfhe,
)

MPC_DIR = Path(__file__).resolve().parents[1] / "mpc"
if str(MPC_DIR) not in sys.path:
    sys.path.insert(0, str(MPC_DIR))
from room_state import RoomState, load_room_state  # noqa: E402


class FHERevealService:
    def reveal_vector(
        self,
        *,
        parent: RoomState,
        child: RoomState,
        reveal_name: str,
        recipients: tuple[str, ...],
        roots: dict[str, Path],
        private_key_path: Path,
    ) -> list[int]:
        repository = Path(__file__).resolve().parents[2]
        validate_child(
            child,
            parent,
            source_hash(Path(__file__).resolve().parent),
            workflow_hash(
                repository / ".github" / "workflows" / "fhe-state-transition.yml"
            ),
        )
        # Authorization precedes all ciphertext, public-material, and private-key IO.
        if recipients != PARTIES or reveal_name != REVEAL_NAME or not child.policy.authorizes(
            reveal_name, recipients
        ):
            raise PermissionError("State policy does not authorize FHE decryption")
        private = private_key_path.resolve()
        if any(root.resolve() == private or root.resolve() in private.parents for root in roots.values()):
            raise ValueError("Private decryption material entered a shared artifact root")

        materials = verify_public_materials(child.crypto_context, roots)
        ciphertext_path = verify_artifact_file(
            child.artifacts[0],
            state_id=child.id,
            holder=EVALUATOR,
            context=child.crypto_context,
            roots=roots,
        )
        fhe = load_openfhe()
        context = deserialize_context(fhe, materials["openfhe-bgv-context"])
        ciphertext = deserialize_ciphertext(fhe, ciphertext_path)
        private_key = deserialize_private_key(fhe, private_key_path)
        plaintext = context.Decrypt(private_key, ciphertext)
        plaintext.SetLength(child.artifacts[0].shape[0])
        return [int(value) for value in plaintext.GetPackedValue()]


def parse_roots(values: list[str]) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for value in values:
        holder, separator, root = value.partition("=")
        if not separator or not holder or holder in roots:
            raise ValueError("Holder roots must use one unique holder=path entry")
        roots[holder] = Path(root)
    if EVALUATOR not in roots:
        raise ValueError("Reveal requires the evaluator ciphertext/public-material root")
    return roots


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--child", type=Path, required=True)
    parser.add_argument("--private-key", type=Path, required=True)
    parser.add_argument("--reveal-name", required=True)
    parser.add_argument("--recipient", action="append", default=[], required=True)
    parser.add_argument("--holder-root", action="append", default=[], required=True)
    args = parser.parse_args()
    result = FHERevealService().reveal_vector(
        parent=load_room_state(args.parent),
        child=load_room_state(args.child),
        reveal_name=args.reveal_name,
        recipients=tuple(args.recipient),
        roots=parse_roots(args.holder_root),
        private_key_path=args.private_key,
    )
    print(
        json.dumps(
            {
                "authorizedRecipients": list(args.recipient),
                "reveal": args.reveal_name,
                "value": result,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
