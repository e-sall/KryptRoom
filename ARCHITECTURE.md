# Architecture

## Current implemented state

KryptRoom has runtime-verified M1 PSI cardinality and M2 two-container SPU private join paths. M2.5 adds an immutable persistent state layer and a two-phase create/terminate/restart/reload integration path. M2.5 is not considered runtime-verified until its Linux cryptographic CI gate passes.

## System boundary

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

Each organization controls its KryptNode and local storage. Cryptographic protocol traffic flows directly between participating nodes when the selected backend supports that topology. The Control Plane coordinates jobs through manifests and status metadata; it is outside the trust boundary for plaintext inputs.

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

- `apps/web`: future user interface; intentionally empty during PSI work.
- `services/control-api`: future metadata and room API.
- `services/orchestrator`: future Temporal workflows.
- `services/proof-service`: future proof lifecycle.
- `nodes/krypt-node`: participant runtime and local policy boundary.
- `engines/{psi,mpc,fhe,zk}`: backend-specific adapters and runtime material.
- `packages/manifests`: protocol and job manifests.
- `workflows`: composed private workflows.
- `chain`: future audit anchoring only.
- `demos/cancer-collaboration`: synthetic, non-medical demo data and run instructions.

## Non-goals for Milestone 2.5

The current milestone does not implement the M3 analytics surface, ML, FHE, ZK, blockchain, a frontend, branch/merge operations, dynamic membership, post-quantum identity, real medical data, production key management, or a production Control Plane.

