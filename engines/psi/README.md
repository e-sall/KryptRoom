# PSI engine

Milestone 1 uses OpenMined PSI v2.0.6 in exact cardinality-only mode:

- ECDH commutative encryption.
- `Raw` encrypted container, avoiding Bloom/GCS false positives.
- `revealIntersection=false` at both peers.
- The client receives only the exact cardinality.

SecretFlow RR22 was evaluated first, as originally approved. Its v2 symmetric PSI API always designates a receiver that obtains the intersection; `broadcast_result=false` only prevents the sender from receiving it. That API therefore cannot satisfy KryptRoom's default no-identifier-disclosure policy.

This backend does not produce secret shares of matched rows. M2 implements a separate fixed-shape join inside SecretFlow SPU, recomputing identifier equality privately rather than extracting matches from PSI cardinality. That two-container CHEETAH/FM128 path is runtime-verified on the synthetic fixture; see [the MPC runtime](../mpc/README.md). This is not a claim that the PSI backend itself emits a secret-shared alignment.

## Verification

The dependency is pinned to v2.0.6 in `package.json` and the full dependency graph is locked in `package-lock.json`. Install with `npm ci --ignore-scripts`; the package's PSI WebAssembly is precompiled, while an unrelated `protoc-gen-js` post-install downloader is broken on the tested Windows environment.

On 2026-09-29, the automated suite passed 9/9 tests and the independent Lab A/Lab B process demo returned exact cardinality `2` without identifier output.

## Security model

The implementation targets honest-but-curious participants. It does not stop a modified client or server from violating the configured policy, does not authenticate peers, and has not been audited as part of KryptRoom.

