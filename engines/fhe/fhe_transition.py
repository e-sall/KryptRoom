"""Execute the authorized M6 ciphertext-to-ciphertext RoomState transition."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from fhe_contract import (
    CODE_FILES,
    EVALUATOR,
    OUTPUT_ARTIFACT_ID,
    OUTPUT_STATE_ID,
    PARTIES,
    artifact_from_file,
    artifact_uri,
    create_child_state,
    resolve_uri,
    source_hash,
    validate_spec,
    verify_artifact_file,
    verify_public_materials,
    workflow_hash,
)
from fhe_kernel import evaluate_vector_add

import sys

MPC_DIR = Path(__file__).resolve().parents[1] / "mpc"
if str(MPC_DIR) not in sys.path:
    sys.path.insert(0, str(MPC_DIR))
from room_state import load_room_state, write_room_state_exclusive  # noqa: E402


def parse_roots(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        holder, separator, root = value.partition("=")
        if not separator or not holder or holder in result:
            raise ValueError("Holder roots must use one unique holder=path entry")
        result[holder] = Path(root)
    if set(result) != {*PARTIES, EVALUATOR}:
        raise ValueError("M6 evaluation requires both ciphertext holders and evaluator")
    return result


def execute(
    *, parent_path: Path, spec_path: Path, child_path: Path, roots: dict[str, Path]
) -> None:
    repository = Path(__file__).resolve().parents[2]
    code_directory = Path(__file__).resolve().parent
    workflow = repository / ".github" / "workflows" / "fhe-state-transition.yml"
    parent = load_room_state(parent_path)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    # Policy, context, state commitment, and all persisted digests are checked
    # before OpenFHE receives ciphertext bytes.
    validate_spec(spec, parent)
    public_materials = verify_public_materials(parent.crypto_context, roots)
    input_paths = [
        verify_artifact_file(
            artifact,
            state_id=parent.id,
            holder=holder,
            context=parent.crypto_context,
            roots=roots,
        )
        for artifact, holder in zip(parent.artifacts, PARTIES, strict=True)
    ]
    output_uri = artifact_uri(EVALUATOR, OUTPUT_STATE_ID, OUTPUT_ARTIFACT_ID)
    output_path = resolve_uri(output_uri, roots)
    evaluate_vector_add(
        context_path=public_materials["openfhe-bgv-context"],
        left_path=input_paths[0],
        right_path=input_paths[1],
        output_path=output_path,
    )
    output = artifact_from_file(
        artifact_id=OUTPUT_ARTIFACT_ID,
        holder=EVALUATOR,
        state_id=OUTPUT_STATE_ID,
        path=output_path,
        context=parent.crypto_context,
    )
    child = create_child_state(
        parent,
        spec,
        output,
        source_hash(code_directory),
        workflow_hash(workflow),
    )
    write_room_state_exclusive(child, child_path)
    print(
        json.dumps(
            {
                "childStateCommitment": child.commitment.value,
                "childStateId": child.id,
                "homomorphicOperation": "OpenFHE.EvalAdd",
                "parentStateIds": list(child.parent_state_ids),
                "plaintextDecryptionDuringTransition": False,
                "requestedReveals": spec["requestedReveals"],
            },
            separators=(",", ":"),
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--child", type=Path, required=True)
    parser.add_argument("--holder-root", action="append", default=[], required=True)
    args = parser.parse_args()
    execute(
        parent_path=args.parent,
        spec_path=args.spec,
        child_path=args.child,
        roots=parse_roots(args.holder_root),
    )


if __name__ == "__main__":
    main()