"""M4: persisted S1 -> secret NN S3 -> restart -> secret evaluation S4 -> reveal."""
from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from nn_contract import (
    EVALUATION_ID, EVALUATION_REVEAL, INPUT_IDS, MODEL_IDS, MODEL_SHAPES, PARTIES,
    bind_evaluation_request, bind_training_request, derive_evaluation_policy,
    derive_model_policy, digest, initializer_values, make_evaluation_transition,
    make_training_transition, source_hash, validate_evaluation_child,
    validate_evaluation_request, validate_job, validate_training_child,
    validate_training_request, workflow_hash,
)
from private_analytics import directory, paths, share_io, verify_local, verify_peer_state
from room_state import (
    ArtifactRef, CiphertextRef, canonical_json, create_room_state,
    inspect_ciphertexts, load_room_state, write_room_state_exclusive,
)


def runtime_hashes(code_dir, workflow):
    return source_hash(code_dir), workflow_hash(workflow)


def _load(root, room, state_id):
    return load_room_state(directory(root, room, state_id) / "state.json")


def prepare_training(root, job, code_dir, workflow):
    validate_job(job)
    parent = _load(root, job["roomId"], job["trainingTransition"]["inputStateIds"][0])
    return bind_training_request(parent, job, *runtime_hashes(code_dir, workflow))


def prepare_evaluation(root, job, code_dir, workflow):
    validate_job(job)
    model_id, data_id = job["evaluationTransition"]["inputStateIds"]
    model_state = _load(root, job["roomId"], model_id)
    data_state = _load(root, job["roomId"], data_id)
    return bind_evaluation_request(
        model_state, data_state, job, *runtime_hashes(code_dir, workflow)
    )


def _artifacts(metadata, parties, room, state_id, context_id, ids, shapes):
    result = []
    for artifact_id, shape in zip(ids, shapes, strict=True):
        result.append(ArtifactRef(
            id=artifact_id, kind="spu-secret-share",
            media_type="application/vnd.kryptroom.spu-share+encrypted",
            visibility="secret-shared", crypto_context_id=context_id,
            shape=tuple(shape), dtype="float32", includes_identifiers=False,
            ciphertexts=tuple(CiphertextRef(
                party=party,
                uri=f"local://{party}/rooms/{room}/states/{state_id}/artifacts/{artifact_id}.share.enc",
                sha256=metadata[index][artifact_id]["sha256"],
                size_bytes=metadata[index][artifact_id]["sizeBytes"],
            ) for index, party in enumerate(parties)),
        ))
    return tuple(result)


def train(self_party, root, request, job, code_dir, workflow):
    parent = _load(root, job["roomId"], request["parentStateId"])
    parent_path = directory(root, parent.room_id, parent.id) / "state.json"
    parent_bytes = parent_path.read_bytes()
    validate_training_request(parent, request, job, *runtime_hashes(code_dir, workflow))
    verify_local(root, parent, self_party)
    output_id = request["outputStateId"]
    output_path = directory(root, parent.room_id, output_id) / "state.json"
    if output_path.exists():
        raise FileExistsError("RoomState S3_model is immutable and already exists")

    import secretflow as sf
    from secretflow.device import SPUCompilerNumReturnsPolicy
    from analytics_reveal import production_service
    from nn_kernel import training_kernel_for
    from private_join import create_devices

    if sf.__version__ != parent.crypto_context.backend_version:
        raise ValueError("SecretFlow runtime version mismatch")
    parties, spu = create_devices(self_party, request["transition"]["transitionId"])
    try:
        service = production_service(parent.policy, parties)
        verify_peer_state(parent, parties, service)
        hashes = service.metadata(lambda: [
            parties[p](lambda value: value)(digest(request)) for p in PARTIES
        ])
        if hashes != [digest(request), digest(request)]:
            raise ValueError("Participants hold different training requests")
        inputs = [spu.load(share_io(root, parent, artifact_id, True)) for artifact_id in INPUT_IDS]
        outputs = spu(
            training_kernel_for(request["trainingSpec"], initializer_values(request["trainingSpec"])),
            num_returns_policy=SPUCompilerNumReturnsPolicy.FROM_USER,
            user_specified_num_returns=4,
        )(*inputs)
        destination = replace(parent, id=output_id)
        for artifact_id, secret in zip(MODEL_IDS, outputs, strict=True):
            spu.dump(secret, share_io(root, destination, artifact_id, False))
        metadata = service.metadata(lambda: [
            parties[p](inspect_ciphertexts)(paths(root, destination, MODEL_IDS)) for p in PARTIES
        ])
        artifacts = _artifacts(
            metadata, PARTIES, parent.room_id, output_id, parent.crypto_context.id,
            MODEL_IDS, MODEL_SHAPES,
        )
        child = create_room_state(
            state_id=output_id, room_id=parent.room_id, parent_state_ids=(parent.id,),
            artifacts=artifacts, transition=make_training_transition(parent, request, artifacts),
            policy=derive_model_policy(parent), crypto_context=parent.crypto_context,
        )
        validate_training_child(child, parent, job, *runtime_hashes(code_dir, workflow))
        verify_peer_state(child, parties, production_service(child.policy, parties))
        write_room_state_exclusive(child, output_path)
        if parent_path.read_bytes() != parent_bytes:
            raise RuntimeError("S1 changed during private NN training")
        return {
            "roomStateId": child.id, "stateCommitment": child.commitment.value,
            "parentStateCommitment": parent.commitment.value,
            "modelParametersSecretShared": True, "trainingReveals": 0,
            "plaintextJoinMaterialized": False,
            "sourceInputsAvailable": Path("/data/local.csv").exists(),
        }
    finally:
        sf.shutdown()


def evaluate(self_party, root, request, job, code_dir, workflow):
    model_id, data_id = job["evaluationTransition"]["inputStateIds"]
    model_state = _load(root, job["roomId"], model_id)
    data_state = _load(root, job["roomId"], data_id)
    model_path = directory(root, model_state.room_id, model_state.id) / "state.json"
    data_path = directory(root, data_state.room_id, data_state.id) / "state.json"
    parent_bytes = (model_path.read_bytes(), data_path.read_bytes())
    validate_evaluation_request(
        model_state, data_state, request, job, *runtime_hashes(code_dir, workflow)
    )
    verify_local(root, model_state, self_party)
    verify_local(root, data_state, self_party)
    output_id = request["outputStateId"]
    output_path = directory(root, data_state.room_id, output_id) / "state.json"
    if output_path.exists():
        raise FileExistsError("RoomState S4_eval is immutable and already exists")

    import secretflow as sf
    from analytics_reveal import production_service
    from nn_kernel import evaluation_kernel_for
    from private_join import create_devices

    if sf.__version__ != data_state.crypto_context.backend_version:
        raise ValueError("SecretFlow runtime version mismatch")
    parties, spu = create_devices(self_party, request["transition"]["transitionId"])
    try:
        model_service = production_service(model_state.policy, parties)
        data_service = production_service(data_state.policy, parties)
        verify_peer_state(model_state, parties, model_service)
        verify_peer_state(data_state, parties, data_service)
        hashes = model_service.metadata(lambda: [
            parties[p](lambda value: value)(digest(request)) for p in PARTIES
        ])
        if hashes != [digest(request), digest(request)]:
            raise ValueError("Participants hold different evaluation requests")
        data_inputs = [spu.load(share_io(root, data_state, artifact_id, True)) for artifact_id in INPUT_IDS]
        model_inputs = [spu.load(share_io(root, model_state, artifact_id, True)) for artifact_id in MODEL_IDS]
        secret_mse = spu(evaluation_kernel_for(request["evaluationSpec"]))(
            *data_inputs, *model_inputs
        )
        destination = replace(model_state, id=output_id)
        spu.dump(secret_mse, share_io(root, destination, EVALUATION_ID, False))
        metadata = model_service.metadata(lambda: [
            parties[p](inspect_ciphertexts)(paths(root, destination, (EVALUATION_ID,)))
            for p in PARTIES
        ])
        artifact = _artifacts(
            metadata, PARTIES, data_state.room_id, output_id, data_state.crypto_context.id,
            (EVALUATION_ID,), ((1,),),
        )[0]
        child = create_room_state(
            state_id=output_id, room_id=data_state.room_id,
            parent_state_ids=(model_state.id, data_state.id), artifacts=(artifact,),
            transition=make_evaluation_transition(model_state, data_state, request, artifact),
            policy=derive_evaluation_policy(model_state, data_state),
            crypto_context=data_state.crypto_context,
        )
        validate_evaluation_child(
            child, model_state, data_state, job, *runtime_hashes(code_dir, workflow)
        )
        verify_peer_state(child, parties, production_service(child.policy, parties))
        write_room_state_exclusive(child, output_path)
        if (model_path.read_bytes(), data_path.read_bytes()) != parent_bytes:
            raise RuntimeError("S1 or S3 changed during private model evaluation")
        return {
            "roomStateId": child.id, "stateCommitment": child.commitment.value,
            "parentStateCommitments": [model_state.commitment.value, data_state.commitment.value],
            "evaluationSecretShared": True, "predictionsPersisted": False,
            "plaintextJoinMaterialized": False,
            "sourceInputsAvailable": Path("/data/local.csv").exists(),
        }
    finally:
        sf.shutdown()


def reveal(self_party, root, request, job, name, code_dir, workflow):
    model_id, data_id = job["evaluationTransition"]["inputStateIds"]
    model_state = _load(root, job["roomId"], model_id)
    data_state = _load(root, job["roomId"], data_id)
    child = _load(root, job["roomId"], request["outputStateId"])
    validate_evaluation_request(
        model_state, data_state, request, job, *runtime_hashes(code_dir, workflow)
    )
    committed = validate_evaluation_child(
        child, model_state, data_state, job, *runtime_hashes(code_dir, workflow)
    )
    if canonical_json(committed) != canonical_json(request):
        raise ValueError("Reveal request differs from committed evaluation request")
    from analytics_reveal import RevealService
    mapping = {EVALUATION_REVEAL: EVALUATION_ID}
    requested = request["transition"]["requestedReveals"]
    # Deny before local ciphertext inspection, runtime creation, load, transfer or reconstruction.
    RevealService(child.policy, {}, None, None).authorize_named(requested, name, mapping)
    verify_local(root, child, self_party)

    import secretflow as sf
    from analytics_reveal import production_service
    from private_join import create_devices

    if sf.__version__ != child.crypto_context.backend_version:
        raise ValueError("SecretFlow runtime version mismatch")
    parties, spu = create_devices(self_party, request["transition"]["transitionId"] + "-reveal")
    try:
        service = production_service(child.policy, parties)
        verify_peer_state(child, parties, service)
        value = service.named_scalar(
            requested, name, mapping,
            lambda artifact_id: spu.load(share_io(root, child, artifact_id, True)),
        )
        return {
            "roomStateId": child.id, "stateReloaded": True,
            "authorizedReveal": name, "value": value,
            "plaintextJoinMaterialized": False,
            "sourceInputsAvailable": Path("/data/local.csv").exists(),
        }
    finally:
        sf.shutdown()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("prepare-training", "train", "prepare-evaluation",
                                             "evaluate", "reveal"), required=True)
    parser.add_argument("--party", choices=PARTIES)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--workflow", type=Path, required=True)
    parser.add_argument("--reveal")
    args = parser.parse_args()
    job = json.loads(args.manifest.read_text())
    request = json.loads(args.request.read_text()) if args.request else None
    code_dir = Path(__file__).parent
    try:
        if args.phase == "prepare-training":
            result = prepare_training(args.state_root, job, code_dir, args.workflow)
        elif args.phase == "prepare-evaluation":
            result = prepare_evaluation(args.state_root, job, code_dir, args.workflow)
        elif args.phase == "train":
            result = train(args.party, args.state_root, request, job, code_dir, args.workflow)
        elif args.phase == "evaluate":
            result = evaluate(args.party, args.state_root, request, job, code_dir, args.workflow)
        else:
            result = reveal(args.party, args.state_root, request, job, args.reveal, code_dir, args.workflow)
    except PermissionError:
        print(json.dumps({"status": "M4_DENIED", "artifactLoadedForReveal": False,
                          "transferAttempted": False, "reconstructionAttempted": False}), flush=True)
        raise SystemExit(3)
    except ValueError as error:
        print(json.dumps({"status": "M4_REJECTED", "reason": str(error)}), flush=True)
        raise SystemExit(2)
    print(canonical_json(result).decode(), flush=True)


if __name__ == "__main__":
    main()
