# Threat model

M5 is implemented / pending real SP1 Groth16 validation. It proves metadata
consistency only, not SecretFlow execution, CHEETAH transcripts, private arithmetic,
numeric MSE, input truthfulness or participant signatures. Low-entropy metadata
may be guessed from public hashes. All existing trusted-host, semi-honest,
key-management, rollback and atomicity limitations remain. See docs/STATE_PROOF.md.

## Scope

This document describes the runtime-verified M1 PSI-cardinality, M2 private-join, and M2.5 persistent encrypted RoomState paths. Verification covers the synthetic fixtures and pinned runtimes, not a general security audit.

## Assets

- Participant raw identifiers and future feature/label datasets.
- Participant private keys and future data-encryption keys.
- Protocol inputs, intermediate state, transcripts, and outputs.
- Job manifests, code/container identities, commitments, proofs, and RunReceipts.
- Authorization policy describing which party may learn which output.
- RoomState documents, local encryption keys, encrypted SPU shares, artifact bindings, and state commitments.

## Trust boundaries

- Each KryptNode and its local storage are trusted by its owning organization.
- The network between KryptNodes is untrusted for confidentiality and integrity unless the protocol or a future authenticated transport provides those properties.
- The planned Control Plane is assumed honest for coordination but untrusted with participant plaintext; it is absent from current demos.
- Container images, host kernels, Docker daemons, operating systems, and third-party dependencies are supply-chain and execution trust dependencies.

## Initial adversary model

Milestones 1, 2, and 2.5 target two non-colluding, semi-honest (honest-but-curious) parties. Each party follows the reviewed protocol but may inspect its local state and transcript to infer additional information. The Control Plane, when introduced, may inspect all metadata it receives but must never receive raw identifiers, raw features, the private match mask, persisted shares, local state keys, or reconstructed joined rows.

## Protected properties targeted by Milestone 1

- Neither party receives matched identifiers through the authorized PSI-cardinality interface.
- Lab B learns the exact intersection cardinality; Lab A need not receive the result.
- A party does not receive the other party's non-intersecting raw identifiers through the authorized interface.
- The Control Plane receives no raw input identifiers because it is absent from the PSI data path.
- Each PSI process is configured to read only its owner's CSV. Both demo processes share a host; this is not OS-enforced cross-process or cross-user isolation.

These properties depend on correct OpenMined PSI configuration, owner-local input handling, non-collusion, the semi-honest assumption, and uncompromised hosts and dependencies.

## Protected properties targeted by Milestone 2

- Each participant container mounts only its own identifier and feature dataset.
- Identifiers are converted locally to fixed-width byte tensors and transferred from their owner PYU to SPU secret shares; neither participant receives the other party's plaintext tensor.
- Equality, padding-mask application, and feature masking execute inside a two-party SPU computation.
- The handoff contains a secret match mask and secret masked feature grids at a public fixed shape. It contains no identifier tensor.
- A second SPU computation consumes the match mask and reconstructs only the authorized cardinality to both participants.
- The Control Plane remains absent from the data path.

M2 uses SecretFlow SPU CHEETAH with FM128. CHEETAH is selected over the initial SEMI2K target because the latter defaults to an unsafe trusted-first-party Beaver provider. M2 does not add a third trusted party and does not silently weaken the two-party privacy policy.

## Protected properties targeted by Milestone 2.5

- The M2 secret match mask and masked feature grids are persisted with SecretFlow's native share serialization; they are not reconstructed for persistence.
- Each KryptNode stores only its local share and a local 256-bit state key. Keys are distinct between the two nodes and are never included in RoomState.
- Persisted share bytes are encrypted with AES-256-GCM. A fresh nonce protects every artifact, and authenticated data binds the ciphertext to its room, state, artifact, party, cipher, and crypto context.
- ArtifactRef ciphertext hashes and sizes detect local storage substitution before SPU load; AES-GCM authentication detects modification, wrong key, or wrong context during decryption.
- RoomState content is immutable through create-exclusive state and artifact writes. Its SHA-256 commitment covers policy, transition, parent list, crypto context, and artifact references.
- The post-restart analytics containers mount only node-local state. They do not mount source participant CSVs.
- SecretFlow reloads the shares into CHEETAH/FM128. Only the explicitly authorized matched-feature sum is reconstructed to Lab A and Lab B; the UI is not an aggregate recipient.
- Matched identifiers and plaintext joined rows are never authorized or materialized. The Control Plane remains absent from the data path.

## Attacker capabilities considered

- Observe or modify ordinary network traffic outside cryptographic protection.
- Inspect Control Plane storage and logs.
- Operate one participating organization and inspect that node's local state.
- Supply malformed, duplicate, or strategically chosen inputs.
- Read accidentally committed artifacts or over-verbose logs.

## Not yet protected

M3 is verified on the synthetic Linux CHEETAH/FM128 fixture. It inherits the same two-party semi-honest model. Analytics operation/input authorization is separate from reveal authorization; wrong contexts and zero-cardinality means fail before computation. Only public ciphertext descriptors cross the metadata boundary. See [M3 details and limits](docs/PRIVATE_ANALYTICS.md).

M4 is verified on the bounded synthetic Linux fixture. Its tested boundary keeps the S1 dataset, normalized values, activations, predictions, loss, gradients, and trained parameters secret; only final encrypted local model shares and an encrypted local MSE share persist. S3 and S4 inherit the same semi-honest, trusted-host limitations. The sole logical disclosure is `model.evaluation.mse`, authorized before artifact load or reconstruction through RevealService. See [M4 details and limits](docs/PRIVATE_NN.md).

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
- KMS/HSM-backed keys, key rotation, anti-rollback protection, and atomic commit or recovery across both node stores.
- Authenticity of the unsigned SHA-256 RoomState commitment against a malicious node owner; signatures and receipts remain future work.
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
- Verify the M2.5 create phase writes exactly one key, one RoomState document, and three encrypted share envelopes per KryptNode.
- Terminate both create-phase containers, start new containers without source CSV mounts, verify S1 and its commitment, and reload all artifacts through `SPU.load`.
- Execute the post-restart CHEETAH/FM128 aggregate and verify the synthetic expected result `68` at both participants.
- Verify both nodes hold byte-identical public RoomState documents, distinct local keys, and no plaintext joined dataset or synthetic patient identifier in state metadata or logs.

