"""Authoritative real M4 S1 -> S3 -> restart -> S4 -> restart -> reveal gate."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "engines/mpc"
WORKFLOW = ROOT / ".github/workflows/private-nn.yml"
sys.path.insert(0, str(CODE))

from jsonschema import Draft202012Validator
from nn_contract import (
    EVALUATION_ID, EVALUATION_REVEAL, MODEL_IDS, bind_evaluation_request,
    validate_evaluation_child, validate_training_child,
)
from private_nn import prepare_evaluation, prepare_training, runtime_hashes
from room_state import ENVELOPE_MAGIC, load_room_state

SYNTHETIC_IDENTIFIERS = (
    "p1", "p2", "p3", "p4", "p5", "p6",
    "a-only-1", "a-only-2", "b-only-1", "b-only-2",
)


def run(args, env, check=True):
    result = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True, timeout=1200)
    if check and result.returncode:
        payload = result.stdout + result.stderr
        for identifier in SYNTHETIC_IDENTIFIERS:
            payload = payload.replace(identifier, "[synthetic-id]")
        raise AssertionError(f"Command failed ({result.returncode}): {args}\n{payload[-16000:]}")
    return result


def compose(files, project):
    args = ["docker", "compose", "-p", project]
    for filename in files:
        args.extend(["-f", filename])
    return args


def phase(args, env, expected_exit=0):
    result = run([*args, "up", "--no-build", "--abort-on-container-failure"], env, check=False)
    payload = result.stdout + result.stderr
    for identifier in SYNTHETIC_IDENTIFIERS:
        assert not re.search(rf"(?<![A-Za-z0-9_-]){re.escape(identifier)}(?![A-Za-z0-9_-])", payload), (
            "Synthetic identifier appeared in M4 logs"
        )
    assert "patient_id" not in payload and "genomic_score" not in payload
    records = []
    for line in payload.splitlines():
        candidate = line[line.find("{"):] if "{" in line else ""
        try:
            record = json.loads(candidate)
            if "roomStateId" in record or "status" in record:
                records.append(record)
        except json.JSONDecodeError:
            pass
    containers = run([*args, "ps", "-a", "-q"], env).stdout.split()
    assert len(containers) == 2
    for container in containers:
        code = int(run(["docker", "inspect", "-f", "{{.State.ExitCode}}", container], env).stdout)
        if code != expected_exit:
            raise AssertionError(f"Container exit {code}, expected {expected_exit}")
    assert len(records) == 2, records
    run([*args, "down"], env)
    assert not run([*args, "ps", "-q"], env).stdout.strip()
    return records


def snapshot(path):
    return {p.relative_to(path).as_posix(): p.read_bytes() for p in path.rglob("*") if p.is_file()}


def verify_state(root, state_id, artifact_ids):
    state_dir = root / "rooms/cancer-collaboration-room/states" / state_id
    state = load_room_state(state_dir / "state.json")
    expected = {"state.json", *(f"artifacts/{identifier}.share.enc" for identifier in artifact_ids)}
    actual = {p.relative_to(state_dir).as_posix() for p in state_dir.rglob("*") if p.is_file()}
    assert actual == expected
    assert tuple(a.id for a in state.artifacts) == tuple(artifact_ids)
    schema = json.loads((ROOT / "packages/manifests/room-state.schema.json").read_text())
    Draft202012Validator(schema).validate(state.to_dict())
    public = (state_dir / "state.json").read_text()
    # The required public model interpretation contains the words
    # normalized_continuous_treatment_response; that is specification metadata,
    # not the participant source column or any private label value.
    assert "patient_id" not in public and "genomic_score" not in public
    assert not any(identifier in public for identifier in SYNTHETIC_IDENTIFIERS)
    for artifact in state.artifacts:
        payload = (state_dir / f"artifacts/{artifact.id}.share.enc").read_bytes()
        assert payload.startswith(ENVELOPE_MAGIC)
        assert artifact.visibility == "secret-shared" and not artifact.includes_identifiers
    return state


def assert_local_descriptors(roots, states):
    for party_index, (root, state) in enumerate(zip(roots, states, strict=True)):
        for artifact in state.artifacts:
            path = root / f"rooms/{state.room_id}/states/{state.id}/artifacts/{artifact.id}.share.enc"
            local = next(c for c in artifact.ciphertexts if c.party == ("lab-a", "lab-b")[party_index])
            import hashlib
            payload = path.read_bytes()
            assert hashlib.sha256(payload).hexdigest() == local.sha256
            assert len(payload) == local.size_bytes
    for artifact in states[0].artifacts:
        a = roots[0] / f"rooms/{states[0].room_id}/states/{states[0].id}/artifacts/{artifact.id}.share.enc"
        b = roots[1] / f"rooms/{states[1].room_id}/states/{states[1].id}/artifacts/{artifact.id}.share.enc"
        assert a.read_bytes() != b.read_bytes(), "Nodes must retain distinct local encrypted shares"


def main():
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="kryptroom-m4-") as temporary:
        base = Path(temporary)
        roots = [base / "lab-a", base / "lab-b"]
        for root in roots:
            root.mkdir()
        source_a, source_b = base / "lab-a-source.csv", base / "lab-b-source.csv"
        shutil.copyfile(ROOT / "demos/cancer-collaboration/m4/lab-a/private-join.csv", source_a)
        shutil.copyfile(ROOT / "demos/cancer-collaboration/m4/lab-b/private-join.csv", source_b)
        join_job = ROOT / "demos/cancer-collaboration/m4/private-join-job.json"
        state_job = ROOT / "demos/cancer-collaboration/m4/persistent-state-job.json"
        manifest_path = ROOT / "demos/cancer-collaboration/m4/private-nn-job.json"
        manifest = json.loads(manifest_path.read_text())
        request_path = base / "bound-request.json"
        request_path.write_text("{}")
        env = dict(
            os.environ,
            KRYPTROOM_LAB_A_STATE_DIR=str(roots[0]),
            KRYPTROOM_LAB_B_STATE_DIR=str(roots[1]),
            KRYPTROOM_M4_JOIN_JOB=str(join_job),
            KRYPTROOM_M4_STATE_JOB=str(state_job),
            KRYPTROOM_M4_INPUT_A=str(source_a),
            KRYPTROOM_M4_INPUT_B=str(source_b),
            KRYPTROOM_NN_MANIFEST=str(manifest_path),
            KRYPTROOM_NN_REQUEST=str(request_path),
        )
        initial = compose(["compose.persistent-state.yml", "compose.private-nn.persist.yml"], "m4-s1")
        runtime = compose(["compose.private-nn.yml"], "m4-private-nn")
        try:
            records = phase(initial, env)
            assert all(record["intersectionCardinality"] == 6 for record in records)
            s1 = [verify_state(root, "S1", ("match-mask", "lab-a-features", "lab-b-features"))
                  for root in roots]
            assert s1[0].to_dict() == s1[1].to_dict()
            s1_before = [snapshot(root / "rooms/cancer-collaboration-room/states/S1") for root in roots]
            training_request = prepare_training(roots[0], manifest, CODE, WORKFLOW)
            request_path.write_text(json.dumps(training_request))
            source_a.unlink()
            source_b.unlink()
            assert not source_a.exists() and not source_b.exists()
            config = json.loads(run([*runtime, "config", "--format", "json"], env).stdout)
            for name, service in config["services"].items():
                assert not any(volume["target"].startswith("/data") for volume in service["volumes"])
                peer = roots[1 if name == "lab-a" else 0]
                assert not any(Path(volume["source"]) == peer for volume in service["volumes"])

            env["KRYPTROOM_NN_PHASE"] = "train"
            records = phase(runtime, env)
            assert all(record["modelParametersSecretShared"] and record["trainingReveals"] == 0
                       and not record["plaintextJoinMaterialized"]
                       and not record["sourceInputsAvailable"] for record in records)
            s3 = [verify_state(root, "S3_model", MODEL_IDS) for root in roots]
            assert s3[0].to_dict() == s3[1].to_dict()
            validate_training_child(s3[0], s1[0], manifest, *runtime_hashes(CODE, WORKFLOW))
            assert_local_descriptors(roots, s3)
            s3_before = [snapshot(root / "rooms/cancer-collaboration-room/states/S3_model") for root in roots]
            for root, before in zip(roots, s1_before, strict=True):
                assert snapshot(root / "rooms/cancer-collaboration-room/states/S1") == before

            evaluation_request = prepare_evaluation(roots[0], manifest, CODE, WORKFLOW)
            request_path.write_text(json.dumps(evaluation_request))
            env["KRYPTROOM_NN_PHASE"] = "evaluate"
            records = phase(runtime, env)
            assert all(record["evaluationSecretShared"] and not record["predictionsPersisted"]
                       and not record["plaintextJoinMaterialized"]
                       and not record["sourceInputsAvailable"] for record in records)
            s4 = [verify_state(root, "S4_eval", (EVALUATION_ID,)) for root in roots]
            assert s4[0].to_dict() == s4[1].to_dict()
            validate_evaluation_child(
                s4[0], s3[0], s1[0], manifest, *runtime_hashes(CODE, WORKFLOW)
            )
            assert_local_descriptors(roots, s4)
            for index, root in enumerate(roots):
                assert snapshot(root / "rooms/cancer-collaboration-room/states/S1") == s1_before[index]
                assert snapshot(root / "rooms/cancer-collaboration-room/states/S3_model") == s3_before[index]

            env["KRYPTROOM_NN_PHASE"] = "reveal"
            for denied in (MODEL_IDS[0], "model.evaluation.rmse"):
                env["KRYPTROOM_REVEAL_ARGUMENT"] = f"--reveal {denied}"
                records = phase(runtime, env, expected_exit=3)
                assert all(record == {"status": "M4_DENIED", "artifactLoadedForReveal": False,
                                      "transferAttempted": False, "reconstructionAttempted": False}
                           for record in records)

            env["KRYPTROOM_REVEAL_ARGUMENT"] = f"--reveal {EVALUATION_REVEAL}"
            records = phase(runtime, env)
            values = [float(record["value"]) for record in records]
            assert values[0] == values[1]
            assert values[0] < 0.02
            assert all(record["stateReloaded"] and not record["plaintextJoinMaterialized"]
                       and not record["sourceInputsAvailable"] for record in records)

            for root, before in zip(roots, s1_before, strict=True):
                assert snapshot(root / "rooms/cancer-collaboration-room/states/S1") == before
            for root, before in zip(roots, s3_before, strict=True):
                assert snapshot(root / "rooms/cancer-collaboration-room/states/S3_model") == before
            for root in roots:
                expected = {"keys/room-state-v1.key"}
                for state in (s1[0], s3[0], s4[0]):
                    prefix = f"rooms/{state.room_id}/states/{state.id}/"
                    expected.add(prefix + "state.json")
                    expected.update(prefix + f"artifacts/{a.id}.share.enc" for a in state.artifacts)
                assert set(snapshot(root)) == expected, "Unexpected intermediate or plaintext material"
            elapsed = round(time.monotonic() - started, 3)
            # The authorized value is deliberately not copied into public CI logs.
            print(json.dumps({
                "scenario": "m4-authoritative", "realCheetahFm128": True,
                "jaxAutodiffTraining": True, "s1Unchanged": True,
                "s3Reloaded": True, "s3Unchanged": True, "s4Reloaded": True,
                "mseBelowPointZeroTwo": True, "onlyAuthorizedReveal": True,
                "plaintextJoinMaterialized": False, "sourceInputsAvailableAfterS1": False,
                "runtimeSeconds": elapsed,
            }), flush=True)
        finally:
            run([*initial, "down"], env, check=False)
            run([*runtime, "down"], env, check=False)


if __name__ == "__main__":
    main()
