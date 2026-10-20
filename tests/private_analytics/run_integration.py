"""Real Docker/SPU acceptance plus explicitly authorized isolated correctness fixture.

Plaintext fixture values occur only in this test harness. No expected answer is
passed to the production analytics engine or stored in a RoomState.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engines/mpc"))
from analytics_contract import FIXED_POINT_TOLERANCE, metric_reveal, validate_child
from private_analytics import prepare, runtime_hashes
from room_state import ENVELOPE_MAGIC, load_room_state
from jsonschema import Draft202012Validator

WORKFLOW = ROOT / ".github/workflows/private-analytics.yml"
CODE = ROOT / "engines/mpc"


def run(args, env, check=True):
    result = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True, timeout=900)
    if check and result.returncode:
        # These are synthetic logs; redact identifiers even on failure.
        message = re.sub(r"P00[1-7]", "[synthetic-id]", (result.stdout + result.stderr)[-12000:])
        raise AssertionError(f"Command failed ({result.returncode}): {args}\n{message}")
    return result


def compose(files, project):
    args = ["docker", "compose", "-p", project]
    for f in files:
        args.extend(["-f", f])
    return args


def phase(args, env, expected_exit=0):
    command = [*args, "up", "--no-build"]
    # An expected non-zero exit is part of the assertion, not a Compose failure:
    # let both peers finish so one cannot SIGTERM the other during teardown.
    if expected_exit == 0:
        command.append("--abort-on-container-failure")
    result = run(command, env, check=False)
    payload = result.stdout + result.stderr
    assert not re.search(r"P00[1-7]", payload), "Identifier appeared in logs"
    records = []
    for line in payload.splitlines():
        candidate = line[line.find("{"):] if "{" in line else ""
        try:
            record = json.loads(candidate)
            if "roomStateId" in record or "status" in record:
                records.append(record)
        except json.JSONDecodeError:
            pass
    ids = run([*args, "ps", "-a", "-q"], env).stdout.split()
    assert len(ids) == 2
    for identifier in ids:
        code = int(run(["docker", "inspect", "-f", "{{.State.ExitCode}}", identifier], env).stdout)
        if code != expected_exit:
            safe_log = re.sub(r"P00[1-7]", "[synthetic-id]", payload[-16000:])
            raise AssertionError(f"Container exit {code}, expected {expected_exit}\n{safe_log}")
    assert len(records) == 2, records
    run([*args, "down"], env)
    assert not run([*args, "ps", "-q"], env).stdout.strip()
    return records


def snapshot(path):
    return {p.relative_to(path).as_posix(): p.read_bytes() for p in path.rglob("*") if p.is_file()}


def verify_state(root, state_id, count):
    state_dir = root / "rooms/cancer-collaboration-room/states" / state_id
    state = load_room_state(state_dir / "state.json")
    files = list(state_dir.rglob("*"))
    actual = {p.relative_to(state_dir).as_posix() for p in files if p.is_file()}
    expected = {"state.json", *(f"artifacts/{a.id}.share.enc" for a in state.artifacts)}
    assert actual == expected and len(state.artifacts) == count
    Draft202012Validator(json.loads((ROOT / "packages/manifests/room-state.schema.json").read_text())).validate(state.to_dict())
    assert not re.search(rb"P00[1-7]|patient_id|genomic_score|treatment_response", (state_dir / "state.json").read_bytes())
    for a in state.artifacts:
        assert not a.includes_identifiers and a.visibility == "secret-shared"
        assert (state_dir / f"artifacts/{a.id}.share.enc").read_bytes().startswith(ENVELOPE_MAGIC)
    return state


def scenario(all_outputs=False):
    with tempfile.TemporaryDirectory(prefix="kryptroom-m3-") as temporary:
        base = Path(temporary)
        roots = [base / p for p in ("lab-a", "lab-b")]
        for root in roots:
            root.mkdir()
        source_a, source_b = base / "a.csv", base / "b.csv"
        source_a.write_text("patient_id,genomic_score\nP001,10\nP002,20\nP003,30\nP004,40\n")
        source_b.write_text("patient_id,treatment_response\nP002,2\nP003,4\nP005,100\n")
        parent_job = json.loads((ROOT / "demos/cancer-collaboration/persistent-state-job.json").read_text())
        policy = parent_job["statePolicy"]
        policy["allowedOperators"] = ["private_analytics"]
        policy["allowedInputArtifactIds"] = ["match-mask", "lab-a-features", "lab-b-features"]
        spec = json.loads((ROOT / "demos/cancer-collaboration/analytics-job.json").read_text())
        # Correctness scenario explicitly opts in before S1 exists; acceptance reveals only mean-a.
        requested = ([metric_reveal(m) for m in spec["metrics"]] if all_outputs else spec["requestedReveals"])
        spec["requestedReveals"] = requested
        policy["authorizedReveals"].extend({"name": name, "recipients": ["lab-a", "lab-b"]} for name in requested)
        parent_path = base / "parent-job.json"
        parent_path.write_text(json.dumps(parent_job))
        job_path = base / "bound-job.json"
        env = dict(os.environ, KRYPTROOM_LAB_A_STATE_DIR=str(roots[0]), KRYPTROOM_LAB_B_STATE_DIR=str(roots[1]),
                   KRYPTROOM_M3_PARENT_JOB=str(parent_path), KRYPTROOM_M3_INPUT_A=str(source_a),
                   KRYPTROOM_M3_INPUT_B=str(source_b), KRYPTROOM_ANALYTICS_JOB=str(job_path))
        project = "m3-correctness" if all_outputs else "m3-acceptance"
        initial = compose(["compose.persistent-state.yml", "compose.private-analytics.persist.yml"], project + "-s1")
        analytics = compose(["compose.private-analytics.yml"], project)
        try:
            records = phase(initial, env)
            assert all(r["intersectionCardinality"] == 2 for r in records)
            s1 = [verify_state(root, "S1", 3) for root in roots]
            assert s1[0].to_dict() == s1[1].to_dict()
            original = [snapshot(root / "rooms/cancer-collaboration-room/states/S1") for root in roots]
            request = prepare(roots[0], spec, CODE, WORKFLOW)
            job_path.write_text(json.dumps(request))
            source_a.unlink()
            source_b.unlink()
            assert not source_a.exists() and not source_b.exists()
            config = json.loads(run([*analytics, "config", "--format", "json"], env).stdout)
            for name, service in config["services"].items():
                mounts = service["volumes"]
                assert not any(v["target"].startswith("/data") for v in mounts)
                assert not any(str(roots[1 if name == "lab-a" else 0]) == v["source"] for v in mounts)
            records = phase(analytics, env)
            assert all(r["outputsSecretShared"] and not r["plaintextJoinMaterialized"] and not r["sourceInputsAvailable"] for r in records)
            s2 = [verify_state(root, "S2", 6) for root in roots]
            assert s2[0].to_dict() == s2[1].to_dict()
            for c, p in zip(s2, s1):
                validate_child(c, p, *runtime_hashes(CODE, WORKFLOW))
            assert (roots[0] / "keys/room-state-v1.key").read_bytes() != (roots[1] / "keys/room-state-v1.key").read_bytes()
            env["KRYPTROOM_ANALYTICS_PHASE"] = "reveal"
            expected = {"analytics.count.matched-count": 2, "analytics.sum.sum-a": 50,
                        "analytics.sum.sum-b": 6, "analytics.mean.mean-a": 25,
                        "analytics.mean.mean-b": 3, "analytics.cross_mean.cross-ab": 80}
            for name in requested:
                env["KRYPTROOM_REVEAL_ARGUMENT"] = f"--reveal {name}"
                records = phase(analytics, env)
                for record in records:
                    assert record["stateReloaded"] and record["authorizedReveal"] == name
                    assert abs(record["value"] - expected[name]) <= FIXED_POINT_TOLERANCE
            if not all_outputs:
                env["KRYPTROOM_REVEAL_ARGUMENT"] = "--reveal analytics.cross_mean.cross-ab"
                records = phase(analytics, env, expected_exit=3)
                assert all(r["status"] == "REVEAL_OR_COMPUTATION_DENIED" and not r["reconstructionAttempted"] for r in records)
            for root, before in zip(roots, original):
                assert before == snapshot(root / "rooms/cancer-collaboration-room/states/S1")
                expected_paths = {"keys/room-state-v1.key"}
                for state in (s1[0], s2[0]):
                    prefix = f"rooms/{state.room_id}/states/{state.id}/"
                    expected_paths.add(prefix + "state.json")
                    expected_paths.update(prefix + f"artifacts/{a.id}.share.enc" for a in state.artifacts)
                assert set(snapshot(root)) == expected_paths, "Unexpected persisted intermediate material"
            print(json.dumps({"scenario": project, "realCheetahFm128": True,
                              "s1Unchanged": True, "s2Reloaded": True,
                              "onlyAuthorizedReveals": True, "plaintextJoinMaterialized": False}), flush=True)
        finally:
            run([*initial, "down"], env, check=False)
            run([*analytics, "down"], env, check=False)


if __name__ == "__main__":
    scenario()
    scenario(all_outputs=True)
