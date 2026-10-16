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
- [x] Execute the two-container CHEETAH/FM128 cryptographic integration test.
- [x] Record exact Milestone 2 runtime and test evidence.

## Milestone 2.5: persistent encrypted RoomState

- [x] Define immutable RoomState, ArtifactRef, StateTransition, StatePolicy, CryptoContext, and StateCommitment contracts.
- [x] Persist each node's native SPU shares with node-local AES-256-GCM encryption and context-bound authenticated data.
- [x] Support list-valued `parentStateIds` while limiting M2.5 to parentless S1 creation.
- [x] Add a restart phase with no source CSV mounts and a policy-authorized private aggregate from reloaded S1.
- [x] Add unit, privacy, reproducibility, storage-layout, and cryptographic CI checks.
- [x] Run and record the Linux create/terminate/restart/reload CHEETAH/FM128 evidence.
- [x] Diagnose initial CI cancellations as hosted-runner acquisition failures and remove duplicate feature push/PR M2.5 runs.

## Environment blocker

- [x] Install the pinned OpenMined PSI dependency and run the cryptographic tests.
- [x] Provide a Linux Docker host through GitHub Actions to execute SecretFlow SPU/MPC.

## Milestone 3: persistent private cohort analytics

- [x] Implement COUNT, SUM, MEAN and CROSS_MEAN over persisted S1 artifacts.
- [x] Bind exact parent/input descriptors, specification, code/workflow, policy and context into a transition and new immutable S2.
- [x] Separate computation permission from scalar reveal permission; fail closed on empty cohort and wrong context.
- [x] Add executable state/privacy/storage tests and real Linux CI chain.
- [x] Execute and record the full M2/S1/restart/M3/S2/restart/reveal cryptographic gate.

## Explicitly deferred

- [ ] Choose project licensing terms before encouraging substantial third-party code contributions.
- [ ] Confirm a private vulnerability-reporting channel in repository settings.

- Analytics beyond COUNT/SUM/MEAN/CROSS_MEAN and neural-network training.
- FHE analytics.
- ZK proofs, post-quantum identity, and RunReceipts.
- Blockchain anchoring.
- Web frontend.
- RoomState branch UI, merge implementation, and dynamic membership.

