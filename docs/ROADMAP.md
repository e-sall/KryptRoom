# Roadmap

Roadmap items are ordered dependencies, not parallel feature invitations.

## Foundation

1. Threat model and protocol/job manifest.
2. Monorepo, container conventions, and common schemas.
3. Independent organization-owned KryptNodes.

## Privacy-preserving compute

4. Real exact two-party PSI cardinality with no matched-identifier disclosure.
5. Circuit-PSI or secret-shared PSI handoff for a private join.
6. Persistent encrypted RoomState layer with restart/reload continuity.
7. MPC private analytics that consume and evolve RoomStates using SecretFlow SPU.
8. Small real JAX/Flax neural network trained with MPC.
9. Treatment-response prediction and gradient-based feature importance.
10. Real OpenFHE encrypted analytics.

## Verifiability and provenance

11. Canonical RunReceipt and provenance commitments.
12. Classical and post-quantum node signatures.
13. Realistic SP1 proof scope for workflow, manifest, signature, policy, and commitment statements.
14. Chain-agnostic audit anchor with an initial Base Sepolia implementation.

## Product surface and hardening

15. KryptRoom web experience.
16. Integration tests, privacy regression tests, benchmarks, reproducibility, and demo hardening.

## Milestone gates

No milestone advances merely because source code exists. A gate requires executed tests, documented runtime evidence, updated threat-model limitations, and security claims that match the evidence.

Milestones 1 and 2 are runtime-verified. Milestone 2.5 source, manifests, encrypted local state store, restart topology, and policy tests are implemented. Its gate remains open until the pinned SecretFlow container creates S1, both nodes terminate, new nodes reload S1 without source-input mounts, CHEETAH/FM128 returns the expected aggregate, and privacy/storage checks pass on a Linux Docker host.

