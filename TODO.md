# TODO

## Repository foundation

- [x] Record product and architecture context.
- [x] Establish initial threat model and decision log.
- [x] Create monorepo directory boundaries.
- [x] Push the initial `main` commit.
- [x] Create and push `dev`, then continue work from `dev`.

## Milestone 1: real two-party PSI

- [x] Confirm that neither participant is authorized to receive matched identifiers; cardinality only is allowed.
- [x] Add two independent KryptNode processes.
- [x] Add isolated synthetic Lab A and Lab B inputs.
- [x] Implement OpenMined ECDH PSI cardinality with the exact `Raw` container.
- [x] Execute the cryptographic integration test and verify cardinality `2`.
- [x] Verify structurally that no Control Plane component mounts or logs raw IDs.
- [x] Add automated integration, privacy, and reproducibility checks.
- [x] Generate and commit `package-lock.json` after a successful trusted install.

## Milestone 2: secret-shared private join handoff

- [x] Integrate a fixed-shape SecretFlow SPU circuit for private join/MPC handoff.
- [ ] Execute the two-container CHEETAH/FM128 cryptographic integration test.
- [ ] Record exact Milestone 2 runtime and test evidence.

## Environment blocker

- [x] Install the pinned OpenMined PSI dependency and run the cryptographic tests.
- [x] Provide a Linux Docker host through GitHub Actions to execute SecretFlow SPU/MPC.

## Explicitly deferred

- MPC analytics and neural-network training.
- FHE analytics.
- ZK proofs, post-quantum identity, and RunReceipts.
- Blockchain anchoring.
- Web frontend.

