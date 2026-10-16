# M5 committed state-transition proof

Status: **implemented / pending real SP1 Groth16 validation**.

M5 proves metadata consistency for exactly `[S3_model, S1] → private_model_evaluation → S4_eval`.
It checks committed parent lineage, ordered artifact bindings, policy authorization,
CryptoContext, requested disclosure, transition commitment and child commitment.
These checks execute inside the Rust guest. Host checks alone are insufficient.

**The M5 proof does not prove correctness of the underlying SecretFlow/CHEETAH
computation or the numerical evaluation result.** It does not prove SecretFlow
executed, PSI/private-join/analytics/training/forward-pass arithmetic, model values,
input truthfulness, honest hosts, malicious security, anti-rollback or crash atomicity.
Code/workflow hashes are bound metadata, not evidence that those programs executed.

**The M5 proof does not establish that participant organizations cryptographically
approved or signed the transition.** Signatures are deferred to M5.1.

## Runtime and trusted verifier

Official SP1 `v6.9.0`, source `b8387fa61e1361d90ee7de49f551863418ca0f08`;
SDK/zkVM exactly `=6.9.0`, dependencies locked in Cargo.lock. The release reports
circuit version **v6.1.0**. Host Rust is 1.96.0; the official pinned CLI installs
`succinct-1.96.0-64bit-v3`. The final proof mode is Groth16, prover explicitly CPU.
There is no mock/network prover fallback. Setup may download public dependencies
and circuit material; the metadata witness never goes to a prover service.
Resource feasibility remains subject to the actual Linux CI gate.

The SDK's default final CPU wrapper uses the official local Gnark container for
circuit v6.1.0. M5 additionally pins it to
`ghcr.io/succinctlabs/sp1-gnark:v6.1.0@sha256:e1a1cd62838b561ca301f9b2c26475c4a92bfe0e2c916e9bba213062e1548c4d`.
This is a local CPU process, not a network prover. Standalone verification uses
the official pure Rust Groth16 verifier and does not require that Docker image.
The independent-process test receives only three public proof documents and the
verifier binary in its working directory, with Docker connectivity disabled and
HTTP(S) proxies pointing to a closed local port. This checks dependency independence;
it is not a hardened network sandbox or compromised-host protection.

The `kryptroom-proof verify` binary embeds the expected ELF at build time,
independently derives its programVKey and checks its SHA-256. It checks strict
receipt/StateProof structures, receipt/proof hashes, exact 64-byte public claim,
expected room/transition when supplied, and real SP1 Groth16 verification.
It needs no SecretFlow, KryptNode, witness, secret state, CSV, key or database.
After dependency/circuit setup, verification requires no network. Verifier/program
material must come from a trusted build. Unsigned commitments cannot establish
organizational authorship, approval, or an authoritative history.

## Formats, hashing and privacy

Strict schemas: `transition-receipt.schema.json`, `state-proof.schema.json`,
`proof-artifact.schema.json`. StateProof is external to S4; no proof hash enters
S4. Existing M1–M4 formats and SHA-256/json-sort-keys-v1 semantics are unchanged.

Public receipts expose room/state/transition IDs, fixed artifact IDs/order,
hashes, key epoch and the logical reveal identifier. Policies, full context,
holder participants/local URIs and sizes are private metadata witness fields.
Existing artifact IDs retain lab role names. Hashes do not hide low-entropy
metadata from guesses.

Witness V1 contains only the exact Python `content_dict` bytes for S3, S1 and S4
and canonical receipt bytes, base64 encoded. No participant data, share payload,
AES key, model value, gradient, activation, prediction or private numeric MSE is
read. Historical S3 float configuration is hashed as exact bytes, never rebuilt
from Rust floats. Rust recomputes only the restricted float-free evaluation
semantics; Python/Rust golden vectors verify compatibility.

- Receipt hash: SHA-256 of ASCII `KRYPTROOM-TRANSITION-RECEIPT-V1`, one NUL, then canonical receipt.
- Public claim: SHA-256 of ASCII `KRYPTROOM-STATE-PROOF-V1` with **no NUL**, followed by the raw receipt hash: exactly 64 bytes.
- Proof ID: SHA-256 of ASCII `KRYPTROOM-STATE-PROOF-ID-V1`, one NUL, raw receipt hash, raw programVKey, raw proof.bin hash; prefix `stateproof-` plus first 32 hex characters. Security does not depend on this ID.

Storage: `proofs/rooms/<roomId>/transitions/<transitionId>/<proofId>/` contains
only `receipt.json`, `proof.bin`, `state-proof.json`. Creation is exclusive.
The witness is isolated in a temporary directory, removed immediately after
reading and cleaned on ordinary errors. Crashes can leave temporary files or
memory; secure deletion and compromised-host protection are not claimed.
CI uploads only explicitly allowlisted public proof/verifier material.

## Fixtures and validation

The deterministic representative fixture uses unchanged M4 state/transition
builders and synthetic ciphertext descriptors. It contains no encrypted payload,
key, CSV, model value or private MSE and does not assert MPC execution for those
descriptors. Actual M4 execution remains independently covered by the M4 workflow.

Failure classes: A invalid private relation rejects inside the guest; B modified
receipt without reproving fails receipt/public-claim binding; C changed proof or
program fails identity, serialization or cryptographic verification. Proofs remain
valid for their own exact receipts. Anti-rebinding is not revocation/anti-rollback.

The authoritative Linux gate builds the pinned guest, tests invalid relations,
generates CPU Groth16, verifies locally, deletes the witness, launches a separate
standalone verifier, and checks public tampering/leakage. It records real setup,
build/proving/verification times, sizes, memory and disk. Execute-only success
does not validate M5. M5 is verified only after this gate and M1–M4 regressions pass.

## Remaining limits

Two parties, semi-honest MPC, trusted hosts, local keys, no production KMS/HSM or
rotation, unsigned commitments, no anti-rollback, no crash-atomic distributed
commit, no malicious-party security. Groth16 inherits SP1 proof-system/setup
assumptions. No signatures, blockchain, FHE, generic zkVM layer or M6 is added.
