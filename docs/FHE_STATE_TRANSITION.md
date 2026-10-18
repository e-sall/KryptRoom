# M6 persistent FHE state transition

## Status

**Implemented; real Linux/OpenFHE CI validation pending.** Source-only and contract
tests are not sufficient to call M6 verified. The authoritative gate is
`.github/workflows/fhe-state-transition.yml` and must complete its real
`M6 real persistent OpenFHE BGV` job before this status changes.

M6 is based on `dev` commit
`ad460f4d5a81d7c42aa32e46fbba492f1636bfdf`. It does not depend on the
concurrent M5 branch or alter the M5 proof relation.

## Bounded operation

M6 implements exactly one transition:

```text
S5_fhe_inputs
  fhe-vector-lab-a (BGV ciphertext)
  fhe-vector-lab-b (BGV ciphertext)
        |
        | authorized OpenFHE EvalAdd, no secret key
        v
S6_fhe_sum
  fhe-vector-sum (BGV ciphertext)
        |
        | separately authorized key-owner reveal
        v
four exact integers to Lab A and Lab B
```

The two input vectors have a fixed public length of four. This is an
architecture-validation fixture, not a general FHE analytics API.

## Exact runtime and parameters

- Backend: official OpenFHE Python bindings.
- Package: `openfhe==1.5.1.0.24.4` for Ubuntu 24.04 / Python 3.12.
- Wheel SHA-256:
  `b39f50f570ea1236dc8a8c64b01552848eb66c068592c4178fa37249f182106e`.
- Scheme: BGV-RNS exact integer arithmetic.
- Plaintext modulus: 65537.
- Multiplicative depth: 0.
- Batch size: 4.
- Security parameter request: `HEStd_128_classic`.
- Ring dimension: selected by OpenFHE and recorded in the committed
  `CryptoContext` after context creation.
- Serialization: OpenFHE binary format.
- Evaluation operation set: `EvalAdd` only; no evaluation key is required or
  generated for ciphertext addition.

The security level above is a parameter selection passed to OpenFHE. It is not
an independent cryptographic audit or a production-system security claim.

## Key ownership and storage

Lab A is the single M6 V1 key owner. The private BGV key is serialized only in
Lab A's participant-owned private root. Its path and bytes are absent from
`RoomState`, `CryptoContext`, `ArtifactRef`, the evaluator roots, the Control
Plane fixture, logs, and uploaded CI artifacts. Public context and public-key
files are digest-bound through `CryptoContext.publicMaterialRefs`.

This is deliberately not threshold or multiparty FHE. Lab A can decrypt any
ciphertext under this key outside KryptRoom's policy boundary if it controls a
modified host. M6 demonstrates the reviewed interface and separation of duties,
not cryptographic enforcement against a malicious key owner.

## Persistence and commitments

Participant-local plaintext fixtures exist only before encryption and are
deleted before evaluation. Input ciphertexts are stored under their participant
artifact roots. The evaluator receives only the public context and committed
ciphertexts, reloads them in a new process, executes `EvalAdd`, and persists the
child ciphertext under the evaluator artifact root. A later process reloads the
child state for the explicit reveal.

FHE artifacts set `protection: fhe_ciphertext`. Their `ArtifactRef` contains
the actual OpenFHE binary size and SHA-256 digest. The transition binds the exact
parent commitment, ordered artifact descriptors and artifact commitments,
policy, crypto context, code hash, workflow hash, requested-reveal hash, output
descriptor, and transition commitment. `RoomState` continues using the existing
sorted-key JSON and SHA-256 commitment semantics.

The resolver rejects an unavailable holder, path traversal, changed size,
changed digest, wrong context, or wrong key epoch before backend use. State files
remain create-exclusive and immutable.

## Policy and reveal boundary

The computation job requests zero reveals. `StatePolicy` separately authorizes
the exact `fhe_vector_add` operator and the two exact input artifact IDs. The
child inherits the same default-deny policy. `FHERevealService` checks the exact
`fhe.vector-sum` disclosure and recipients `[lab-a, lab-b]` before reading the
ciphertext, public material, or private key. An unauthorized UI reveal fails
before reconstruction.

## Acceptance chain

The real CI test must show all of the following in separate processes:

1. generate a real BGV context and Lab A key pair;
2. encrypt one participant-local vector for each lab;
3. persist committed input state `S5_fhe_inputs`;
4. delete both plaintext input files and end all input processes;
5. reload public material and both ciphertexts without a private-key path;
6. reject an unauthorized operator and a tampered input ciphertext;
7. execute real `OpenFHE.EvalAdd` and persist `S6_fhe_sum`;
8. reload and validate the immutable child state and lineage;
9. reject an unauthorized reveal before private-key access;
10. authorize Lab A and Lab B, decrypt, and obtain `[16, 22, 26, 34]`;
11. reject a tampered child ciphertext before decryption;
12. scan shared state/artifact storage for the private key and plaintext input
    encodings.

## Guarantees and non-guarantees

When the real gate passes, M6 demonstrates a persisted OpenFHE ciphertext state,
secret-key-free homomorphic addition, a new committed ciphertext state, restart
continuity, tamper-detecting descriptor checks, context/key-epoch binding, and a
separate authorized decryption boundary for the bounded fixture.

It does not provide malicious security, threshold/multiparty FHE, arbitrary FHE
programs, encrypted neural networks, input authenticity, participant signatures,
ZK proof of FHE arithmetic, compromised-host protection, side-channel resistance,
production KMS/HSM, key rotation/recovery, anti-rollback, quantum-security proof,
or a production Control Plane. M5, when integrated separately, proves committed
transition metadata rather than this FHE arithmetic.
