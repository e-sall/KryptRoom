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

## Milestone 7: public blockchain anchor

- [x] Define exact domain-separated RoomState and optional StateProof commitments.
- [x] Implement the stateless permissionless event-only Solidity contract.
- [x] Add immutable ChainAnchor and separate dynamic status schemas/models.
- [x] Implement Base receipt, event, runtime-code, canonicality, finality, and reorg checks.
- [x] Keep package matching distinct from the existing M5 standalone proof verifier.
- [x] Support M6 state-only anchoring without reading FHE artifacts or keys.
- [x] Add deterministic vectors, negative/privacy tests, and pinned Foundry CI.
- [x] Split fast M5 regression from change-scoped/manual real Groth16 acceptance.
- [x] Configure protected GitHub environment `base-sepolia-m7` with testnet-only `BASE_SEPOLIA_RPC_URL` and `M7_TEST_ANCHOR_PRIVATE_KEY`.
- [x] Perform exactly one authoritative Base Sepolia V1 deployment and validate its transaction, receipt, canonical block, and exact runtime without sending another transaction.
- [x] Publish one real state-only acceptance anchor and verify exactly one canonical matching event without sending a duplicate.
- [x] Recover the authoritative manifest/artifact package, wait for `finalized`, and pass standalone Layers A/B through the guarded evidence-only resume workflow without broadcasting.

Status: **VERIFIED** for the bounded state-only Base Sepolia acceptance. The V1
contract and sole canonical event are finalized, standalone Layers A/B pass,
and run 39381943437 contains the authoritative public evidence package.

## M8 PR1 — Design System & App Shell

- [x] Audit the actual dev baseline and supplied M8 source archive.
- [x] Add reusable tokens, identity, controls and honest module placeholders.
- [x] Add desktop sidebar/inspector, tablet rail/bottom inspector and mobile sheets/navigation.
- [x] Run targeted component, production-build, keyboard, responsive and browser checks.
- [x] Document source comparisons, conversion failures and integration boundaries.
- [x] PR1 merged through #14 at `acf5f262b03d6c0db3ff36b413f330b61f1181d2` (verified before PR2).
- [ ] Resolve or explicitly accept the documented lint-tooling debt (unpatched braces advisory and ESLint 9 support lifecycle).
- [x] Align the single KLogo with the later P05/P06/P11 thin gray-branch identity and add regression checks.
- [x] Record temporary exception M8-SEC-001 with production/reachability evidence.
- [ ] Maintainer reevaluation of M8-SEC-001 **before PR7 starts or 2026-11-21, whichever is earlier**; no silent renewal.
- [ ] Implement PR2–7 in separate approved increments; no backend capability inferred.

## M8 PR2 — Rooms & Easy Setup

- [x] Reinspect merged dev, original P03/P06/P11 and missing workspace services.
- [x] Build isolated synthetic List/Cards, search/filter, expansion, details and navigation.
- [x] Build four-step setup with validation, ephemeral draft and denied business actions.
- [x] Exercise frontend unit/build/type/lint and production Chromium journeys on three formats.
- [x] Record visual comparisons, backend gaps, traceability and ADR-017.
- [x] Implement owner-authorized frontend/core CI scope conditions and synthetic tests; inspect dev protections without changing them.
- [x] Apply the separately authorized exact M5 metadata refresh; retain reproducibility assertion, negative CI-scope tests and historical proof provenance.
- [x] Apply the separately authorized two-file M7 synthetic-vector refresh; verify M5/M7 together, exact hash-bound CI classification and historical Layer B/Layer C distinction.
- [x] Owner-approved PR2 merged through #15 at `a88df46a0213d7c422410db4d5cde32f8c3de897`; ten post-merge workflows passed.
- [ ] Integrate authenticated Room/invitation/connector/policy services only in a separately approved scope.
- [ ] Reevaluate M8-SEC-001 before PR7 or 2026-11-21, whichever is earlier (no renewal in PR2).

## M8 PR3 — Graph Workspace

- [x] Merge approved PR #15 into dev after head/check/invariant verification.
- [x] Start PR3 from verified merge `a88df46a0213d7c422410db4d5cde32f8c3de897`.
- [x] Audit recovered P04/P11 and actual immutable multi-parent core contracts.
- [x] Implement isolated graph model/layout, three modes, selection, viewport and inspector.
- [x] Test DAG negatives, frontend regressions, keyboard, touch, responsive and privacy boundaries.
- [x] Document converted-reference comparisons and HTML/React adaptations.
- [x] PR #16 merged into dev at `2c912bcfc52d281ecdfda5798fc75e47b87fdf1e`, independently rechecked before PR4.
- [ ] Preserve M8-SEC-001 reevaluation before PR7 or 2026-11-21.

## M8 PR4 — Computations & Results

- [x] Verify PR #16 merge/base, original P07/P08/P04/P11 and absent Workspace services.
- [x] Implement Clean interactive explanatory workflow and fail-closed Readiness/Review.
- [x] Implement separate Premium V3 PSI/Join/Analytics fixed result views and chart/table.
- [x] Preserve Room identity, immutable ordered parent references and exact-state Graph navigation.
- [x] Exercise frontend regression, keyboard, responsive, system-state and privacy tests.
- [x] Record source conversions, application captures and explicit HTML adaptations in ADR-019/report.
- [x] Address PR #17 narrow Analytics label spacing with a failing-then-passing browser regression, four-width visual evidence and unchanged chart/table values.
- [ ] Independent PR4 review and final-head CI disposition; **do not automatically merge**.
- [ ] Authenticated services and real disclosure remain separately scoped future work.
- [ ] M8-SEC-001 reevaluation before PR7 or 2026-11-21, whichever is earlier; no renewal.

## Explicitly deferred work (unchanged)

- [ ] Choose project licensing terms before encouraging substantial third-party code contributions.
- [ ] Confirm a private vulnerability-reporting channel in repository settings.

- Analytics beyond COUNT/SUM/MEAN/CROSS_MEAN and ML beyond the fixed M4 network.
- FHE analytics beyond the bounded M6 fixed-vector addition.
- Proofs beyond M5's bounded metadata relation, post-quantum identity, and RunReceipts.
- Mainnet deployment, on-chain state/storage/computation, tokens, payments, or blockchain governance.
- Web product functionality beyond the disconnected M8 PR1–PR4 presentation scope.
- Authoritative RoomState branch operations, merge implementation, and dynamic membership.

