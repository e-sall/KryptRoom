# M4 — Persistent Private Neural Network

Status: **implemented, pending real CHEETAH/FM128 validation**.

M4 is a bounded persistent-state proof, not a general private-ML platform. It trains from the existing S1 fixed join grid, persists only the final secret model as S3, destroys the runtime, reloads S3 together with S1, evaluates privately, persists one secret MSE scalar as S4, destroys the runtime again, and permits only the commitment-bound `model.evaluation.mse` disclosure through the existing RevealService.

## Exact graph and artifacts

```text
S1 --private_nn_training--> S3_model
[S3_model, S1] --private_model_evaluation--> S4_eval
S4_eval --StatePolicy + RevealService--> authorized MSE scalar
```

Training consumes exactly `match-mask`, `lab-a-features`, and `lab-b-features`. S3 contains exactly `model-nn-layer1-weight` `[1,2]`, `model-nn-layer1-bias` `[2]`, `model-nn-output-weight` `[2,1]`, and `model-nn-output-bias` `[1]`. S4 contains only `model-evaluation-mse` `[1]`. All use float32 SPU values where applicable, remain secret-shared, and are persisted with native `SPU.dump` through the existing node-local AES-256-GCM envelope.

S1 and S3 are referenced as exact evaluation parents; S1 artifacts are not copied into S3. M3's S2 is a sibling from S1 and is not an M4 dependency.

## Fixed model and training

The model is exactly Dense 1→2, square activation, Dense 2→1. The feature is Lab A column zero divided by 10.0 and the label is Lab B column zero divided by 1000.0 inside SPU. Training uses masked MSE with the secret mask count as denominator, four full-batch vanilla gradient-descent steps, learning rate 0.4, and no shuffling. No loss, prediction, activation, gradient, feature, label, or trained parameter is reconstructed.

Initialization is public and deterministic: `kryptroom-sha256-uniform-v1`, seed 1, scale 0.30, ordered W1, b1, W2, b2. Each scalar uses the first unsigned big-endian 64 bits of SHA-256 over the version label, canonical seed, tensor name, and canonical flat index. The full generated tensor metadata and its commitment are bound into the training request.

## Commitments and policy

Training binds the S1 commitment, ordered input ArtifactRefs and descriptor commitments, selectors and normalization, canonical model/training specs and hashes, initializer metadata/commitment, code/workflow/context/input-policy/output-policy hashes, empty requested-reveal hash, output state, and ordered output artifact commitments.

Evaluation binds ordered parent IDs and commitments `[S3_model, S1]`, both policy hashes, exact ordered model and S1 ArtifactRefs/commitments, model and evaluation specs/hashes, code/workflow/context/output-policy hashes, requested-reveal hash, output state, and evaluation artifact commitment.

Legacy and M3-only S1 policies gain no permissions. A newly created M4 S1 explicitly opts into training and evaluation. S3 derives a default-deny policy allowing only evaluation over the four model artifacts. S4 has no compute permission and authorizes only `model.evaluation.mse` when that consent existed in both parents. No model-parameter reveal identifier exists.

## Acceptance fixture and boundary

The dedicated fixture has eight rows per party and six matches. The authoritative Linux gate must execute real M2 and M2.5, delete the CSVs, run direct JAX autodiff training under the pinned SecretFlow 1.14.0b0 CHEETAH/FM128 image, persist/reload S3, evaluate from reloaded S3 plus S1, persist/reload S4, reject model/unknown metric disclosure before load or reconstruction, and verify the authorized MSE is below 0.02. The exact scalar is participant-authorized and must not be copied into public CI logs.

## Limitations

The claim is limited to this deterministic bounded synthetic fixture. M4 remains two-party and semi-honest, trusts participant hosts and Docker, uses node-local key files rather than KMS/HSM, has no key rotation, signatures, anti-rollback, crash-atomic distributed commit, malicious-party protection, general numerical stability, private inference service, model registry, resumable optimizer state, DP, FHE, ZK, explainability, or biomedical-quality claim.
