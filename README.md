# KryptRoom

> Compute together. Reveal nothing.

KryptRoom is encrypted-compute and collaboration infrastructure for organizations that need to work together without disclosing their raw data to one another, KryptRoom or a central cloud operator.

## Status

The repository is in its foundation phase. The first product capability is a real two-party private set intersection (PSI) for the cancer-collaboration demo. Product claims in this repository are intentionally limited to code that has been executed and verified.

The intended first demo uses two independent KryptNodes:

- Lab A owns patient identifiers `P001`, `P002`, `P004`, and `P006`.
- Lab B owns patient identifiers `P002`, `P003`, `P004`, and `P007`.
- The expected intersection is `P002`, `P004`.
- Raw input identifiers remain local to their owning KryptNode.

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

The real PSI milestone targets Linux containers. Windows development requires Docker Desktop with its WSL 2 backend or an equivalent Linux Docker host. Exact demo and verification commands will be documented with the PSI implementation.

## Security notice

KryptRoom is pre-release research software. It has not been independently audited and must not be used with real medical or regulated data.

