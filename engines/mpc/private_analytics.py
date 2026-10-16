"""M3: persisted S1 -> real SPU scalar analytics -> persisted S2 -> separate reveal."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from analytics_contract import (
    INPUT_IDS, PARTIES, bind_request, digest, make_transition,
    output_id, safe_id, source_hash, validate_child, validate_request, workflow_hash,
)
from room_state import (
    ArtifactRef, CiphertextRef, EncryptedShareReader, EncryptedShareWriter,
    artifact_aad, canonical_json, create_room_state, inspect_ciphertexts,
    load_room_state, write_room_state_exclusive,
)

KEY_PATH = "keys/room-state-v1.key"


def directory(root, room, state):
    return root / "rooms" / safe_id(room) / "states" / safe_id(state)


def paths(root, state, ids):
    return {i: str(directory(root, state.room_id, state.id) / "artifacts" / f"{safe_id(i)}.share.enc")
            for i in ids}


def share_io(root, state, artifact_id, reader):
    cls = EncryptedShareReader if reader else EncryptedShareWriter
    path = paths(root, state, [artifact_id])[artifact_id]
    return [cls(path=path, key_path=str(root / KEY_PATH), aad=artifact_aad(
        room_id=state.room_id, state_id=state.id, artifact_id=artifact_id,
        party=party, crypto_context_id=state.crypto_context.id)) for party in PARTIES]


def verify_local(root, state, self_party):
    metadata = inspect_ciphertexts(paths(root, state, [a.id for a in state.artifacts]))
    for artifact in state.artifacts:
        descriptor = next(c for c in artifact.ciphertexts if c.party == self_party)
        if metadata[artifact.id] != {"sha256": descriptor.sha256, "sizeBytes": descriptor.size_bytes}:
            raise ValueError("Local ciphertext does not match exact ArtifactRef")


def verify_peer_state(state, parties, service):
    # Only already-public content hashes cross this boundary.
    hashes = service.metadata(lambda: [parties[p](lambda x: x)(state.commitment.value) for p in PARTIES])
    if hashes != [state.commitment.value, state.commitment.value]:
        raise ValueError("Participants hold different RoomStates")


def runtime_hashes(code_dir, workflow):
    return source_hash(code_dir), workflow_hash(workflow)


def prepare(root, spec, code_dir, workflow):
    safe_id(spec["roomId"])
    parent = load_room_state(directory(root, spec["roomId"], spec["inputStateIds"][0]) / "state.json")
    return bind_request(parent, spec, *runtime_hashes(code_dir, workflow))


def compute(self_party, root, request, code_dir, workflow):
    spec = request["spec"]
    parent_path = directory(root, spec["roomId"], spec["inputStateIds"][0]) / "state.json"
    parent_bytes = parent_path.read_bytes()
    parent = load_room_state(parent_path)
    validate_request(parent, request, *runtime_hashes(code_dir, workflow))
    verify_local(root, parent, self_party)
    output_path = directory(root, parent.room_id, spec["outputStateId"]) / "state.json"
    if output_path.exists():
        raise FileExistsError("RoomState S2 is immutable and already exists")

    import secretflow as sf
    from secretflow.device import SPUCompilerNumReturnsPolicy
    from private_join import create_devices
    from analytics_kernel import kernel_for
    from analytics_reveal import production_service

    if sf.__version__ != parent.crypto_context.backend_version:
        raise ValueError("SecretFlow runtime version mismatch")
    parties, spu = create_devices(self_party, spec["transitionId"])
    try:
        service = production_service(parent.policy, parties)
        verify_peer_state(parent, parties, service)
        requests = service.metadata(lambda: [parties[p](lambda x: x)(digest(request)) for p in PARTIES])
        if requests != [digest(request), digest(request)]:
            raise ValueError("Participants hold different analytics requests")
        # Loaded exclusively through native SPU.load and existing AES-GCM readers.
        inputs = [spu.load(share_io(root, parent, i, True)) for i in INPUT_IDS]
        outputs = spu(kernel_for(spec["metrics"]),
                      num_returns_policy=SPUCompilerNumReturnsPolicy.FROM_USER,
                      user_specified_num_returns=len(spec["metrics"]))(*inputs)
        # SPU returns a tuple even for a single user-specified output in this kernel.
        if len(spec["metrics"]) == 1 and not isinstance(outputs, (list, tuple)):
            outputs = [outputs]
        output_ids = [output_id(m) for m in spec["metrics"]]
        # A draft descriptor supplies only destination identity for the existing share writer.
        from dataclasses import replace
        destination = replace(parent, id=spec["outputStateId"])
        for artifact_id, secret in zip(output_ids, outputs, strict=True):
            spu.dump(secret, share_io(root, destination, artifact_id, False))
        metadata = service.metadata(lambda: [parties[p](inspect_ciphertexts)(
            paths(root, destination, output_ids)) for p in PARTIES])
        artifacts = []
        for metric, artifact_id in zip(spec["metrics"], output_ids, strict=True):
            artifacts.append(ArtifactRef(
                id=artifact_id, kind="spu-secret-share",
                media_type="application/vnd.kryptroom.spu-share+encrypted",
                visibility="secret-shared", crypto_context_id=parent.crypto_context.id,
                shape=(1,), dtype="int32" if metric["op"] == "COUNT" else "float32",
                includes_identifiers=False, ciphertexts=tuple(CiphertextRef(
                    party=p, uri=f"local://{p}/rooms/{parent.room_id}/states/{destination.id}/artifacts/{artifact_id}.share.enc",
                    sha256=metadata[index][artifact_id]["sha256"],
                    size_bytes=metadata[index][artifact_id]["sizeBytes"])
                    for index, p in enumerate(PARTIES))))
        artifacts = tuple(artifacts)
        child = create_room_state(
            state_id=destination.id, room_id=parent.room_id, parent_state_ids=(parent.id,),
            artifacts=artifacts, transition=make_transition(parent, request, artifacts),
            policy=parent.policy, crypto_context=parent.crypto_context)
        validate_child(child, parent, *runtime_hashes(code_dir, workflow))
        verify_peer_state(child, parties, service)
        write_room_state_exclusive(child, output_path)
        if parent_path.read_bytes() != parent_bytes:
            raise RuntimeError("Parent RoomState changed")
        return {"roomStateId": child.id, "stateCommitment": child.commitment.value,
                "parentStateCommitment": parent.commitment.value, "outputsSecretShared": True,
                "plaintextJoinMaterialized": False, "sourceInputsAvailable": Path("/data/local.csv").exists()}
    finally:
        sf.shutdown()


def reveal(self_party, root, request, name, code_dir, workflow):
    spec = request["spec"]
    parent = load_room_state(directory(root, spec["roomId"], spec["inputStateIds"][0]) / "state.json")
    child = load_room_state(directory(root, spec["roomId"], spec["outputStateId"]) / "state.json")
    validate_request(parent, request, *runtime_hashes(code_dir, workflow))
    committed_spec = validate_child(child, parent, *runtime_hashes(code_dir, workflow))
    if committed_spec != spec:
        raise ValueError("Reveal request differs from the committed analytics spec")
    # Deny before runtime creation as well as before any load or reconstruction.
    from analytics_reveal import RevealService
    RevealService(child.policy, {}, None, None).authorize(spec, name)
    verify_local(root, child, self_party)
    import secretflow as sf
    from private_join import create_devices
    from analytics_reveal import production_service
    if sf.__version__ != child.crypto_context.backend_version:
        raise ValueError("SecretFlow runtime version mismatch")
    parties, spu = create_devices(self_party, spec["transitionId"] + "-reveal")
    try:
        service = production_service(child.policy, parties)
        verify_peer_state(child, parties, service)
        value = service.scalar(spec, name, lambda i: spu.load(share_io(root, child, i, True)))
        return {"roomStateId": child.id, "stateReloaded": True, "authorizedReveal": name,
                "value": value, "plaintextJoinMaterialized": False}
    finally:
        sf.shutdown()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("prepare", "compute", "reveal"), required=True)
    parser.add_argument("--party", choices=PARTIES)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--job", type=Path, required=True)
    parser.add_argument("--workflow", type=Path, required=True)
    parser.add_argument("--reveal")
    args = parser.parse_args()
    job = json.loads(args.job.read_text())
    code_dir = Path(__file__).parent
    try:
        if args.phase == "prepare":
            result = prepare(args.state_root, job, code_dir, args.workflow)
        elif args.phase == "compute":
            result = compute(args.party, args.state_root, job, code_dir, args.workflow)
        else:
            result = reveal(args.party, args.state_root, job, args.reveal, code_dir, args.workflow)
    except PermissionError:
        print(json.dumps({"status": "REVEAL_OR_COMPUTATION_DENIED", "reconstructionAttempted": False}), flush=True)
        raise SystemExit(3)
    except ValueError as error:
        # Values/identifiers never appear in validation errors from the contracts.
        print(json.dumps({"status": "ANALYTICS_REJECTED", "reason": str(error)}), flush=True)
        raise SystemExit(2)
    print(canonical_json(result).decode(), flush=True)


if __name__ == "__main__":
    main()
