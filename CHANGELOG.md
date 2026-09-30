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

### Changed

- Adopted the product default that matched identifiers are disclosed to neither participant; only cardinality is authorized.
- Replaced the planned SecretFlow RR22 milestone backend with OpenMined PSI cardinality because RR22's mandatory receiver learns the intersection.
- Selected SPU CHEETAH instead of SEMI2K's default trusted-first-party preprocessing for the two-party M2 privacy model.

### Security

- Established the rule that no privacy or security claim may exceed tested implementation evidence.
- Enforced `revealIntersection=false` at both PSI peers and selected the exact `Raw` encrypted container.
- Enforced fixed-shape MPC output, excluded identifiers from the handoff, and limited reconstruction to cardinality.

### Verified

- Nine automated tests pass, including a real two-process cryptographic PSI-cardinality integration test.
- The cancer-collaboration demo returns cardinality `2` with `matchedIdentifiersRevealed: false`.
- The locally cached production dependency audit reports zero known vulnerabilities.

### Pending verification

- The Milestone 2 SPU runtime has not been executed in this Windows workspace because Python, Docker, and WSL are unavailable. Source or policy-test success must not be presented as cryptographic runtime evidence.

