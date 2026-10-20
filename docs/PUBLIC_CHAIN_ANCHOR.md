# M7 public blockchain anchor

## Status

**IMPLEMENTED / LIVE RECOVERY PENDING.** The stateless Solidity contract,
Foundry tests, exact commitment implementation, immutable off-chain records,
Base finality/reorg verifier, schemas, deterministic vectors, M6 state-only
coverage, privacy tests, and CI are implemented. Live run 39377159223 created
the authoritative Base Sepolia V1 contract at
`0xd090b5f1834d41c1db39cfbb642edb3acbbce96b` in transaction
`0x86fa94f71d74ee43bb87ca2c0b31b0f0f69938936dc3d9c71bf56bda4f706f9a`.
The run then failed on an HTTP 403 before manifest construction, and its anchor
step was skipped. The deployment has since passed read-only chain, receipt,
canonicality, and exact-runtime validation. M7 becomes **VERIFIED** only after
recovery publishes the single acceptance anchor, reaches `finalized`, and the
standalone verifier passes against that exact inclusion.

Short claim: **Publicly anchor private collaboration state without publishing it.**

## Protocol boundary

M7 is public audit/provenance anchoring, not a blockchain state machine. The
permissionless `KryptRoomAnchorV1` contract has no storage, owner, administrator,
proxy, token, payment logic, or registry. It rejects zero and emits only:

```solidity
event AnchorRecorded(bytes32 indexed anchorCommitment, address indexed submitter);
```

The submitter is an Ethereum transaction sender. It is not a KryptRoom
participant identity, authorization, organizational identity, or approval.
Duplicate commitments are legal and produce distinct chain inclusions.

## Exact commitments

All integer tags below are one byte. All commitments are raw 32-byte values.

```text
AnchorCommitment = SHA256(
  ASCII("KRYPTROOM-CHAIN-ANCHOR-V1") || 0x00 ||
  0x01 || outputStateCommitment ||
  evidenceType || evidenceCommitment
)

0x01 subject type = ROOM_STATE_V1
0x00 evidence type = NONE, evidenceCommitment = ZERO32
0x01 evidence type = STATE_PROOF_V1

StateProofDocumentCommitment = SHA256(
  ASCII("KRYPTROOM-STATE-PROOF-DOCUMENT-V1") || 0x00 ||
  canonical_json(StateProof)
)
```

`canonical_json` is imported from the existing RoomState implementation. M7
does not define a second serializer. The StateProof document transitively binds
its receipt, transition/output commitments, program verification key, proof
artifact digest, and public-values digest. `proof.bin` stays off-chain.

The committed deterministic vectors are:

- output state commitment:
  `4783c68ffbae1b11475a009ccd421b15045287929143d0f975cb1842933d7a62`
- state-only AnchorCommitment:
  `0xbeb356e0fb84d976fea8d349f10d6aec168811e1ffc92fbea8b2ee4a04eb62d9`
- StateProofDocumentCommitment:
  `c2f9b2538e52d8bcf5cd77862fac7366c4b19bdfb21a9a79df60b2dca7fbca5e`
- state-plus-proof AnchorCommitment:
  `0x5141aa2f8e8903860db82dd06e6b9a6edf2a2b4ac170a9f7ba08c1a183b6b7a6`

## Records and finality

`ChainAnchor` is an immutable off-chain inclusion record. It contains the
package identity, Base chain and contract identity, transaction/log identity,
runtime bytecode hash, and inclusion block. It is not part of RoomState and
never mutates RoomState. Its deterministic `anchorId` hashes fixed-width
chainId, contract address, transaction hash, and log index under
`KRYPTROOM-CHAIN-ANCHOR-ID-V1\0`.

Dynamic status is a separate `AnchorStatusRecord`: `PENDING`, `CONFIRMED`,
`FINALIZED`, `ORPHANED`, or `FAILED`. Base Sepolia is chain ID 84532. The
verifier uses the RPC `safe` and `finalized` heads, not an invented confirmation
count. It checks successful receipt, exact contract/event/log/commitment,
canonical block and hash, deployed runtime code hash, and ancestry from the
safe/finalized head. A disappeared or removed inclusion is `ORPHANED`; its
immutable record remains historical, and resubmission creates a new anchor ID.

## Independent verification layers

1. **Layer A — chain:** validates chain ID, deployed code, receipt, event,
   exact log index, block consistency, canonicality, and required finality.
2. **Layer B — package:** verifies the supplied RoomState with existing
   commitment semantics, optionally hashes the exact StateProof document, and
   recomputes the AnchorCommitment. It never resolves RoomState artifact URIs.
3. **Layer C — M5 proof:** when evidence is `STATE_PROOF_V1`, invokes the
   existing M5 standalone verifier as an explicit separate step. Matching the
   document hash is not proof validation.

State-only anchors use evidence `NONE` and ZERO32. The M6 test constructs S6,
deletes all local FHE material, then successfully performs Layer B using only
the committed RoomState representation. No ciphertext, OpenFHE key/context
file, or plaintext vector is read by M7.

## Deployment and key handling

The target is one authoritative Base Sepolia V1 deployment. Foundry is pinned
to 1.8.5 and Solidity to 0.8.37. The deployment manifest binds chain ID,
address, deployment transaction/block, runtime Keccak-256, tool versions, and
timestamp. Deployment and anchor helpers consume `BASE_SEPOLIA_RPC_URL` from
the environment. A limited testnet key named `M7_TEST_ANCHOR_PRIVATE_KEY` must
exist only in the protected `base-sepolia-m7` GitHub environment; it is never a
participant identity and must not be logged, persisted, or uploaded.

No manifest, address, or transaction is fabricated when these controls are
unavailable. Mainnet is outside scope.

The manual `Public Chain Anchor Live Acceptance` workflow requires an explicit
mode and mode-specific confirmation phrase and serializes all V1 attempts.
`resume_existing_deployment` requires both normalized deployment identifiers,
never invokes `forge create`, validates the creation transaction, successful
receipt, canonical block, and exact pinned runtime, and refuses an already
recorded acceptance commitment before sending anything. `deploy` additionally
requires and pins the expected deployer nonce so a retry of the same attempt
cannot silently redeploy. The workflow then publishes one deterministic
state-only acceptance anchor, waits for `finalized`, runs the standalone
verifier, and uploads only the public manifest/record/status/result. If a run
fails after anchor publication, the duplicate preflight fails closed and a
separate evidence-only recovery decision is required.

## CI policy

Fast M5 regression and real proving are separate. The ordinary M5 workflow
covers canonicalization, fixtures, Python and Rust guest tests, tampering, and
standalone-verifier behavior. The real CPU Groth16 acceptance workflow runs
only for changes to the M5 relation/serialization/public semantics/tooling or
by explicit dispatch. Unrelated M7 commits do not regenerate a proof.

The M7 workflow compiles and tests the contract, regenerates exact vectors,
runs package/chain/reorg/privacy negatives, and compiles the Python entrypoints.
Local and CI tests are implementation evidence, not live-chain validation.

## Guarantees and limitations

After live acceptance, a finalized public-chain block can contain an
AnchorCommitment that an independent verifier can recompute from the exact
supplied KryptRoom state/evidence package. The chain publishes neither
collaborative data nor encrypted artifacts, secret shares, FHE ciphertexts,
OpenFHE keys, proof bytes, features, labels, model values, gradients, MSE, or
matched identifiers.

M7 does not prove correctness of PSI, SecretFlow/CHEETAH MPC, OpenFHE
arithmetic, neural training/evaluation, or the underlying private computation.
It does not establish participant identity or approval, malicious security,
compromised-host resistance, an exact wall-clock timestamp, local anti-rollback,
or production key custody. Hashes may expose low-entropy metadata to guessing.
SP1 validity, when referenced, remains a separate M5 verifier assertion.
