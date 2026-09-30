"""Two-party private join that keeps identifiers and joined rows secret-shared.

Both organizations execute this program. Each process can read only the CSV
mounted by its own KryptNode. Identifiers are encoded as fixed-width UTF-8
bytes locally and transferred directly from each PYU into the SPU as secret
shares. The SPU produces a fixed-shape join mask and masked feature grids.
Only the intersection cardinality is reconstructed.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

import jax.numpy as jnp
import numpy as np
import secretflow as sf
import spu
from secretflow.device import SPUCompilerNumReturnsPolicy


PARTIES = ("lab-a", "lab-b")
APPROVED_SECRETFLOW_VERSION = "1.14.0b0"
SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
FEATURE_LIMIT = 1_000_000


def load_local_dataset(
    path: str,
    feature_column: str,
    max_rows: int,
    max_identifier_bytes: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load and pad one party's input without logging any record values."""

    identifiers = np.zeros((max_rows, max_identifier_bytes), dtype=np.uint8)
    active = np.zeros((max_rows,), dtype=np.bool_)
    features = np.zeros((max_rows, 1), dtype=np.int32)

    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        expected_columns = ["patient_id", feature_column]
        if reader.fieldnames != expected_columns:
            raise ValueError("Local dataset has an invalid schema")
        rows = list(reader)

    if not rows or len(rows) > max_rows:
        raise ValueError("Local dataset row count is outside the public capacity")

    seen: set[str] = set()
    for index, row in enumerate(rows):
        identifier = row["patient_id"]
        if not SAFE_IDENTIFIER.fullmatch(identifier):
            raise ValueError("Local dataset contains an invalid patient identifier")
        if identifier in seen:
            raise ValueError("Local dataset contains duplicate patient identifiers")
        seen.add(identifier)

        encoded = identifier.encode("utf-8")
        if len(encoded) > max_identifier_bytes:
            raise ValueError("Local patient identifier exceeds the public byte limit")

        try:
            feature = int(row[feature_column])
        except (TypeError, ValueError) as error:
            raise ValueError("Local dataset contains an invalid integer feature") from error
        if abs(feature) > FEATURE_LIMIT:
            raise ValueError("Local dataset feature is outside the accepted range")

        identifiers[index, : len(encoded)] = np.frombuffer(encoded, dtype=np.uint8)
        active[index] = True
        features[index, 0] = feature

    return identifiers, active, features


def build_private_join_handoff(
    left_payload: tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray],
    right_payload: tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray],
) -> tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    """Build a fixed-shape secret join grid inside SPU.

    Identifier bytes never appear in the output. The mask and both feature
    grids remain secret values and are safe to pass to subsequent SPU calls.
    """

    left_ids, left_active, left_features = left_payload
    right_ids, right_active, right_features = right_payload

    identifier_equal = jnp.all(
        left_ids[:, jnp.newaxis, :] == right_ids[jnp.newaxis, :, :], axis=2
    )
    active_pairs = left_active[:, jnp.newaxis] & right_active[jnp.newaxis, :]
    match_mask = identifier_equal & active_pairs

    mask = match_mask.astype(jnp.int32)
    left_grid = jnp.broadcast_to(
        left_features[:, jnp.newaxis, :],
        (left_features.shape[0], right_features.shape[0], left_features.shape[1]),
    )
    right_grid = jnp.broadcast_to(
        right_features[jnp.newaxis, :, :],
        (left_features.shape[0], right_features.shape[0], right_features.shape[1]),
    )

    # Unmatched feature cells are zeroed inside MPC. The match mask is still
    # required by downstream computations because zero is a valid feature.
    return mask, left_grid * mask[:, :, jnp.newaxis], right_grid * mask[:, :, jnp.newaxis]


def intersection_cardinality(secret_match_mask: jnp.ndarray) -> jnp.ndarray:
    """Authorized MPC consumer for the current cardinality-only policy."""

    return jnp.sum(secret_match_mask, dtype=jnp.int32)


def load_job(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    policy = manifest.get("outputPolicy", {})
    backend = manifest.get("backend", {})
    handoff = manifest.get("mpcHandoff", {})
    join = manifest.get("join", {})
    participants = manifest.get("participants", [])

    if manifest.get("version") != "1":
        raise ValueError("Unsupported private-join job version")
    if not isinstance(manifest.get("jobId"), str) or not manifest["jobId"]:
        raise ValueError("Job identifier is required")
    if manifest.get("operation") != "private-join-handoff":
        raise ValueError("Job operation is not private-join-handoff")
    if backend != {
        "name": "SecretFlow SPU",
        "version": APPROVED_SECRETFLOW_VERSION,
        "protocol": "CHEETAH",
        "field": "FM128",
        "securityModel": "semi-honest",
    }:
        raise ValueError("Job backend does not match the approved runtime")
    if sf.__version__ != APPROVED_SECRETFLOW_VERSION:
        raise RuntimeError(
            "Installed SecretFlow version does not match the approved runtime"
        )
    if policy.get("resultMode") != "cardinality-only":
        raise ValueError("Only cardinality-only output is supported")
    if policy.get("revealMatchedIdentifiers") is not False:
        raise ValueError("Matched-identifier disclosure is forbidden")
    if policy.get("futureIdentifierDisclosure", {}).get("requiresExplicitOptIn") is not True:
        raise ValueError("Future identifier disclosure must require explicit opt-in")
    if set(policy.get("cardinalityRecipients", [])) != {"lab-a", "lab-b", "ui"}:
        raise ValueError("Cardinality recipients do not match the approved policy")
    if handoff != {
        "format": "fixed-shape-join-grid",
        "visibility": "secret-shared",
        "includesIdentifiers": False,
        "recipient": "mpc",
    }:
        raise ValueError("MPC handoff policy is invalid")
    if join.get("key") != "patient_id":
        raise ValueError("Private join key is invalid")
    if join.get("identifierEncoding") != "fixed-width-utf8":
        raise ValueError("Private join identifier encoding is invalid")
    if not isinstance(join.get("maxIdentifierBytes"), int) or not (
        1 <= join["maxIdentifierBytes"] <= 128
    ):
        raise ValueError("Identifier byte capacity is invalid")
    if not isinstance(join.get("maxRowsPerParticipant"), int) or not (
        1 <= join["maxRowsPerParticipant"] <= 1024
    ):
        raise ValueError("Participant row capacity is invalid")
    expected_participants = {
        "lab-a": {"role": "left", "featureColumn": "genomic_score"},
        "lab-b": {"role": "right", "featureColumn": "treatment_response"},
    }
    if not isinstance(participants, list) or len(participants) != 2:
        raise ValueError("Exactly two participants are required")
    actual_participants = {entry.get("id"): entry for entry in participants}
    if set(actual_participants) != set(expected_participants):
        raise ValueError("Private join participants are invalid")
    for party, expected in expected_participants.items():
        participant = actual_participants[party]
        if participant.get("role") != expected["role"]:
            raise ValueError("Private join participant role is invalid")
        if participant.get("featureColumn") != expected["featureColumn"]:
            raise ValueError("Private join feature column is invalid")
        if not str(participant.get("input", "")).startswith(f"local://{party}/"):
            raise ValueError("Participant input must be local to its KryptNode")
    if manifest.get("controlPlaneDataAccess") != "none":
        raise ValueError("Control Plane access to participant data is forbidden")
    return manifest


def create_devices(self_party: str, job_id: str) -> tuple[dict[str, sf.PYU], sf.SPU]:
    cluster_config = {
        "parties": {
            "lab-a": {"address": "lab-a:9100", "listen_addr": "0.0.0.0:9100"},
            "lab-b": {"address": "lab-b:9200", "listen_addr": "0.0.0.0:9200"},
        },
        "self_party": self_party,
    }
    sf.init(
        # SecretFlow 1.14.0b0 officially supports production scheduling with
        # its thread-pool backend. This image intentionally has no Ray package.
        ray_mode=False,
        cluster_config=cluster_config,
        logging_level="warning",
        job_name=job_id,
        cross_silo_comm_options={"timeout_in_ms": 300_000},
    )

    parties = {party: sf.PYU(party) for party in PARTIES}
    cluster_def = {
        "nodes": [
            {
                "party": "lab-a",
                "address": "lab-a:9300",
                "listen_address": "0.0.0.0:9300",
            },
            {
                "party": "lab-b",
                "address": "lab-b:9400",
                "listen_address": "0.0.0.0:9400",
            },
        ],
        "runtime_config": {
            "protocol": spu.ProtocolKind.CHEETAH,
            "field": spu.FieldType.FM128,
        },
    }
    secure_device = sf.SPU(
        cluster_def=cluster_def,
        link_desc={
            "connect_retry_times": 120,
            "connect_retry_interval_ms": 1_000,
            "recv_timeout_ms": 300_000,
            "http_timeout_ms": 300_000,
        },
    )
    return parties, secure_device


def run(self_party: str, manifest_path: Path, local_input_path: str) -> dict[str, Any]:
    manifest = load_job(manifest_path)
    participants = {entry["id"]: entry for entry in manifest["participants"]}
    join = manifest["join"]
    max_rows = join["maxRowsPerParticipant"]
    max_identifier_bytes = join["maxIdentifierBytes"]

    parties, secure_device = create_devices(self_party, manifest["jobId"])
    try:
        # The same local path resolves inside each participant's isolated
        # container, where only that participant's CSV is mounted.
        left_payload = parties["lab-a"](load_local_dataset)(
            local_input_path,
            participants["lab-a"]["featureColumn"],
            max_rows,
            max_identifier_bytes,
        )
        right_payload = parties["lab-b"](load_local_dataset)(
            local_input_path,
            participants["lab-b"]["featureColumn"],
            max_rows,
            max_identifier_bytes,
        )

        # This is the M2 boundary: all three returned values are SPUObjects.
        # No participant or Control Plane receives the join mask or joined rows.
        secret_match_mask, secret_left_features, secret_right_features = secure_device(
            build_private_join_handoff,
            num_returns_policy=SPUCompilerNumReturnsPolicy.FROM_USER,
            user_specified_num_returns=3,
        )(left_payload, right_payload)

        # Consume the secret handoff in a second MPC computation. The feature
        # grids are deliberately retained as secret SPUObjects for later M3
        # analytics; M2 does not train or evaluate any ML model.
        secret_cardinality = secure_device(intersection_cardinality)(secret_match_mask)
        # Every controller must construct the same federated task graph. Move
        # the authorized cardinality to both approved participants in a stable
        # order, then reconstruct those cardinality objects together.
        cardinality_for_participants = [
            secret_cardinality.to(parties[party]) for party in PARTIES
        ]
        participant_cardinalities = [
            int(np.asarray(value).item())
            for value in sf.reveal(cardinality_for_participants)
        ]
        if len(set(participant_cardinalities)) != 1:
            raise RuntimeError("Participants reconstructed different cardinalities")
        cardinality = participant_cardinalities[0]

        # Keep references alive through authorized output reconstruction and
        # fail closed if the runtime ever returns plaintext-like objects.
        if secret_left_features.device is not secure_device:
            raise RuntimeError("Lab A feature handoff did not remain on SPU")
        if secret_right_features.device is not secure_device:
            raise RuntimeError("Lab B feature handoff did not remain on SPU")

        return {
            "intersectionCardinality": cardinality,
            "matchedIdentifiersRevealed": False,
            "mpcHandoff": {
                "visibility": "secret-shared",
                "format": "fixed-shape-join-grid",
                "includesIdentifiers": False,
            },
        }
    finally:
        sf.shutdown()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--party", choices=PARTIES, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--local-input", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run(args.party, args.manifest, args.local_input)
    print(json.dumps(result, separators=(",", ":"), sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
