# Project context

## Product

KryptRoom is horizontal trust infrastructure for sensitive cross-organization collaboration. Its core product is encrypted compute plus collaboration—not encrypted storage, a blockchain application, a biotech company, or merely a machine-learning wrapper.

The hero use case is collaboration between two cancer-research labs. Lab A holds genomic or gene-expression features. Lab B holds clinical and treatment-response information for an overlapping patient population. Neither party authorizes raw-data disclosure to the other party, KryptRoom, or a central operator.

The long-term workflow is private schema mapping, matching, deduplication, quality analysis, analytics, private neural-network training, biomarker discovery, treatment-response prediction, explainability, proof, and audit anchoring. Only the explicitly scheduled milestone may be implemented.

## Approved architecture

- A KryptRoom Control Plane coordinates metadata and authorized artifacts but is not trusted with participant raw data.
- Every organization runs its own KryptNode.
- A KryptNode reads and preprocesses local data, owns private keys, encrypts or secret-shares locally, validates jobs, participates in cryptographic protocols, signs contributions, and releases only authorized outputs.
- The Control Plane may handle metadata, signed manifests, protocol ciphertexts or designated shares, commitments, proofs, and authorized results. It must never receive raw datasets or plaintext data-encryption keys.

## Approved technologies

- Backend: Python 3.12, FastAPI, Pydantic, PostgreSQL, Temporal, and gRPC where appropriate. SecretFlow 1.14.0b0 is isolated in its official Linux image because that release supports Python 3.10/3.11 rather than Python 3.12.
- Packaging and CI: Docker, Docker Compose, and GitHub Actions.
- PSI: SecretFlow PSI, initially real two-party exact PSI; RR22 when practical.
- MPC: SecretFlow SPU with JAX and Flax; FM128, two parties, honest-but-curious. SEMI2K remains a target only with safe preprocessing; the current two-party private join uses CHEETAH to avoid SEMI2K's trusted-first-party default.
- Private ML: a small real JAX/Flax neural network on SPU, with features, labels, gradients, weights, and loss private by default.
- FHE: OpenFHE Python bindings where practical; BFV/BGV for exact arithmetic and CKKS for approximate vector arithmetic.
- ZK: SP1 zkVM for realistic manifest, signature, commitment, policy, and output-authorization statements—not a false claim of proving full MPC training.
- Post-quantum target: OpenSSL 3.5 or newer, ML-KEM, ML-DSA, and hybrid X25519 + ML-KEM-768 key establishment.
- Artifact encryption target: random 256-bit DEK with AES-256-GCM; no plaintext DEK at the Control Plane.
- Audit target: chain-agnostic `BlockchainAnchor`, initially Base Sepolia, storing commitments and provenance only.
- Frontend, later: Next.js, TypeScript, Tailwind, shadcn/ui, and React Flow.

## Backend-to-operation mapping

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
5. MPC private analytics.
6. MPC neural-network training.
7. Treatment-response prediction and private feature importance.
8. OpenFHE private analytics.
9. Canonical RunReceipt and commitments.
10. Post-quantum signatures.
11. SP1 proof.
12. Base Sepolia registry.
13. UI.
14. Integration tests, benchmarks, and demo hardening.

Do not casually reorder this sequence or expand product scope without approval.

## Current milestone

Milestone 2 is a fixed-shape, secret-shared private join handoff into a two-party SecretFlow SPU. Identifier equality is computed inside MPC; the resulting match mask and masked feature grids remain secret SPU objects. The only authorized reconstruction is the intersection cardinality. Matched identifiers are revealed to neither participant, and any future identifier disclosure requires an explicit opt-in policy naming authorized recipients. Private analytics and ML remain out of scope.

