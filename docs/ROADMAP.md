# Roadmap

M5 committed model-evaluation proof is **VERIFIED** by real SP1 6.9.0 CPU
Groth16 generation and independent verification. Its bounded statement is
metadata consistency; SecretFlow/CHEETAH and MPC arithmetic, numeric MSE,
participant signatures, and malicious security are not proved. See STATE_PROOF.md.

Roadmap items are ordered dependencies, not parallel feature invitations.

## Foundation

1. Threat model and protocol/job manifest.
2. Monorepo, container conventions, and common schemas.
3. Independent organization-owned KryptNodes.

## Privacy-preserving compute

4. Real exact two-party PSI cardinality with no matched-identifier disclosure.
5. Fixed-shape private join and secret-shared handoff inside SecretFlow SPU (M2).
6. Persistent encrypted RoomState layer with restart/reload continuity.
7. MPC private analytics that consume and evolve RoomStates using SecretFlow SPU.
8. Small fixed direct-JAX neural network trained and evaluated with MPC (M4 verified on bounded synthetic fixture).
9. Treatment-response prediction and gradient-based feature importance.
10. First real OpenFHE encrypted state transition: exact fixed-vector BGV addition (M6 verified on the bounded synthetic fixture).

## Verifiability and provenance

11. Canonical RunReceipt and provenance commitments.
12. Classical and post-quantum node signatures.
13. Realistic SP1 proof scope for workflow, manifest, signature, policy, and commitment statements.
14. Chain-agnostic audit anchor with an initial Base Sepolia implementation.

## Product surface and hardening

15. KryptRoom web experience.
16. Integration tests, privacy regression tests, benchmarks, reproducibility, and demo hardening.

## Milestone gates

M3 Persistent Private Cohort Analytics is verified on the synthetic Linux fixture: exactly COUNT, SUM, MEAN and CROSS_MEAN over persisted S1, producing secret scalar artifacts in S2 and a separate policy-controlled reveal after restart. See [CI evidence and limitations](PRIVATE_ANALYTICS.md).

M4 Persistent Private Neural Network passed its authoritative Linux gate: real S1 training into persistent S3, restart/reload, two-parent evaluation with S1 into persistent S4, another restart, fail-closed model disclosure, and an authorized MSE below 0.02. See [evidence and limitations](PRIVATE_NN.md).

M5 Committed State-Transition Proof passed its authoritative GitHub Actions gate: real SP1 6.9.0 CPU Groth16 generation, persisted StateProof/proof bundle, standalone verification without private state, invalid-relation and tampering negatives, witness deletion, and leakage checks. See [evidence and limitations](M5_VALIDATION.md).

M6 Persistent FHE State Transition is implemented as exact OpenFHE BGV addition
from `S5_fhe_inputs` to `S6_fhe_sum`, with participant-owned private key,
secret-key-free evaluation, persisted ciphertexts, committed context/artifacts,
and separate computation/reveal authorization. The real Linux gate passed on
the bounded synthetic fixture. See [the evidence and limitations](FHE_STATE_TRANSITION.md).

No milestone advances merely because source code exists. A gate requires executed tests, documented runtime evidence, updated threat-model limitations, and security claims that match the evidence.

Milestones 1, 2, 2.5, 3, 4, 5 and 6 are runtime-verified on their bounded synthetic fixtures. M4 evolves S1 into secret model S3, reloads it with S1 for multi-parent evaluation into secret S4, and validates fail-closed disclosure plus authorized MSE under CHEETAH/FM128. M5 proves only the committed metadata relation around that evaluation transition. M6 reloads persisted BGV-RNS ciphertexts, executes real secret-key-free `EvalAdd`, persists and reloads the child ciphertext, and separates computation from authorized decryption.

