# M5 validation report

Status: **implemented / NOT VALIDATED — hosted runner shutdown blocks the real Groth16 gate**.
This report distinguishes implemented checks from results actually observed.
No final proof-generation or independent-verification success is claimed yet.

1. Branch: `feat/state-transition-proof`.
2. Final implementation/test/CI head: `55cf72e26631f1d3ef2070a6317a64da583b78f8` (not Groth16-validated). The last completed full hosted attempt used `efe8c3009a2e98390349d7c3379de35c45128dff`; subsequent changes add log/binary privacy assertions, their unit test, and an optional isolated runner label, not cryptographic logic. Exact implementation/fix commits, oldest first:

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
```
3. Documentation/status commit: the finalized report's commit, reported separately in the final handoff.
4. PR: [#6](https://github.com/e-sall/KryptRoom/pull/6), targeting `dev`, intentionally open and unmerged.
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
12. Guest ELF SHA-256 observed identically on `426c050` and `efe8c30`: `e6e06afd460d31db211d3eff84c031b14ebb2019b71256b651e6932e4e9c4c03`. Guest source and locked dependencies are unchanged by the final privacy-test/runner-label commit.
13. programVKey observed identically on both attempts: `0x003eba0b114a21d954c4714393c0eedf6833406b8e9b6b70ae828b3a466ea2e3`; the verifier independently derives it from its embedded expected ELF.
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
28. proof.bin SHA-256: unavailable; neither completed attempt uploaded a proof bundle. No proof hash is invented.
29. proof.bin size: unavailable for the same reason.
30. receipt.json size: the deterministic canonical receipt fixture is exactly 2,419 bytes. A final proof-bundle receipt size has not been independently observed.
31. state-proof.json size: unavailable; no completed bundle was uploaded.
32. Successful proof-generation runtime: unavailable. The two full acceptance-stage attempts lasted about 254 seconds and 2,079 seconds (34m39s) before runner shutdown. These include setup/proving and any subsequent acceptance work; buffered child output and the abrupt shutdown prevent identifying the exact internal phase reached. They are NOT successful proof-generation timings. The host implements separate setup and generation timers, but their final metrics were not emitted.
33. Standalone verification runtime: unavailable. The test is implemented to time a separate process with only public documents and trusted verifier binary, Docker disabled and HTTP(S) proxies pointing to a closed local port. No successful independent-verification result was observed.
34. Resources observed: Ubuntu 24.04 hosted runner, 15 GiB RAM, 3 GiB swap, four CPUs. Run 38912279657: acceptance-stage attempt 254 seconds before shutdown (143); sampled MemAvailable minimum 276,524 kB; SwapFree minimum 1,786,532 kB; about 83,757,360 kB free disk. Guest build 48 seconds; host build 9:57.10, peak build RSS 1,630,724 kB. Memory-bounded retry 38915045867: acceptance stage 14:32:29–15:07:08 UTC (34m39s); 70 resource samples; MemAvailable minimum 1,701,400 kB; SwapFree minimum 2,048 kB out of 3,145,724 kB; free disk minimum 83,757,248 kB (about 79.9 GiB). Guest build 39 seconds; host build 8:26.97, peak build RSS 1,632,736 kB. The runner again received shutdown signal 143. No final proving peak RSS, OOM counter or successful timing survived either shutdown, so OOM and the exact internal proving phase are not established. Disk exhaustion and the 90-minute timeout were not observed; severe swap pressure was. Official SP1CoreOpts trace/shard thresholds and bounded buffers did not yield a completed gate on this runner. [Official hardware guidance](https://docs.succinct.xyz/docs/sp1/getting-started/hardware-requirements) lists 16GB+ RAM and 16+ CPUs for Groth16, about 14GB for final wrapping alone. A larger isolated Linux runner is the recommended next profiling environment, not a proven fix for an established OOM.
35. Real Groth16 verification: **not validated**. No complete proof-generation plus independent-verification success was observed. Execute-only/native success is not final M5 validation.
36. Invalid-policy relation: Python/native checks pass. Both attempts printed `M5_GUEST_RELATION_TESTS_PASSED`: five coherent invalid relations rejected by nonzero real guest exit, valid relation accepted with the exact claim. Guest execution alone is not a final proof.
37. Mutated parent receipt: Class B tests implemented; no validated independent-verifier result is available.
38. Mutated output receipt: Class B tests implemented; no validated independent-verifier result is available.
39. Wrong-room rebinding: tests also update outer StateProof/proofId and remove caller expectations, requiring actual public-values mismatch; no validated result is available.
40. Wrong-transition rebinding: same rebinding attack and public-values requirement; no validated result is available.
41. Altered proof: descriptor tampering, truncation and valid-serialization encoded Groth16 corruption tests implemented. Corruption targets curve-proof bytes after the 96-byte encoded header. Exact SDK serialization is required, including rejection of the SDK's shorter network transport fallback. No final cryptographic test result is available.
42. Wrong programVKey: metadata/proofId is rebuilt before testing independently derived expected identity; wrong ELF/hash/program version are also tested. No final cryptographic test result is available.
43. Leakage checks: final local Python suite has 13 passing schema/metadata/privacy tests, including a unit test that private child-log markers fail without being echoed. The completed CI attempts passed 12 Python and six Rust tests; the final head must rerun CI. Proof-binary and child-log marker guards are implemented, but no completed real-proof leakage result is available. No witness, `.key` or `.share.enc` is tracked, and no common private-key/GitHub-token/AWS-key signature was found in the tracked M5 diff; this is not an exhaustive secret audit. CI uploads are an explicit public-file allowlist; both stopped attempts uploaded zero artifacts. Caches contain dependency sources only.
44. `.share.enc` reads: no M5 production path resolves ArtifactRef URIs or opens payload files; metadata/proof readers reject unsupported file extensions before reading. Fixtures contain no share files.
45. AES key reads: no M5 key-loading calls; `.key` paths are rejected by metadata readers. No key is in the fixture.
46. Participant CSV reads: no M5 CSV loading/imports; `.csv` paths are rejected by metadata readers. No CSV is in the M5 fixture.
47. M1 regression: [green on efe8c30](https://github.com/e-sall/KryptRoom/actions/runs/38915045728).
48. M2 regression: [green on efe8c30](https://github.com/e-sall/KryptRoom/actions/runs/38915045447).
49. M2.5 regression: [green on efe8c30](https://github.com/e-sall/KryptRoom/actions/runs/38915045464).
50. M3 regression: [green on efe8c30](https://github.com/e-sall/KryptRoom/actions/runs/38915045844). Locally all 17 M3 tests also passed after using a workspace temporary directory instead of the permission-restricted Windows sandbox temp directory.
51. M4 regression: [green on efe8c30](https://github.com/e-sall/KryptRoom/actions/runs/38915045588). Locally 27 passed and one Linux-specific test was skipped. Existing M1–M4 cryptographic implementations remain unchanged.
52. M5 workflow: [first full attempt 38912279657](https://github.com/e-sall/KryptRoom/actions/runs/38912279657) and [memory-bounded retry 38915045867](https://github.com/e-sall/KryptRoom/actions/runs/38915045867) both passed contracts/build/real guest tests, then failed when the runner received a shutdown signal (143). Neither was superseded by a newer push; neither hit the 90-minute job timeout. The exact provider-level shutdown cause is unavailable; do not label it a confirmed OOM or a cryptographic rejection. The public GitHub status endpoint reported no active Actions incident when checked, which does not establish an individual runner's health. Earlier build prerequisites and the SDK nonzero-exit reporting bug were diagnosed and fixed. Superseded obsolete PR runs are cancelled by concurrency; dev/main pushes are serialized. Final-head automatic CI may rerun on the same default runner, but the milestone remains unvalidated until a complete real gate succeeds.
53. README claim currently added: M5 is implemented / pending real SP1 Groth16 validation, and covers bounded metadata consistency only. The verified capability wording is intentionally withheld until the real gate passes.
54. Explicit non-guarantees: no proof of SecretFlow execution, CHEETAH/MPC transcripts, private join/analytics/training/forward-pass arithmetic, trained parameters, numeric MSE, input truthfulness, participant consent/signatures, honest hosts, anti-rollback, crash atomicity or malicious security. Code/workflow hashes are bound, not proof those programs executed.
55. Remaining limits: two-party semi-honest MPC, trusted hosts, local keys, no production KMS/HSM/rotation, unsigned state commitments and StateProof metadata, no authoritative history/approval proof, no anti-rollback/revocation, no production distributed atomic commit, SP1/Groth16 setup assumptions, Linux-only validation scope, temporary files may survive crashes, no secure-erasure guarantee. `createdAt` is local metadata, not an attested timestamp; randomized proof bytes/hash/proofId need not repeat. CI artifacts expire after seven days; production proof hosting is not implemented. Next infrastructure step: provide an isolated, pre-provisioned Linux x64 runner and set repository variable `KRYPTROOM_M5_RUNNER` to its label, then rerun the full gate. Start profiling with 16+ CPUs and 32–64 GiB RAM headroom; sufficiency is not yet measured. Never use a production KryptNode or expose participant secrets to public PR code. No paid capacity or network prover was provisioned.
56. Participant signatures: not added. “The M5 proof does not establish that participant organizations cryptographically approved or signed the transition.”
57. Blockchain: not added.
58. Full MPC correctness: not claimed. The proof covers only the bounded committed metadata relation.
59. Safe to merge into dev: **NO**. The real CPU Groth16 generation plus independent verification and all proof-tampering/leakage gates have no completed success. Provide adequate isolated runner capacity, rerun, inspect the actual results, and update status only after all gates pass. PR remains open; dev/main are unchanged. No M6, signatures, blockchain, FHE, additional ML or license was added.
