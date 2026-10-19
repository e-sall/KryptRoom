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

## Milestone 4: persistent private neural network

- [x] Implement the fixed Dense 1→2→1 square-activation direct-JAX training kernel and deterministic initializer.
- [x] Bind S1 training inputs into an immutable S3 model transition with four encrypted local parameter-share artifacts.
- [x] Implement exact `[S3_model, S1]` evaluation into immutable secret MSE state S4.
- [x] Reuse StatePolicy and RevealService for fail-closed MSE-only disclosure.
- [x] Add M4 contract, privacy, persistence, restart, and regression test coverage.
- [x] Execute and record the authoritative real CHEETAH/FM128 S1→S3→restart→S4→restart→reveal gate.

## Milestone 5: committed evaluation metadata proof

- [x] Implement the bounded SP1 relation, receipt/StateProof schemas and standalone verifier.
- [x] Add metadata-only fixtures, cross-language vectors and negative/privacy checks.
- [x] Pass real SP1 6.9.0 CPU Groth16 generation and independent verification in Linux CI.

Status: **M5 VERIFIED**. The unchanged real gate passed on a temporary
repository-scoped one-job WSL2 runner after two preserved historical hosted-runner
shutdowns. See [M5 validation](docs/M5_VALIDATION.md). The result covers only the
bounded committed metadata relation.

## Milestone 6: persistent FHE state transition

- [x] Select exact fixed-vector BGV addition as the bounded first FHE operation.
- [x] Pin the official OpenFHE 1.5.1.0.24.4 Ubuntu 24.04 wheel by SHA-256.
- [x] Extend RoomState contracts compatibly for `fhe_ciphertext` artifacts and FHE CryptoContext material.
- [x] Keep the private decryption key in Lab A's participant-owned root and out of shared metadata/storage.
- [x] Implement persisted `S5_fhe_inputs` → secret-key-free `EvalAdd` → persisted `S6_fhe_sum`.
- [x] Separate FHE computation authorization from `fhe.vector-sum` decryption authorization.
- [x] Add context/epoch, commitment, tampering, policy, lineage, leakage, and restart tests.
- [x] Pass and record the real Linux OpenFHE persistence/EvalAdd/decryption CI gate.

## Explicitly deferred

- [ ] Choose project licensing terms before encouraging substantial third-party code contributions.
- [ ] Confirm a private vulnerability-reporting channel in repository settings.

- Analytics beyond COUNT/SUM/MEAN/CROSS_MEAN and ML beyond the fixed M4 network.
- FHE analytics beyond the bounded M6 fixed-vector addition.
- Proofs beyond M5's bounded metadata relation, post-quantum identity, and RunReceipts.
- Blockchain anchoring.
- Web frontend.
- RoomState branch UI, merge implementation, and dynamic membership.

