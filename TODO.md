# TODO

## Repository foundation

- [x] Record product and architecture context.
- [x] Establish initial threat model and decision log.
- [x] Create monorepo directory boundaries.
- [ ] Push the initial `main` commit.
- [ ] Create and push `dev`, then continue work from `dev`.

## Milestone 1: real two-party PSI

- [x] Confirm that neither participant is authorized to receive matched identifiers; cardinality only is allowed.
- [x] Add two independent KryptNode processes.
- [x] Add isolated synthetic Lab A and Lab B inputs.
- [x] Implement OpenMined ECDH PSI cardinality with the exact `Raw` container.
- [ ] Execute the cryptographic integration test and verify cardinality `2` (dependency download blocked in the current environment).
- [x] Verify structurally that no Control Plane component mounts or logs raw IDs.
- [x] Add automated integration, privacy, and reproducibility checks.
- [ ] Generate and commit `package-lock.json` after a successful trusted install.
- [ ] Integrate a mature circuit-PSI or secret-shared PSI backend for private join/MPC handoff.
- [ ] Record exact runtime and test evidence.

## Environment blocker

- [ ] Permit npm package access long enough to install the pinned OpenMined PSI dependency and run the cryptographic tests.
- [ ] Install Docker Desktop with WSL 2 backend, or provide a Linux Docker host before SecretFlow SPU/MPC work. The current Windows environment has no Python, Docker, or WSL installation.

## Explicitly deferred

- MPC analytics and neural-network training.
- FHE analytics.
- ZK proofs, post-quantum identity, and RunReceipts.
- Blockchain anchoring.
- Web frontend.

