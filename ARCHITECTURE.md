# Architecture

## Current implemented state

KryptRoom has a runtime-verified two-process PSI-cardinality path and an implemented two-container SPU private-join path awaiting Linux runtime evidence. No cryptographic capability is considered verified until its executable test evidence is recorded.

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

Lab A and Lab B run separate SecretFlow controllers and Ray clusters in isolated containers. Each container mounts the shared reviewed runtime and job manifest, but only its own local CSV. A local PYU parses and pads identifiers into a public fixed shape before the owner transfers the tensor into the two-party SPU as secret shares.

The SPU uses CHEETAH/FM128 to compare fixed-width identifier bytes, apply secret active-row masks, and produce a fixed-shape secret join grid. The handoff consists of a secret match mask plus masked Lab A and Lab B feature tensors; identifiers are excluded. A separate SPU call consumes the secret match mask and only its scalar cardinality is reconstructed. ML and private analytics are not part of this milestone.

The fixed-shape equality circuit is O(n*m) and is intentionally bounded to small datasets. It prevents match positions and compacted-row shapes from being released, but the configured capacity remains public. The current Docker transport is an unauthenticated local demo network, not a production deployment.

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

## Non-goals for Milestone 2

The current milestone does not implement private analytics, ML, the web frontend, blockchain, FHE, ZK, post-quantum identity, real medical data, or a production Control Plane.

