# Threat model

## Scope

This document describes the bootstrap architecture and the planned Milestone 1 two-party PSI. It must be revised when implementation evidence changes.

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

Milestone 1 targets two non-colluding, semi-honest (honest-but-curious) parties. Each party follows the configured RR22 protocol but may inspect its local state and transcript to infer additional information. The Control Plane, when introduced, may inspect all metadata it receives but must never receive raw identifiers.

## Protected properties targeted by Milestone 1

- A party does not receive the other party's non-intersecting raw identifiers through the authorized PSI interface.
- The Control Plane receives no raw input identifiers because it is absent from the PSI data path.
- Raw CSV inputs are mounted only into their owning KryptNode container.

These properties depend on correct SecretFlow configuration, isolated mounts, non-collusion, the semi-honest assumption, and uncompromised hosts and images.

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
- Authentication of peers, signed job authorization, replay prevention, rate limits, and audit receipts.
- Side channels, including timing, memory, filesystem, CPU/cache, and container co-tenancy leakage.
- Cryptographic agility or post-quantum protection.
- Correct deletion, backup handling, disaster recovery, and production key management.
- Regulatory compliance or suitability for real patient data.

## Information leakage inherent to PSI

Authorized result recipients learn the intersection and its size. Parties may combine that result with prior knowledge. Dataset cardinality and traffic patterns may also be exposed by the implementation. Repeated or adversarial queries can amplify membership leakage; production policy must constrain them.

## Validation obligations

- Verify the exact SecretFlow protocol selected at runtime.
- Verify input mounts are disjoint and the Control Plane has none.
- Verify logs and committed files contain no raw private inputs or non-matching peer identifiers.
- Verify the result against synthetic fixtures outside the protocol only in test code that is not part of the Control Plane.
- Pin and record container image digests before any production claim.

