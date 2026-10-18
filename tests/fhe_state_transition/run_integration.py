"""Real OpenFHE M6 persistence/restart/policy acceptance chain."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FHE = ROOT / "engines" / "fhe"
MPC = ROOT / "engines" / "mpc"
sys.path[:0] = [str(FHE), str(MPC)]

from fhe_contract import (
    EVALUATOR,
    INPUT_ARTIFACT_IDS,
    INPUT_STATE_ID,
    OUTPUT_ARTIFACT_ID,
    OUTPUT_STATE_ID,
    PARTIES,
    REVEAL_NAME,
    artifact_from_file,
    artifact_uri,
    context_from_report,
    create_initial_state,
    resolve_uri,
    source_hash,
    validate_child,
    verify_artifact_file,
    workflow_hash,
)
from room_state import create_room_state, load_room_state, write_room_state_exclusive


def run(command: list[str], *, success: bool = True, contains: str | None = None):
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    combined = result.stdout + result.stderr
    if success and result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}):\n{combined[-4000:]}")
    if not success and result.returncode == 0:
        raise RuntimeError("Negative M6 command unexpectedly succeeded")
    if contains is not None and contains not in combined:
        raise RuntimeError(f"Expected failure marker was absent: {contains!r}\n{combined[-2000:]}")
    return result


def main() -> None:
    temporary_root = ROOT / "build" / "m6-integration"
    temporary_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="kryptroom-m6-", dir=temporary_root) as temporary:
        root = Path(temporary)
        holder_roots = {holder: root / "artifacts" / holder for holder in (*PARTIES, EVALUATOR)}
        private_roots = {holder: root / "private" / holder for holder in PARTIES}
        key_owner_root = root / "key-owner-lab-a"
        control_root = root / "control-plane"
        for directory in (*holder_roots.values(), *private_roots.values(), key_owner_root, control_root):
            directory.mkdir(parents=True)

        public_dir = holder_roots[EVALUATOR] / "crypto"
        private_key = key_owner_root / "keys" / "fhe-key-epoch-1.openfhe.bin"
        report_path = public_dir / "context-report.json"
        run(
            [
                sys.executable,
                str(FHE / "fhe_setup.py"),
                "--public-dir",
                str(public_dir),
                "--private-key",
                str(private_key),
                "--report",
                str(report_path),
            ]
        )
        assert private_key.exists() and private_key.stat().st_size > 0
        assert private_key.resolve() not in [path.resolve() for path in holder_roots.values()]

        vectors = {"lab-a": [3, 5, 7, 11], "lab-b": [13, 17, 19, 23]}
        expected = [16, 22, 26, 34]
        ciphertext_paths: dict[str, Path] = {}
        for holder, identifier in zip(PARTIES, INPUT_ARTIFACT_IDS, strict=True):
            input_path = private_roots[holder] / "input" / "vector.json"
            input_path.parent.mkdir(parents=True)
            input_path.write_text(json.dumps(vectors[holder], separators=(",", ":")), encoding="utf-8")
            output_path = resolve_uri(
                artifact_uri(holder, INPUT_STATE_ID, identifier), holder_roots
            )
            run(
                [
                    sys.executable,
                    str(FHE / "fhe_encrypt.py"),
                    "--public-dir",
                    str(public_dir),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                ]
            )
            ciphertext_paths[holder] = output_path

        # The control-plane state is created from ciphertext descriptors only.
        context = context_from_report(json.loads(report_path.read_text(encoding="utf-8")))
        artifacts = tuple(
            artifact_from_file(
                artifact_id=identifier,
                holder=holder,
                state_id=INPUT_STATE_ID,
                path=ciphertext_paths[holder],
                context=context,
            )
            for holder, identifier in zip(PARTIES, INPUT_ARTIFACT_IDS, strict=True)
        )
        parent = create_initial_state(context, artifacts)
        parent_path = control_root / "states" / INPUT_STATE_ID / "state.json"
        write_room_state_exclusive(parent, parent_path)
        parent_state_bytes = parent_path.read_bytes()

        # Terminate the logical input phase: separate processes have exited and
        # participant plaintext fixture files are removed before evaluation.
        for directory in private_roots.values():
            shutil.rmtree(directory)
        del vectors, context, artifacts, parent

        spec_path = ROOT / "demos" / "cancer-collaboration" / "m6" / "fhe-vector-add-job.json"
        child_path = control_root / "states" / OUTPUT_STATE_ID / "state.json"
        holder_arguments = [
            item
            for holder, path in holder_roots.items()
            for item in ("--holder-root", f"{holder}={path}")
        ]
        transition = [
            sys.executable,
            str(FHE / "fhe_transition.py"),
            "--parent",
            str(parent_path),
            "--spec",
            str(spec_path),
            "--child",
            str(child_path),
            *holder_arguments,
        ]

        # A policy-valid state commitment with the operator removed must fail
        # before any ciphertext output is created.
        parent = load_room_state(parent_path)
        blocked = create_room_state(
            state_id=parent.id,
            room_id=parent.room_id,
            parent_state_ids=parent.parent_state_ids,
            artifacts=parent.artifacts,
            transition=parent.transition,
            policy=replace(parent.policy, allowed_operators=()),
            crypto_context=parent.crypto_context,
        )
        blocked_path = control_root / "negative" / "blocked-state.json"
        write_room_state_exclusive(blocked, blocked_path)
        blocked_command = transition.copy()
        blocked_command[blocked_command.index(str(parent_path))] = str(blocked_path)
        run(blocked_command, success=False, contains="default-deny state policy")
        assert not child_path.exists()

        # Byte tampering is rejected by the ArtifactRef digest before OpenFHE.
        left_path = ciphertext_paths["lab-a"]
        original_left = left_path.read_bytes()
        left_path.write_bytes(original_left + b"tampered")
        run(transition, success=False, contains="commitment verification failed")
        assert not child_path.exists()
        left_path.write_bytes(original_left)

        transition_result = run(transition)
        transition_record = json.loads(transition_result.stdout.strip().splitlines()[-1])
        assert transition_record["homomorphicOperation"] == "OpenFHE.EvalAdd"
        assert transition_record["plaintextDecryptionDuringTransition"] is False
        assert transition_record["requestedReveals"] == []

        child = load_room_state(child_path)
        parent = load_room_state(parent_path)
        validate_child(
            child,
            parent,
            source_hash(FHE),
            workflow_hash(ROOT / ".github/workflows/fhe-state-transition.yml"),
        )
        assert child.parent_state_ids == (INPUT_STATE_ID,)
        assert child.id == OUTPUT_STATE_ID
        assert parent_path.read_bytes() == parent_state_bytes

        reveal_base = [
            sys.executable,
            str(FHE / "fhe_reveal.py"),
            "--parent",
            str(parent_path),
            "--child",
            str(child_path),
            "--reveal-name",
            REVEAL_NAME,
            "--holder-root",
            f"{EVALUATOR}={holder_roots[EVALUATOR]}",
        ]
        # Authorization must fail before attempting to read this absent key.
        run(
            [
                *reveal_base,
                "--private-key",
                str(root / "does-not-exist.key"),
                "--recipient",
                "ui",
            ],
            success=False,
            contains="does not authorize FHE decryption",
        )

        authorized = run(
            [
                *reveal_base,
                "--private-key",
                str(private_key),
                "--recipient",
                "lab-a",
                "--recipient",
                "lab-b",
            ]
        )
        reveal = json.loads(authorized.stdout.strip().splitlines()[-1])
        assert reveal["value"] == expected

        # Child ciphertext tampering is detected before decryption.
        output_path = resolve_uri(child.artifacts[0].ciphertexts[0].uri, holder_roots)
        original_output = output_path.read_bytes()
        output_path.write_bytes(original_output[:-1] + bytes([original_output[-1] ^ 1]))
        run(
            [
                *reveal_base,
                "--private-key",
                str(private_key),
                "--recipient",
                "lab-a",
                "--recipient",
                "lab-b",
            ],
            success=False,
            contains="commitment verification failed",
        )
        output_path.write_bytes(original_output)

        # The key remains exclusively in the participant-owned root. Shared
        # state and ciphertext storage contain neither key bytes nor plaintext vectors.
        private_key_bytes = private_key.read_bytes()
        forbidden_plaintexts = (b"[3,5,7,11]", b"[13,17,19,23]")
        for shared_root in (*holder_roots.values(), control_root):
            for path in shared_root.rglob("*"):
                if path.is_file():
                    payload = path.read_bytes()
                    assert private_key_bytes not in payload
                    assert not any(value in payload for value in forbidden_plaintexts)
        states = [path.relative_to(control_root).as_posix() for path in control_root.rglob("state.json")]
        assert sorted(states) == [
            "states/S5_fhe_inputs/state.json",
            "states/S6_fhe_sum/state.json",
        ]
        assert not any(path.exists() for path in private_roots.values())
        assert b"private-key" not in parent_path.read_bytes() + child_path.read_bytes()
        assert b"fhe-key-epoch-1.openfhe.bin" not in parent_path.read_bytes() + child_path.read_bytes()

        verified_output = verify_artifact_file(
            child.artifacts[0],
            state_id=child.id,
            holder=EVALUATOR,
            context=child.crypto_context,
            roots=holder_roots,
        )
        print(
            json.dumps(
                {
                    "authorizedResult": expected,
                    "backend": "OpenFHE",
                    "backendVersion": "1.5.1.0.24.4",
                    "childStateCommitment": child.commitment.value,
                    "childStateId": child.id,
                    "ciphertextSha256": child.artifacts[0].ciphertexts[0].sha256,
                    "homomorphicOperation": "EvalAdd",
                    "inputStateId": parent.id,
                    "noPlaintextIntermediatePersisted": True,
                    "privateKeyInControlPlane": False,
                    "restartReloadContinuity": True,
                    "scheme": "BGV-RNS",
                    "verifiedCiphertextBytes": verified_output.stat().st_size,
                },
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        print("M6_REAL_OPENFHE_ACCEPTANCE_PASSED")


if __name__ == "__main__":
    main()
