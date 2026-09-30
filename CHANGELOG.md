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

### Changed

- Adopted the product default that matched identifiers are disclosed to neither participant; only cardinality is authorized.
- Replaced the planned SecretFlow RR22 milestone backend with OpenMined PSI cardinality because RR22's mandatory receiver learns the intersection.

### Security

- Established the rule that no privacy or security claim may exceed tested implementation evidence.
- Enforced `revealIntersection=false` at both PSI peers and selected the exact `Raw` encrypted container.

