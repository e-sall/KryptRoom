# KryptRoom

> Compute together. Reveal nothing.

KryptRoom is a persistent encrypted state machine for organizations that need to collaborate without disclosing their raw data to one another, KryptRoom, or a central cloud operator.

## Status

Milestone 1 provides a runtime-verified two-party private-set-intersection cardinality (PSI-CA). Milestone 2 provides a runtime-verified secret-shared private join handoff into SecretFlow SPU. Milestone 2.5 implements immutable, encrypted RoomState persistence and is awaiting its Linux restart/reload CI evidence. Product claims are intentionally limited to recorded evidence.

The intended first demo uses two independent KryptNodes:

- Lab A owns patient identifiers `P001`, `P002`, `P004`, and `P006`.
- Lab B owns patient identifiers `P002`, `P003`, `P004`, and `P007`.
- The expected intersection cardinality is `2`; matched identifiers are not an authorized output.
- Raw input identifiers remain local to their owning KryptNode.

## Milestone 1 demo

The current implementation uses OpenMined PSI v2.0.6 with ECDH commutative encryption, the exact `Raw` encrypted container, and identifier disclosure disabled at both peers.

Prerequisites: Node.js 20 or newer and npm.

```bash
npm ci --ignore-scripts
npm test
npm run demo:psi
```

The authorized demo output contains `intersectionCardinality: 2` and no matched identifiers. Lab A and Lab B run as independent operating-system processes and read separate CSV files. No Control Plane process receives either dataset.

Runtime verification completed on 2026-09-29: all nine automated tests passed and the end-to-end demo returned cardinality `2` without emitting matched identifiers. The use of `--ignore-scripts` avoids an unnecessary and currently broken `protoc-gen-js` installer; OpenMined PSI's distributed WebAssembly runtime is already precompiled.

## Milestone 2 private join

The M2 runtime compares fixed-width identifier bytes inside a two-party SecretFlow SPU and produces a fixed-shape secret handoff: a match mask and masked feature grids. Identifiers are excluded from the handoff. A second MPC call consumes the mask and reconstructs only cardinality.

The demo requires a Linux Docker host or Docker Desktop with WSL 2:

```bash
npm run demo:private-join
```

The official SecretFlow 1.14.0b0 image is pinned by immutable digest. Its release entrypoint is bypassed because that interactive version banner imports optional packages absent from the image; KryptRoom starts SecretFlow's documented no-Ray production scheduler directly. CHEETAH/FM128 is used because SEMI2K's default trusted-first-party preprocessing does not satisfy the two-party privacy model. No ML is included. The full Linux cryptographic integration is enforced in GitHub Actions.

Runtime verification completed on 2026-09-30 in [GitHub Actions run 36731809790](https://github.com/e-sall/KryptRoom/actions/runs/36731809790): both containers exited successfully, both returned cardinality `2`, the SPU logs recorded CHEETAH over a 128-bit ring, and the log-leak gate found no synthetic participant identifier.

## Milestone 2.5 persistent RoomState

The M2.5 create phase persists the M2 match mask and masked feature grids as RoomState S1. Each KryptNode keeps only its own SecretFlow share, encrypted at rest with AES-256-GCM under a distinct node-local key. Artifact authentication binds the share to S1 and the exact CHEETAH/FM128 crypto context. State and artifact files cannot overwrite an existing state ID.

After the create containers terminate, the analytics phase starts new containers without either source CSV mounted. It verifies and reloads S1 through SecretFlow's native SPU persistence interface, then computes a minimal private aggregate whose expected synthetic value is `68`. This continuity check is not the future M3 analytics API.

On a Linux Docker host, create S1 and stop the containers:

```bash
npm run demo:persistent-state:create
docker compose -f compose.persistent-state.yml -f compose.persistent-state.persist.yml down
```

Then start fresh containers from the persisted local state only:

```bash
npm run demo:persistent-state:analytics
```

The default state directory is `.runtime/persistent-state/` and is excluded from Git. The demo stores local keys as permission-restricted files; it does not yet provide production KMS/HSM integration, key rotation, signed commitments, malicious-party security, or crash-atomic distributed commit.

## Principles

- The Control Plane is not trusted with participant plaintext.
- Privacy-preserving claims must match the implementation and threat model.
- Mature cryptographic libraries are preferred over custom cryptography.
- Simulated components must be labelled as simulated.
- Blockchain is reserved for commitments and audit provenance, never datasets or model material.

## Repository map

- `nodes/`: organization-owned KryptNode components.
- `engines/`: adapters and runtime configuration for PSI, MPC, FHE, and ZK systems.
- `services/`: Control Plane services, added only as milestones require them.
- `workflows/`: composable private-compute workflows.
- `packages/`: shared manifests, protocol types, and SDKs.
- `demos/`: synthetic end-to-end demonstrations.
- `tests/`: integration, privacy, and reproducibility checks.
- `docs/`: roadmap and architectural decision records.

Read [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [THREAT_MODEL.md](THREAT_MODEL.md) before making implementation changes.

## Runtime prerequisites

The PSI-cardinality demo runs on Node.js. The private-join and persistent-state demos require Docker Desktop with its WSL 2 backend on Windows, or an equivalent Linux Docker host. SecretFlow 1.14.0b0 supports Python 3.10 and 3.11, not Python 3.12, so the engine stays inside its pinned Linux container.

## Security notice

KryptRoom is pre-release research software. It has not been independently audited and must not be used with real medical or regulated data.

