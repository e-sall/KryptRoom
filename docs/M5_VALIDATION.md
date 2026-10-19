# M5 validation report

Status: **M5 VERIFIED** for the bounded committed model-evaluation metadata
relation. A manual WSL2 gate and the authoritative GitHub Actions gate both
completed real SP1 6.9.0 CPU Groth16 generation, persisted public proof bundles,
standalone verification, negative tests, witness deletion and leakage checks.

KryptRoom can generate an independently verifiable zero-knowledge proof that a
committed model-evaluation state transition is consistent with its committed
lineage, artifact bindings, authorization policy, cryptographic context, and
child-state commitment without exposing the underlying collaborative data.

The M5 proof does not prove correctness of the underlying SecretFlow/CHEETAH
computation or the numerical evaluation result.

1. Branch: `feat/state-transition-proof`.
2. Authoritative proof-tested PR head: `c6778eb5fa82e533aab860bf7b0425d31ccae192`. The successful run used PR merge commit `d5f9754c6e5accf9a7cf7c198cb683f8213df5d9`, which GitHub created from that exact head and dev base `ad460f4d5a81d7c42aa32e46fbba492f1636bfdf`. Exact implementation/fix commits, oldest first:

```text
cec8ba53bf7521e389983cae67aa6210ddb3f699
48f56ec06be0a64af88bb372419a51a8052f6624
70121d94aa4b80a4a4ae82d330837ac20666e5ed
846fb0b56049f75f3fd84475360b2ce4a29cab8d
f551d62135212461bf5dabf545202f4df7697ec5
aef70de507e1f16f0f804d35bd2d66648e0ce0ac
83cbd9568354e18bc979316a71472ddd988bdfd3
b9c219077dfc6db6c086e27cb3ac5e2fc988e167
d20cfa455225e88678a4e676630bde404a7864b1
963e7b9e88d79b9f2ed006dc4deb527b62a26f29
d61e200410c01ad77f674f849f159d77c92b8d84
ab15891bff699fc71ce5247d43f19656b4efafcd
426c050bb8dbb8fad42242712f635f03c4692a1c
01fe8861409d625b0a001030bba440b3dd444dd7
efe8c3009a2e98390349d7c3379de35c45128dff
55cf72e26631f1d3ef2070a6317a64da583b78f8
c6778eb5fa82e533aab860bf7b0425d31ccae192
```
3. Documentation/status commit: the finalized report's commit, reported separately in the final handoff.
4. PR: [#6](https://github.com/e-sall/KryptRoom/pull/6), targeting `dev`. Merge status is reported in the final handoff after final-head CI.
5. Exact dev base: `ad460f4d5a81d7c42aa32e46fbba492f1636bfdf`.
6. Files added (28, including this report):

```text
.github/workflows/state-proof.yml
docs/STATE_PROOF.md
docs/M5_VALIDATION.md
engines/zk/proof_receipt.py
engines/zk/state-transition-proof/Cargo.toml
engines/zk/state-transition-proof/Cargo.lock
engines/zk/state-transition-proof/shared/Cargo.toml
engines/zk/state-transition-proof/shared/src/lib.rs
engines/zk/state-transition-proof/program/Cargo.toml
engines/zk/state-transition-proof/program/src/main.rs
engines/zk/state-transition-proof/host/Cargo.toml
engines/zk/state-transition-proof/host/src/main.rs
packages/manifests/transition-receipt.schema.json
packages/manifests/state-proof.schema.json
packages/manifests/proof-artifact.schema.json
tests/state_proof/generate_fixture.py
tests/state_proof/requirements.txt
tests/state_proof/setup_sp1.sh
tests/state_proof/run_integration.py
tests/state_proof/test_receipt.py
tests/state_proof/fixtures/S1.json
tests/state_proof/fixtures/S1.content.json
tests/state_proof/fixtures/S3_model.json
tests/state_proof/fixtures/S3_model.content.json
tests/state_proof/fixtures/S4_eval.json
tests/state_proof/fixtures/S4_eval.content.json
tests/state_proof/fixtures/receipt.json
tests/state_proof/fixtures/hashes.json
```

7. Files modified (9):

```text
.gitignore
README.md
PROJECT_CONTEXT.md
ARCHITECTURE.md
THREAT_MODEL.md
TODO.md
CHANGELOG.md
docs/DECISIONS.md
docs/ROADMAP.md
```

8. SP1 CLI and SDK: exactly `6.9.0`; official release commit `b8387fa61e1361d90ee7de49f551863418ca0f08`; all SP1 crates locked to `6.9.0` in Cargo.lock.
9. Circuit metadata: official release's `SP1_CIRCUIT_VERSION` is `v6.1.0`, distinct from SDK version. The official local Gnark wrapper is pinned to `ghcr.io/succinctlabs/sp1-gnark:v6.1.0@sha256:e1a1cd62838b561ca301f9b2c26475c4a92bfe0e2c916e9bba213062e1548c4d`.
10. Rust: host `1.96.0 (ac68faa20 2026-05-25)`; guest `rustc 1.96.0-dev`, official `succinct-1.96.0-64bit-v3` toolchain. All new Rust crates use edition 2021.
11. Final proof type: SP1 Groth16, generated explicitly with CPU. LightProver is restricted to real guest execution-only tests and verifier-key derivation; it cannot generate proofs and is not the final proof mode.
12. Successful WSL manual and GitHub Actions guest ELF SHA-256: `69528f56ceaac35f55858957a1b530a3712619f0135eb9c72f09951c1b2222c4`. The earlier hosted attempts recorded `e6e06afd460d31db211d3eff84c031b14ebb2019b71256b651e6932e4e9c4c03`; byte-identical cross-environment guest builds are therefore not claimed. Each proof binds its exact ELF, and the manual/CI builds on the authoritative WSL environment matched.
13. Successful WSL manual and GitHub Actions programVKey: `0x0013deac8d5783a6a602207736809af9f46f18c337f3725ecd1c5045b386e1b2`; the verifier independently derives it from its embedded expected ELF. The historical hosted attempts used the corresponding earlier-build vkey `0x003eba0b114a21d954c4714393c0eedf6833406b8e9b6b70ae828b3a466ea2e3`.
14. Exact TransitionReceipt schema: [transition-receipt.schema.json](../packages/manifests/transition-receipt.schema.json). All 18 fields are required, extra properties forbidden, version/domain/operator fixed, exactly two ordered parents/seven inputs/one output, fixed MSE reveal and lowercase SHA-256 hashes.
15. Exact StateProof schema: [state-proof.schema.json](../packages/manifests/state-proof.schema.json). All 16 fields are required; version, proof system, SDK/program version and output state are fixed; no signatures or optional null fields.
16. Exact ProofArtifactRef schema: [proof-artifact.schema.json](../packages/manifests/proof-artifact.schema.json). Exactly mediaType, logical URI, SHA-256 and positive sizeBytes. This is separate from encrypted-share ArtifactRef.
17. Relation: consistency of committed M4 evaluation metadata for exact ordered parents `[S3_model, S1]`, exact artifact bindings, authorization policies, CryptoContext, requested MSE disclosure, existing transition commitment and S4 state commitment. It does not prove confidential computation.
18. Guest checks: exact receipt domain/version/operator/IDs/order; SHA-256 of exact parent/child content bytes; strict relevant state structure; model-parent model-spec/lineage/code/workflow/context/policy identity; default-deny and operator/input/reveal authorization; exact recipients; pinned equal contexts and key epoch; positive authorized cohort metadata; artifact metadata/shapes/dtypes and local holder descriptors; exact model/evaluation specs; exact evaluation request; derived S4 policy; ordered output commitment; exact transition payload/hash/record; canonical S4 bytes/hash; exact public claim. Duplicate JSON keys fail. Historical S3 floats are never reserialized to regenerate its commitment.
19. SP1 public values: exactly 64 bytes: `SHA256(b"KRYPTROOM-STATE-PROOF-V1") || receiptHashBytes`. No policy/context/holder objects or collaborative values are individually exposed.
20. Private witness: version plus base64-encoded exact Python canonical S3, S1 and S4 content bytes and canonical receipt bytes. Metadata only; temporary prover-local files are deleted immediately after reading and on ordinary wrapper errors.
21. Excluded inputs: CSVs, identifiers/join keys, encrypted share payloads, AES keys, features, labels, trained weights, gradients, activations, predictions and private numeric MSE. The fixture uses synthetic ciphertext descriptors and no actual payloads; actual M4 remains independently tested.
22. Policy privacy: full policies are private witness metadata; public receipts expose their hashes and the one logical reveal identifier. Fixed choices/low-entropy metadata can be inferred or guessed; hashes are not a hiding commitment to low-entropy objects.
23. Context privacy: full CryptoContext and holder descriptors stay out of receipt/public values. The bounded program's fixed expected backend/context is public code, so this does not conceal known constants.
24. Receipt hash: `SHA256(b"KRYPTROOM-TRANSITION-RECEIPT-V1\x00" + canonical_json(receipt))`; raw 32 bytes internally, lowercase hex externally. Python/Rust golden vectors and exact domain tests cover compatibility.
25. Transition commitment: exact existing M4 `digest({operator, request, outputStateId, outputArtifactCommitments})`, compared with both receipt and S4 transition binding. No M1–M4 hash algorithm or state format changed.
26. S4 commitment: SHA-256 of exact canonical existing `content_dict` bytes, including exact ordered parents, output ArtifactRef, transition, policy and context. Rust recomputation is checked against Python golden vectors.
27. proofId: `stateproof-` plus first 32 lowercase hex characters of `SHA256(b"KRYPTROOM-STATE-PROOF-ID-V1\x00" || receiptHashBytes || programVKeyBytes || proofSha256Bytes)`. Security does not depend on the truncated ID.
28. Manual WSL2 proof.bin: 1,757 bytes, SHA-256 `c847720a828333515d4bc9e6a43a328d8525e7b381bbfbb8c2c165d19b6042e1`, proofId `stateproof-7eb0ec0d4cd5ca5b841769c55e667d39`.
29. Authoritative GitHub Actions proof.bin: 1,757 bytes, SHA-256 `08a68f2f840e69a572e85b9ee3f0c6e9f682fae6033272e61d7cf56012b24c6a`, proofId `stateproof-33f2bbd7d40285950f4d85dfd329b2bb`. Randomized proof bytes, hashes and proof IDs are expected to differ between valid runs.
30. Successful public bundle sizes in both runs: receipt.json 2,419 bytes, state-proof.json 1,145 bytes, proof.bin 1,757 bytes.
31. Manual WSL2 gate: Ubuntu 24.04/WSL2, 18 logical CPUs, about 24 GiB RAM and 24 GiB swap; proof generation 1,532.46 seconds (25m32s), standalone verification 3.28 seconds, total integration 1,580.12 seconds. GNU time reported 20,351,972 KiB max RSS. Sampling recorded about 134 MiB minimum MemAvailable, about 7.90 GiB maximum swap use and about 45.9 GiB minimum free `/mnt/c`. The retained evidence is outside Git at `~/kryptroom-validation/groth16-public`, `groth16.log`, `resources.jsonl` and `gate-result.json`.
32. Authoritative GitHub Actions gate: [workflow run 38922127315, attempt 2](https://github.com/e-sall/KryptRoom/actions/runs/38922127315), [real proof job 117738187007](https://github.com/e-sall/KryptRoom/actions/runs/38922127315/job/117738187007), exact PR head `c6778eb5fa82e533aab860bf7b0425d31ccae192`. Proof generation 1,334.07 seconds (22m14s), standalone verification 3.74 seconds, total acceptance integration 1,387.65 seconds; the full job took 33m22s including checkout, builds, diagnostics, artifact and cache handling.
33. CI resources: 18 CPUs, about 24 GiB RAM and 24 GiB swap. GNU time reported 20,413,424 KiB (19.47 GiB) max RSS. Thirty-second samples recorded minimum MemAvailable 150,380 KiB (146.9 MiB) and minimum SwapFree 16,212,988 KiB, or about 8.54 GiB maximum sampled swap use. The runner work filesystem retained about 934 GiB; host `/mnt/c` had about 45 GiB free near peak use.
34. Historical hosted failures are preserved: [first full attempt 38912279657](https://github.com/e-sall/KryptRoom/actions/runs/38912279657) and [memory-bounded retry 38915045867](https://github.com/e-sall/KryptRoom/actions/runs/38915045867) passed contracts/build/real guest tests, then received runner shutdown signal 143 under measured memory/swap pressure. Neither hit the 90-minute timeout. The provider-level cause remains unavailable; these are not labeled confirmed OOMs or cryptographic rejections.
35. Real Groth16 verification: **validated**. Both the retained manual run and authoritative GitHub Actions completed proof generation and independent verification. Execute-only/native success remains insufficient on its own.
36. Invalid relations: passed. Five coherently rebound cases—unauthorized reveal, unauthorized operator, wrong CryptoContext, forbidden identifier-bearing input and wrong recipients—failed in the real SP1 guest; the valid relation succeeded.
37. Parent/lineage and output tampering: passed. Altered parent state commitment/ID/policy, input artifact commitment/ID, output artifact commitment/ID, parent/input order and output-state/transition fields all failed verification.
38. Room and transition rebinding: passed after also rebuilding untrusted outer StateProof/proofId metadata and removing caller expectations; the independently verified public values rejected each rebinding.
39. Receipt tampering: passed for room, transition, operator, output-state commitment/ID, requested reveal, code/workflow hashes, transition commitment, key epoch, CryptoContext hash, reveal hash and output-policy hash.
40. Altered proof: passed. Descriptor mismatch, truncation, serialization mutation and encoded Groth16 curve-proof corruption all failed; the cryptographic corruption still failed after updating the public descriptor and proofId.
41. Program identity: passed. Wrong programVKey, ELF hash, program version, proof-system version and candidate guest ELF failed.
42. Standalone verifier isolation: passed in a separate process containing only receipt.json, state-proof.json, proof.bin and the verifier binary. Docker was forced unavailable and HTTP(S)/ALL proxy endpoints were closed; verification succeeded without SecretFlow, private RoomState content or network access.
43. Leakage checks: passed. Public documents, public values, captured child logs and proof bytes contained none of the guarded payload/key/private-metadata markers. The output directory contained only the three public files, and GitHub uploaded only the explicit public allowlist plus verifier/ELF. No private fixture, witness, `.key`, `.share.enc` or CSV was uploaded.
44. Witness deletion: passed. The valid witness was deleted immediately after prover read; invalid witnesses were removed; no witness was persisted in the proof bundle or artifact.
45. `.share.enc` and AES key reads: none. The M5 path resolves no ArtifactRef payload URI, fixtures contain no shares/keys, unsupported extensions are rejected before reads, and the acceptance metric reported `noSecretPayloadReads: true`.
46. Participant CSV reads: none. The M5 integration imports no participant CSV and its fixtures contain no CSV.
47. M1 regression: [green on c6778eb](https://github.com/e-sall/KryptRoom/actions/runs/38922127143).
48. M2 regression: [green on c6778eb](https://github.com/e-sall/KryptRoom/actions/runs/38922127127).
49. M2.5 regression: [green on c6778eb](https://github.com/e-sall/KryptRoom/actions/runs/38922127067).
50. M3 regression: [green on c6778eb](https://github.com/e-sall/KryptRoom/actions/runs/38922127079).
51. M4 regression: [green on c6778eb](https://github.com/e-sall/KryptRoom/actions/runs/38922127104). Existing M1–M4 cryptographic implementations remain unchanged.
52. M5 workflow: [green authoritative run](https://github.com/e-sall/KryptRoom/actions/runs/38922127315). The repository-scoped runner `kryptroom-m5-local-4b51feb7` had a unique label, was configured ephemeral/unattended, accepted exactly one job, removed its credentials/configuration, exited successfully and disappeared from the repository runner list.
53. README claim: M5 is verified for the bounded committed metadata relation. The allowed capability statement is immediately followed by the SecretFlow/CHEETAH and numerical-correctness limitation.
54. Explicit non-guarantees: no proof of SecretFlow execution, CHEETAH/MPC transcripts, private join/analytics/training/forward-pass arithmetic, trained parameters, numeric MSE, input truthfulness, participant consent/signatures, honest hosts, anti-rollback, crash atomicity or malicious security. Code/workflow hashes are bound, not proof those programs executed.
55. Remaining limits: two-party semi-honest MPC, trusted hosts, local keys, no production KMS/HSM/rotation, unsigned state commitments and StateProof metadata, no authoritative history/approval proof, no anti-rollback/revocation, no production distributed atomic commit, SP1/Groth16 setup assumptions, Linux-only validation scope, temporary files may survive crashes, and no secure-erasure guarantee. `createdAt` is local metadata, not an attested timestamp; randomized proof bytes/hash/proofId need not repeat. CI artifacts expire after seven days; production proof hosting is not implemented. The successful machine had 18 CPUs, about 24 GiB RAM and 24 GiB swap and ran very near its memory limit; this is measured sufficiency for the bounded fixture, not general sizing guidance. Never use a production KryptNode or expose participant secrets to public PR code. No paid service, cloud/network prover or production data was used.
56. Participant signatures: not added. “The M5 proof does not establish that participant organizations cryptographically approved or signed the transition.”
57. Blockchain: not added.
58. Full MPC correctness: not claimed. The proof covers only the bounded committed metadata relation.
59. Merge result: **M5 was merged into dev at `6f01e3c412252d20b57c2a233df8f4ac8020e769` after the documentation-only final head and all required checks were green**. The real CPU Groth16 generation, independent verification, proof-tampering/identity negatives and leakage gates completed successfully. M5 itself added no M6, signatures, blockchain, FHE, additional ML or license.
