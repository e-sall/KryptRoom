# Changelog

All notable project changes are recorded here. The project follows milestone-oriented development; it has not adopted semantic versioning yet.

## Unreleased

### Added

- Initial project documentation and persistent engineering context.
- Monorepo boundaries for applications, services, nodes, cryptographic engines, workflows, shared packages, chain code, demos, infrastructure, and tests.
- Initial architecture and honest-but-curious threat model for two-party PSI.
- Two independent KryptNode processes for exact PSI cardinality.
- Synthetic cancer-collaboration fixtures, disclosure manifest, demo runner, and automated unit/integration/privacy/reproducibility tests.
- CI workflow for the PSI milestone.
- Reproducible npm lockfile for the full PSI dependency graph.
- Canonical PSI job manifest and schema recording the backend, participants, security model, local inputs, and disclosure policy.
- Milestone 2 private-join manifest, schema, synthetic feature fixtures, isolated two-container topology, and SecretFlow SPU runtime.
- Fixed-shape secret join handoff containing only a secret match mask and masked feature grids, with identifiers excluded.
- Privacy, manifest, container-isolation, and runtime-pin tests for the private join.
- A Linux Docker CI gate for the two-party CHEETAH/FM128 integration test.
- Immutable RoomState, ArtifactRef, StateTransition, StatePolicy, CryptoContext, and StateCommitment contracts.
- Node-local AES-256-GCM persistence for native SecretFlow SPU shares, with authenticated crypto-context bindings.
- A two-phase M2.5 integration gate that creates S1, terminates both nodes, restarts without source-data mounts, reloads S1, and executes a private aggregate.

### Changed

- Reworked the public README around verified capabilities, synthetic cancer-research collaboration, explicit experimental limitations, and the persistent-state roadmap. Corrected historical architecture/backend wording, added contribution and security-reporting guidance, and expanded local-artifact ignore rules without changing runtime code or selecting a license.

- Made PR events authoritative for feature-branch M2.5 integration, retained main/dev push validation, and serialized M2.5 runs without cancelling an active run. The initial cancelled jobs never acquired hosted runners; no cryptographic execution failure was observed.

- Adopted the product default that matched identifiers are disclosed to neither participant; only cardinality is authorized.
- Replaced the planned SecretFlow RR22 milestone backend with OpenMined PSI cardinality because RR22's mandatory receiver learns the intersection.
- Selected SPU CHEETAH instead of SEMI2K's default trusted-first-party preprocessing for the two-party M2 privacy model.
- Bypassed the SecretFlow 1.14.0b0 image's incompatible optional-dependency banner and selected its packaged no-Ray production scheduler without changing SPU, CHEETAH, or FM128.
- Passed CHEETAH/FM128 as the protobuf JSON names required by the pinned SecretFlow SPU constructor.
- Kept both production controllers on an identical cardinality-reconstruction graph and bounded the CI runtime so a failed party cannot leave its peer waiting indefinitely.
- Updated GitHub's checkout and Node setup actions to their Node 24-based v7 releases.
- Reframed the project core as a persistent encrypted state machine and inserted M2.5 before private analytics.

### Security

- Established the rule that no privacy or security claim may exceed tested implementation evidence.
- Enforced `revealIntersection=false` at both PSI peers and selected the exact `Raw` encrypted container.
- Enforced fixed-shape MPC output, excluded identifiers from the handoff, and limited reconstruction to cardinality.
- Enforced default-deny state disclosure, create-exclusive immutable state files, per-node encryption keys, and explicit authorization for every reconstruction.

### Verified

- Initial M1 validation passed nine automated tests, including a real two-process cryptographic PSI-cardinality integration test.
- The cancer-collaboration demo returns cardinality `2` with `matchedIdentifiersRevealed: false`.
- The initial locally cached production dependency audit reported zero known vulnerabilities; this is historical evidence, not a current vulnerability assessment.
- The two-container SecretFlow integration executed CHEETAH over a 128-bit ring, returned cardinality `2` at both participants, exited cleanly, and emitted none of the synthetic participant identifiers.
- Twenty-eight local unit, privacy, integration, and reproducibility tests pass for M1, M2, and the M2.5 contracts. Linux M2.5 cryptographic restart/reload evidence remains pending CI.
- Public-repository pass (2026-10-13): all 28 tests and the real PSI demo passed with local networking permitted; documentation links and ignore rules checked. No runtime, workflow, or test implementation changed. Docker was unavailable locally, so SPU was not re-executed in this pass.

