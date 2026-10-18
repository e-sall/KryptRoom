# Project context

## Product

KryptRoom is a persistent encrypted state machine for collaboration between mutually distrustful organizations. Private computations evolve immutable `RoomState` objects whose artifacts remain secret-shared and locally encrypted at participant-owned KryptNodes or remain committed FHE ciphertexts across authorized homomorphic transitions. KryptRoom is not a central encrypted-storage service, a blockchain application, a biotech company, or a machine-learning wrapper.

The hero use case is collaboration between two cancer-research labs. Lab A holds genomic or gene-expression features. Lab B holds clinical and treatment-response information for an overlapping patient population. Neither party authorizes raw-data disclosure to the other party, KryptRoom, or a central operator.

The long-term workflow is private schema mapping, matching, deduplication, quality analysis, analytics, private neural-network training, biomarker discovery, treatment-response prediction, explainability, proof, and audit anchoring. Only the explicitly scheduled milestone may be implemented.

## Approved architecture (target and implementation boundaries)

M1, M2, and M2.5 are runtime-verified on synthetic fixtures. The Control Plane, node identity, signatures, proofs, and production job orchestration below are architectural targets, not deployed capabilities. See ARCHITECTURE.md for the current runtime boundary.

- A KryptRoom Control Plane coordinates metadata and authorized artifacts but is not trusted with participant raw data.
- Every organization runs its own KryptNode.
- A KryptNode reads and preprocesses local data, owns private keys, encrypts or secret-shares locally, validates jobs, participates in cryptographic protocols, signs contributions, and releases only authorized outputs.
- The Control Plane may handle metadata, signed manifests, protocol ciphertexts or designated shares, commitments, proofs, and authorized results. It must never receive raw datasets or plaintext data-encryption keys.
- A `RoomState` is immutable. It names zero or more parent states through a list-valued `parent_state_ids`, binds each `ArtifactRef` to a `CryptoContext`, records the authorized `StateTransition` and `StatePolicy`, and carries a deterministic `StateCommitment`.
- Secret-share artifacts are stored only in the participant-owned KryptNode that holds the share. Persisted shares are encrypted at rest; a RoomState never embeds plaintext shares, matched identifiers, or joined rows.

## Current runtime and future technology direction

- Future application backend: Python 3.12, FastAPI, Pydantic, PostgreSQL, Temporal, and gRPC where appropriate; these services are not implemented. SecretFlow 1.14.0b0 is isolated in its official Linux image because that release supports Python 3.10/3.11 rather than Python 3.12.
- Packaging and CI: Docker, Docker Compose, and GitHub Actions.
- Current PSI: OpenMined PSI v2.0.6, exact ECDH cardinality-only mode. ADR-006 supersedes the original SecretFlow RR22 plan because that interface reveals identifiers to its receiver.
- Current MPC: SecretFlow SPU with JAX; CHEETAH/FM128, two parties, honest-but-curious. CHEETAH avoids SEMI2K's trusted-first-party default.
- Current M4: a fixed direct-JAX Dense 1→2→1 square-activation network on SPU, with features, labels, activations, gradients, weights, predictions, and loss private by default. Its authoritative real CHEETAH/FM128 persistence/restart chain is verified on the bounded synthetic fixture.
- Current M6 FHE: official OpenFHE Python 1.5.1.0.24.4 with exact BGV-RNS addition of two fixed four-integer ciphertext vectors. Lab A is the single private-key owner; the evaluator has only public material. Implementation is complete, but real CI validation is pending.
- Future ZK: SP1 zkVM for realistic manifest, signature, commitment, policy, and output-authorization statements—not a false claim of proving full MPC training. Not implemented.
- Post-quantum target: OpenSSL 3.5 or newer, ML-KEM, ML-DSA, and hybrid X25519 + ML-KEM-768 key establishment.
- Artifact encryption: AES-256-GCM with random nonces and node-local 256-bit keys for M2.5. No plaintext key reaches another participant or the Control Plane. Production KMS/HSM integration remains future work.
- Audit target: chain-agnostic `BlockchainAnchor`, initially Base Sepolia, storing commitments and provenance only.
- Frontend, later: Next.js, TypeScript, Tailwind, shadcn/ui, and React Flow.

## Target backend-to-operation mapping (not a capability inventory)

- Exact matching: PSI.
- Exact private join: PSI plus MPC.
- Exact encrypted count and sum: BFV/BGV.
- Mean, variance, and vector arithmetic: CKKS.
- Comparisons and branching: MPC.
- Neural-network training, gradients, weights, and initial private inference: MPC.
- Selective disclosure: ZK.
- Provenance: signatures and commitments.
- Immutable audit anchor: blockchain.

## Canonical receipt target

`RunReceipt` will eventually cover room and run identifiers, workflow/code/container hashes, input/output/model commitments, cryptographic backends and parameters, participants, and start/completion times. Each KryptNode will sign the receipt.

## Build order

0. Threat model and protocol/job manifest.
1. Monorepo, Docker, and common schemas.
2. Two independent KryptNodes.
3. Real PSI private matching.
4. Secret-shared private join handoff into MPC.
5. Persistent encrypted RoomState layer.
6. MPC private analytics that consume and evolve RoomStates.
7. MPC neural-network training.
8. Treatment-response prediction and private feature importance.
9. OpenFHE private analytics.
10. Canonical RunReceipt and provenance commitments.
11. Post-quantum signatures.
12. SP1 proof.
13. Base Sepolia registry.
14. UI.
15. Integration tests, benchmarks, and demo hardening.

Do not casually reorder this sequence or expand product scope without approval.

## Current milestone

M6 Persistent FHE State Transition is implemented against dev commit
`ad460f4d5a81d7c42aa32e46fbba492f1636bfdf`, independently of concurrent M5.
It persists two OpenFHE BGV ciphertexts as `S5_fhe_inputs`, reloads them in a
private-key-free evaluator, applies one authorized `EvalAdd`, persists
`S6_fhe_sum`, and permits only a separately authorized Lab A/Lab B decryption.
The official wheel, scheme parameters, key epoch/owner, public material, artifact
digests, policy, code/workflow, lineage, and transition are committed. Real CI
validation is pending; see docs/FHE_STATE_TRANSITION.md.

M4 Persistent Private Neural Network is verified on the bounded synthetic Linux CHEETAH/FM128 fixture. It consumes S1 directly, persists exactly four final secret model tensors as S3, reloads S3 with S1 for exact multi-parent private evaluation, and persists one secret MSE scalar as S4. See docs/PRIVATE_NN.md. This does not make KryptRoom a general ML platform.

M3 Persistent Private Cohort Analytics is verified on the synthetic Linux CHEETAH/FM128 fixture. It reuses S1's persisted share grids for exactly COUNT, SUM, MEAN and CROSS_MEAN, persists scalar artifacts in S2, and separates computation authorization from scalar reveal authorization. See docs/PRIVATE_ANALYTICS.md for exact bindings, numeric tolerance and acceptance evidence.

Milestone 2.5 persists the validated M2 handoff as immutable RoomState S1. Each KryptNode encrypts its local SPU shares at rest with AES-256-GCM; authenticated-data bindings cover the room, state, artifact, party, and crypto-context identifiers. The Linux acceptance test terminated both node containers, loaded S1 in new containers through SecretFlow's native SPU share dump/load boundary, and ran a minimal private aggregate without remounting source CSVs. The verified result is specific to the synthetic fixture and current pinned runtime.

The disclosure default remains deny. Cardinality may be released to Lab A, Lab B, and the UI. The synthetic M2.5 aggregate, explicitly opted-in M3 scalars, M4 evaluation MSE, and M6 vector sum are authorized only to their exact named participants. Matched identifiers, plaintext joined rows, model parameters, predictions, gradients, and activations remain forbidden. ML beyond the fixed M4 network, FHE beyond the bounded M6 addition, threshold/multiparty FHE, ZK proof of FHE arithmetic, blockchain, frontend, branching/merge behavior, and dynamic membership remain out of scope.
