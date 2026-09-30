# Architecture

## Current implemented state

At repository bootstrap, KryptRoom contains architecture documentation and reserved monorepo boundaries. No Control Plane, KryptNode runtime, or cryptographic capability is considered implemented until executable code and test evidence are committed.

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

The current backend does not produce secret shares of matched rows. It therefore does not yet implement the private join/MPC handoff. A circuit-PSI or secret-shared PSI backend is required before that claim can be made.

The milestone does not yet implement node identity, transport authentication, signed manifests, output commitments, malicious-security enforcement, or RunReceipts. These omissions are security limitations, not implicit features.

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

## Non-goals for Milestone 1

The current milestone does not implement the web frontend, blockchain, MPC, ML, FHE, ZK, post-quantum identity, real medical data, or a production Control Plane.

