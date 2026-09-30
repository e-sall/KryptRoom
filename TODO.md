# TODO

## Repository foundation

- [x] Record product and architecture context.
- [x] Establish initial threat model and decision log.
- [x] Create monorepo directory boundaries.
- [ ] Push the initial `main` commit.
- [ ] Create and push `dev`, then continue work from `dev`.

## Milestone 1: real two-party PSI

- [ ] Confirm which participant(s) are authorized to receive the intersection.
- [ ] Add two independently configured KryptNode containers.
- [ ] Add isolated synthetic Lab A and Lab B inputs.
- [ ] Execute SecretFlow PSI v2 with `PROTOCOL_RR22`.
- [ ] Verify the intersection is exactly `P002`, `P004`.
- [ ] Verify no Control Plane component mounts or logs raw IDs.
- [ ] Verify non-intersecting peer IDs are absent from outputs and logs.
- [ ] Add automated integration, privacy, and reproducibility checks.
- [ ] Pin the tested SecretFlow container by immutable digest.
- [ ] Record exact runtime and test evidence.

## Environment blocker

- [ ] Install Docker Desktop with WSL 2 backend, or provide a Linux Docker host. The current Windows environment has no Python, Docker, or WSL installation, so real PSI execution is not yet possible here.

## Explicitly deferred

- MPC analytics and neural-network training.
- FHE analytics.
- ZK proofs, post-quantum identity, and RunReceipts.
- Blockchain anchoring.
- Web frontend.

