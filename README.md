# KryptRoom

> Compute together. Reveal nothing.

KryptRoom is encrypted-compute and collaboration infrastructure for organizations that need to work together without disclosing their raw data to one another, KryptRoom, or a central cloud operator.

## Status

Milestone 1 provides a runtime-verified two-party private-set-intersection cardinality (PSI-CA). Milestone 2 now contains an implemented secret-shared private join handoff into SecretFlow SPU, with its Linux cryptographic integration run still pending. Product claims are intentionally limited to the recorded evidence.

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

The PSI-cardinality demo runs on Node.js. The private-join demo requires Docker Desktop with its WSL 2 backend on Windows, or an equivalent Linux Docker host. SecretFlow 1.14.0b0 supports Python 3.10 and 3.11, not Python 3.12, so the engine stays inside its pinned Linux container.

## Security notice

KryptRoom is pre-release research software. It has not been independently audited and must not be used with real medical or regulated data.

