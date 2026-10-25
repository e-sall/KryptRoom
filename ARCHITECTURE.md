# Architecture

## Current implemented state

KryptRoom has runtime-verified M1 PSI cardinality, M2 two-container SPU private join, M2.5 persistent encrypted RoomState paths, M3 persistent private analytics, bounded M4 persistent private NN training/evaluation, the bounded M5 SP1 committed state-transition proof, and bounded M6 persistent OpenFHE BGV ciphertext addition. M7 public-chain anchoring is verified for one finalized Base Sepolia state-only inclusion and its authoritative public evidence package.

## Target system boundary

M8 PR1 adds a disconnected presentation layer in `apps/web`: Next.js App Router,
shared design tokens/components, responsive navigation and inspector infrastructure.
It neither reads node storage nor calls any core runtime. All business routes are
explicitly unavailable; example component states are isolated in `/design-system`.
No production Control Plane, authentication or API is implied. See
[`docs/m8/pr1/README.md`](docs/m8/pr1/README.md) for the frontend boundary and evidence.

PR2 extends presentation only. `/preview/rooms` owns a separate React context for
synthetic P03 Room summaries and P06 setup drafts. The provider survives preview
route changes, but has no browser storage, API adapter, server action or core
import. Production `/app` routes cannot read this provider or fixture collection.
The shared shell accepts optional page-header and inspector content; its original
defaults remain intact. The Room mini-history is an accessible, read-only P03
fixture diagram, not the PR3 graph editor and not canonical runtime lineage.
Readiness always denies execution. Local field validation is not authorization.
See `docs/m8/pr2/README.md` for exact scope, tests and backend gaps.

PR3 replaces only the preview Workspace placeholder with a read-only interactive
DAG. A safe presentation model, deterministic rank/lane layout, viewport/selection
state and inspector are separate modules. Parent arrays remain ordered and
multi-valued; edges never mutate source states. HTML controls overlay SVG paths.
P11 uses horizontal desktop/tablet layout and a vertical narrow-canvas layout.
No API DTO, hashing, artifact resolution or disclosure decision is implemented.
The future server adapter must provide authorized, field-filtered metadata.
Production Graph remains unavailable. See `docs/m8/pr3/README.md`.

PR4 adds presentation-only `features/operations`: shared operation vocabulary,
ordered input selection, a three-phase explanatory diagram and Readiness/Review
inspector; separate PSI/Join/Analytics result routes use fixed P08 display values.
Result context is derived from existing graph fixtures, not a second RoomState
catalog. Exact-state graph routes validate Room/state pairs against that catalog.
Workflow phases never create graph nodes or generate results. Selecting a sample
result does not disclose a private output. Run/approve/save/reveal/download remain
disabled; `/app/computations` and `/app/results` have no fixture fallback.
The preview has no I/O, storage, authentication or definitive API DTO. Desktop,
tablet and mobile reuse the existing shell/inspector/modal. See ADR-019 and
`docs/m8/pr4/README.md`; no M1–M7 or CI routing change.

PR5 adds presentation-only `features/provenance`: four P09 stages and the P10
hybrid timeline/graph, with contextual inspectors, progressive details and
Room/state-specific navigation. Both derive from PR3 rather than loading core
documents or historical transactions. Sample activity order is not execution
chronology. No StateProof/ChainAnchor serializer, verification or anchoring
adapter exists; all real actions remain unavailable. Structural validation,
document consistency, cryptographic verification and canonical finality are
explained separately and none is performed by this frontend. Production
Proofs/Activity remain disconnected. See ADR-020 and `docs/m8/pr5/README.md`.

The Control Plane and signed metadata in this target diagram are planned. Neither participates in the current demos; only participant runtimes and their local storage are implemented.

```text
Organization A                          Organization B
+----------------------+                +----------------------+
| KryptNode A          |<-- protocol -->| KryptNode B          |
| - local raw data     |                | - local raw data     |
| - participant keys   |                | - participant keys   |
| - crypto runtime     |                | - crypto runtime     |
+----------+-----------+                +-----------+----------+
           | signed metadata / authorized artifacts |
           +-------------------+---------------------+
                               v
                    +-----------------------+
                    | KryptRoom Control     |
                    | Plane                 |
                    | no raw participant    |
                    | data                  |
                    +-----------------------+
```

Each organization controls its KryptNode and local storage. Cryptographic protocol traffic flows directly between participating nodes when the selected backend supports that topology. The planned Control Plane will coordinate jobs through manifests and status metadata; it is outside the trust boundary for plaintext inputs.

## Milestone 1 design

Milestone 1 runs OpenMined PSI v2.0.6 between two separate KryptNode processes. Each process reads only its organization's local CSV. Lab A acts as the PSI server and Lab B as the client. The client sends ECDH-encrypted identifiers; the server responds with evaluated ciphertexts and an exact `Raw` encrypted server-set representation. The client computes only the intersection cardinality.

Both peers instantiate the library with identifier revelation disabled. The server never receives Lab B plaintext identifiers. Lab B receives the cardinality but no matched identifiers. No Control Plane service participates in the protocol or receives participant input.

The Milestone 1 backend does not produce secret shares of matched rows. Milestone 2 therefore re-evaluates identifier equality inside MPC rather than attempting to extract hidden matches from the PSI-cardinality protocol.

The milestone does not yet implement node identity, transport authentication, signed manifests, output commitments, malicious-security enforcement, or RunReceipts. These omissions are security limitations, not implicit features.

## Milestone 2 design

Lab A and Lab B run separate SecretFlow controllers using the pinned release's production no-Ray scheduler in isolated containers. Each container mounts the shared reviewed runtime and job manifest, but only its own local CSV. A local PYU parses and pads identifiers into a public fixed shape before the owner transfers the tensor into the two-party SPU as secret shares.

The SPU uses CHEETAH/FM128 to compare fixed-width identifier bytes, apply secret active-row masks, and produce a fixed-shape secret join grid. The handoff consists of a secret match mask plus masked Lab A and Lab B feature tensors; identifiers are excluded. A separate SPU call consumes the secret match mask and only its scalar cardinality is reconstructed. ML and private analytics are not part of this milestone.

The fixed-shape equality circuit is O(n*m) and is intentionally bounded to small datasets. It prevents match positions and compacted-row shapes from being released, but the configured capacity remains public. The current Docker transport is an unauthenticated local demo network, not a production deployment.

## Milestone 2.5 persistent state design

`RoomState` is the immutable public state descriptor. It contains list-valued parent state IDs, `ArtifactRef` entries, one `StateTransition`, one default-deny `StatePolicy`, the exact `CryptoContext`, and a SHA-256 `StateCommitment` over deterministic sorted-key JSON. The commitment is a content-integrity/provenance identifier, not a signature or malicious-host defense.

Each ArtifactRef represents one logical SPU value and contains only public shape/type information plus per-party ciphertext digests and local URIs. The M2 handoff is persisted as three artifacts: the match mask, masked Lab A feature grid, and masked Lab B feature grid. SecretFlow's native `SPU.dump` writes each runtime share through a KryptRoom AES-256-GCM writer; `SPU.load` later reads it through the matching authenticated decryptor. No custom secret-sharing format or plaintext join is introduced.

Every KryptNode creates and retains its own 256-bit state key. The encrypted envelope uses a fresh 96-bit nonce, and its authenticated data binds the room ID, state ID, artifact ID, participant, cipher, and crypto-context ID. State documents and artifact files are created exclusively, so an existing state ID cannot be overwritten. The two nodes hold identical public state documents but different keys and different local encrypted shares.

The acceptance topology has two separate phases. The create phase mounts each node's own source CSV and produces S1. Both containers are then removed. The analytics phase starts new containers with only node-local state directories mounted, verifies the state commitment and ciphertext digest, loads the encrypted shares back into CHEETAH/FM128, and reconstructs only the explicitly authorized synthetic aggregate. The aggregate is a narrow continuity test for M2.5, not the M3 analytics API.

## Repository boundaries

M3 adds persistent scalar analytics over S1 and an immutable child S2 using the same RoomState/share storage. Its contract and kernel are separate from the policy-controlled reveal service. Status: verified on the synthetic Linux CHEETAH/FM128 fixture, including two restarts. See [M3 architecture and evidence](docs/PRIVATE_ANALYTICS.md).

M4 is a sibling transition from S1, not a child of S2. Training produces immutable S3 with four encrypted local model-share artifacts. Evaluation consumes exact ordered parents `[S3_model, S1]`, persists only secret MSE in S4, and reuses the single RevealService reconstruction boundary. Status: verified on the bounded synthetic Linux CHEETAH/FM128 fixture. See [M4 design and evidence](docs/PRIVATE_NN.md).

## Milestone 6 FHE state transition

M6 is independent of the MPC lineage and the M5 proof relation. It
creates parentless `S5_fhe_inputs` from two participant-local four-integer
vectors encrypted under one OpenFHE BGV-RNS public key. Lab A owns the only
private key; Lab B and the evaluator receive public material only. The evaluator
reloads committed ciphertexts in a separate process, performs one `EvalAdd`
without a decryption API or private-key path, and persists `S6_fhe_sum`.

The existing RoomState model remains canonical. Optional FHE fields extend
`CryptoContext` with the exact OpenFHE version, scheme parameters, actual ring
dimension, key epoch/owner, and digest-bound public-material references. FHE
`ArtifactRef` entries explicitly use `protection: fhe_ciphertext`; their binary
size and SHA-256 digest bind the persisted OpenFHE representation. Legacy M1–M4
serialization is unchanged when these optional fields are absent.

The computation policy authorizes only `fhe_vector_add` over the two named input
artifacts and requests no reveals. A separate `FHERevealService` authorizes only
`fhe.vector-sum` to Lab A and Lab B before reading the private key. This is a
single-owner-key prototype, not threshold or multiparty FHE. See
[the complete M6 design](docs/FHE_STATE_TRANSITION.md).

Status: verified on the bounded synthetic Linux fixture in the
[authoritative OpenFHE run](https://github.com/e-sall/KryptRoom/actions/runs/39155437292),
including process restart/reload, real `EvalAdd`, immutable child persistence,
pre-decryption policy denial, authorized exact decryption, and ciphertext
tamper detection.

## Milestone 7 public-chain anchor

M7 observes an already immutable RoomState; it does not evolve, store, or
replace that state. The off-chain layer verifies existing RoomState metadata,
optionally commits the exact external M5 StateProof document, and computes one
domain-separated `AnchorCommitment`. The public contract is stateless and emits
only that bytes32 plus the ordinary Ethereum sender. No RoomState identifier,
policy, artifact descriptor, participant metadata, encrypted payload, key, or
proof bytes are transaction arguments or event data.

One immutable `ChainAnchor` records an exact inclusion and deployed runtime
code hash outside RoomState. A separate status observation tracks pending,
safe/confirmed, finalized, failed, or orphaned state. The verifier checks Base
Sepolia chain ID 84532, receipt/event/log identity, canonical block/hash,
runtime code, and ancestry from the RPC `safe`/`finalized` heads. Package
matching and optional M5 proof validation are separate layers. M6 S6 can be
anchored with NONE/ZERO32 using only its RoomState document after all FHE
material is unavailable.

The code is chain-agnostic at the commitment boundary; Base Sepolia is the V1
validation target. Status is **VERIFIED** for the sole canonical state-only
acceptance event, finalized in evidence-only run 39381943437 without a new
transaction.
See [the complete M7 design](docs/PUBLIC_CHAIN_ANCHOR.md).

- `apps/web`: future user interface; intentionally empty during PSI work.
- `services/control-api`: future metadata and room API.
- `services/orchestrator`: future Temporal workflows.
- `services/proof-service`: future proof lifecycle.
- `nodes/krypt-node`: participant runtime and local policy boundary.
- `engines/{psi,mpc,fhe,zk}`: backend-specific adapters and runtime material.
- `packages/manifests`: protocol and job manifests.
- `workflows`: composed private workflows.
- `chain`: M7 stateless Foundry contract and Base Sepolia deployment/recording helpers.
- `demos/cancer-collaboration`: synthetic, non-medical demo data and run instructions.

## Current non-goals

M5 adds external TransitionReceipt/StateProof for exact `[S3_model, S1]` evaluation
lineage, authorization and commitments. Status: **M5 VERIFIED** by real SP1 6.9.0
CPU Groth16 generation and independent verification in GitHub Actions. Full
policy/context/holder metadata stays in the private witness. S4 is unchanged.
SecretFlow/CHEETAH execution, MPC arithmetic and numeric MSE are not proved. See
docs/STATE_PROOF.md.

The current milestone does not implement general-purpose private ML, private inference APIs, model export, optimizer checkpoints, ML beyond the fixed M4 network, FHE beyond one four-element BGV `EvalAdd`, threshold/multiparty FHE, proofs beyond M5's bounded metadata relation, ZK proof of the FHE arithmetic, a blockchain state machine or on-chain computation/storage, a frontend, branch/merge operations, dynamic membership, post-quantum identity, real medical data, production key management, or a production Control Plane. M7 proves one finalized public inclusion and exact package match; it does not prove the underlying private computation.

