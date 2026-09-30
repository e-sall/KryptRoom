# KryptRoom

> Compute together. Reveal nothing.

KryptRoom is encrypted-compute and collaboration infrastructure for organizations that need to work together without disclosing their raw data to one another, KryptRoom, or a central cloud operator.

## Status

The repository is in its foundation phase. The first product capability is a real two-party private-set-intersection cardinality (PSI-CA) for the cancer-collaboration demo. Product claims in this repository are intentionally limited to code that has been executed and verified.

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

Runtime verification completed on 2026-09-29: all eight automated tests passed and the end-to-end demo returned cardinality `2` without emitting matched identifiers. The use of `--ignore-scripts` avoids an unnecessary and currently broken `protoc-gen-js` installer; OpenMined PSI's distributed WebAssembly runtime is already precompiled.

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

The PSI-cardinality demo runs on Node.js. Future SecretFlow SPU, MPC, and Linux-native cryptographic services will require Docker Desktop with its WSL 2 backend on Windows, or an equivalent Linux Docker host.

## Security notice

KryptRoom is pre-release research software. It has not been independently audited and must not be used with real medical or regulated data.

