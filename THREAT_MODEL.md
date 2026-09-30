# Threat model

## Scope

This document describes the verified Milestone 1 PSI-cardinality path and the implemented, not-yet-runtime-verified Milestone 2 private join handoff. It must be revised when execution evidence changes.

## Assets

- Participant raw identifiers and future feature/label datasets.
- Participant private keys and future data-encryption keys.
- Protocol inputs, intermediate state, transcripts, and outputs.
- Job manifests, code/container identities, commitments, proofs, and RunReceipts.
- Authorization policy describing which party may learn which output.

## Trust boundaries

- Each KryptNode and its local storage are trusted by its owning organization.
- The network between KryptNodes is untrusted for confidentiality and integrity unless the protocol or a future authenticated transport provides those properties.
- The Control Plane is honest for coordination but untrusted with participant plaintext.
- Container images, host kernels, Docker daemons, operating systems, and third-party dependencies are supply-chain and execution trust dependencies.

## Initial adversary model

Milestones 1 and 2 target two non-colluding, semi-honest (honest-but-curious) parties. Each party follows the reviewed protocol but may inspect its local state and transcript to infer additional information. The Control Plane, when introduced, may inspect all metadata it receives but must never receive raw identifiers, raw features, the private match mask, or reconstructed joined rows.

## Protected properties targeted by Milestone 1

- Neither party receives matched identifiers through the authorized PSI-cardinality interface.
- Lab B learns the exact intersection cardinality; Lab A need not receive the result.
- A party does not receive the other party's non-intersecting raw identifiers through the authorized interface.
- The Control Plane receives no raw input identifiers because it is absent from the PSI data path.
- Raw CSV inputs are mounted only into their owning KryptNode container.

These properties depend on correct OpenMined PSI configuration, isolated mounts, non-collusion, the semi-honest assumption, and uncompromised hosts and dependencies.

## Protected properties targeted by Milestone 2

- Each participant container mounts only its own identifier and feature dataset.
- Identifiers are converted locally to fixed-width byte tensors and transferred from their owner PYU to SPU secret shares; neither participant receives the other party's plaintext tensor.
- Equality, padding-mask application, and feature masking execute inside a two-party SPU computation.
- The handoff contains a secret match mask and secret masked feature grids at a public fixed shape. It contains no identifier tensor.
- A second SPU computation consumes the match mask and reconstructs only the authorized cardinality to the local participant.
- The Control Plane remains absent from the data path.

M2 uses SecretFlow SPU CHEETAH with FM128. CHEETAH is selected over the initial SEMI2K target because the latter defaults to an unsafe trusted-first-party Beaver provider. M2 does not add a third trusted party and does not silently weaken the two-party privacy policy.

## Attacker capabilities considered

- Observe or modify ordinary network traffic outside cryptographic protection.
- Inspect Control Plane storage and logs.
- Operate one participating organization and inspect that node's local state.
- Supply malformed, duplicate, or strategically chosen inputs.
- Read accidentally committed artifacts or over-verbose logs.

## Not yet protected

- Malicious parties that deviate from the protocol.
- Collusion between participating parties, the Control Plane, or host operators.
- Compromised participant hosts, Docker daemons, kernels, or container images.
- Input poisoning, membership-inference attacks from repeated/adaptive PSI queries, or minimum-set-size policy abuse.
- Traffic analysis, protocol denial of service, and availability.
- Leakage of the configured public capacity and fixed tensor shapes.
- Authentication of peers, signed job authorization, replay prevention, rate limits, and audit receipts.
- Side channels, including timing, memory, filesystem, CPU/cache, and container co-tenancy leakage.
- Cryptographic agility or post-quantum protection.
- Correct deletion, backup handling, disaster recovery, and production key management.
- Regulatory compliance or suitability for real patient data.

## Information leakage inherent to PSI cardinality

Authorized result recipients learn the exact intersection size. They may combine that number with their own dataset or prior knowledge; small sets can make individual membership inferable even without identifier output. Each peer learns the other input's declared cardinality, and traffic patterns may expose additional size information. Repeated or adversarial queries can amplify membership leakage; production policy must constrain them.

The honest-but-curious model assumes both peers run the reviewed binaries and honor the manifests. A malicious or modified peer is outside the current model and may attempt policy bypasses or chosen-input attacks.

## Validation obligations

- Verify OpenMined PSI v2.0.6, ECDH mode, `Raw` exact container, and identifier revelation disabled at runtime.
- Verify input mounts are disjoint and the Control Plane has none.
- Verify logs and committed files contain no raw private inputs or non-matching peer identifiers.
- Verify the result against synthetic fixtures outside the protocol only in test code that is not part of the Control Plane.
- Pin the full dependency graph before any production claim.
- Execute the two-container CHEETAH/FM128 private join and verify cardinality `2` on a Linux Docker runner.
- Verify both processes emit only cardinality and non-sensitive handoff metadata, with no identifiers or feature rows in logs.
- Verify the match mask and masked feature grids remain SPUObjects and are consumed by a subsequent SPU call without reconstruction.

