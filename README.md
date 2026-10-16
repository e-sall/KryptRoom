# KryptRoom

**Compute together. Reveal nothing.**

KryptRoom is a persistent encrypted state machine for collaboration between mutually distrustful organizations.

Organizations often need answers from combined data without being able to share the underlying records. KryptRoom explores how independent, organization-owned **KryptNodes** can match and join data privately, retain secret computation state, and authorize specific results. Persistent state is intended to let collaboration continue across computations and node restarts.

**Experimental research prototype.** Current protocols target two non-colluding, semi-honest participants on trusted hosts. There is no malicious-party or compromised-host protection, production KMS/HSM, key rotation, or production-grade distributed recovery/anti-rollback. The tagline expresses the privacy goal: authorized outputs such as cardinality are intentionally revealed. See the [threat model](THREAT_MODEL.md).

## What works today

- **M1 — verified two-party PSI cardinality.** Two independent processes use OpenMined PSI 2.0.6, ECDH, and the exact `Raw` container. Both peers disable matched-identifier revelation. The synthetic fixture returns intersection cardinality `2`; the [integration test](tests/integration/psi-cardinality.test.mjs) checks the result and output.
- **M2 — verified private join inside SecretFlow SPU.** Two isolated containers execute **CHEETAH / FM128**. The match mask and masked feature grids remain secret-shared, identifiers are excluded from the handoff, and a second MPC call reconstructs only cardinality. [Recorded successful Linux run](https://github.com/e-sall/KryptRoom/actions/runs/36731809790).
- **M2.5 — verified persistent encrypted RoomState.** Immutable `RoomState`, `ArtifactRef`, `StateTransition`, `StatePolicy`, `CryptoContext`, and `StateCommitment` contracts bind native SPU shares to their cryptographic context. Each KryptNode encrypts its local persisted shares with AES-256-GCM under a node-local key. In the [successful Linux CI run](https://github.com/e-sall/KryptRoom/actions/runs/38424886677), both nodes created S1, terminated, restarted without source CSV mounts, reloaded the encrypted secret state, and returned the authorized synthetic aggregate `68` through CHEETAH/FM128 without materializing a plaintext joined dataset.

These results establish behavior for the tested fixtures and stated threat model, not an independent security audit or a performance benchmark.

**M3 — verified Persistent Private Cohort Analytics.** M3 consumes S1's encrypted local SPU shares, executes COUNT, SUM, MEAN, or cross-party CROSS_MEAN, and persists secret scalar artifacts into a new S2. Computation and scalar disclosure have separate policy gates. The [successful Linux CI gate](https://github.com/e-sall/KryptRoom/actions/runs/38841137327) restarted twice, revealed only authorized `mean-a`, and rejected CROSS_MEAN before reconstruction; a separate explicitly authorized synthetic correctness case verified all six scalar outputs. See [the M3 design and validation guide](docs/PRIVATE_ANALYTICS.md).

**M4 — implemented, pending real CHEETAH/FM128 validation.** M4 adds a fixed direct-JAX Dense 1→2→1 square-activation network over S1, persists its four secret parameter tensors as S3, and evaluates the reloaded model with S1 through an exact two-parent transition into secret MSE state S4. No training value or model parameter is revealed. See [the bounded M4 design and validation gate](docs/PRIVATE_NN.md).

## Hero use case: cancer-research collaboration

Lab A holds genomic features; Lab B holds clinical treatment-response information for an overlapping population. Each lab wants to study the overlap without handing patient identifiers or raw records to the other lab or a central operator.

The repository uses only small synthetic fixtures. M1 privately counts the overlap. M2 independently compares identifiers inside MPC and creates a secret-shared join; M1 does not export hidden matches into M2. The persistence layer is intended to keep that join available for later authorized computations.

```text
Private Matching → Private Join → Persistent Encrypted State → Private Analytics → Private ML → Proof → Audit
M1 verified        M2 verified    M2.5 verified                  M3 verified        M4 pending   Future  Future
```

The M2.5 aggregate is a narrow continuity test, not the general M3 analytics API. M4 is limited to one deterministic synthetic training/evaluation fixture and is not yet runtime-validated. No real patient data, biomedical performance claim, FHE computation, ZK proof, or blockchain integration is included.

## Architecture

```mermaid
flowchart LR
  subgraph A[Lab A KryptNode]
    DA[Local raw data]
    RA[PSI peer / SPU party A]
    EA[Local encrypted share artifacts - M2.5 verified]
    DA --> RA
    RA --> EA
  end
  subgraph B[Lab B KryptNode]
    DB[Local raw data]
    RB[PSI peer / SPU party B]
    EB[Local encrypted share artifacts - M2.5 verified]
    DB --> RB
    RB --> EB
  end
  RA <-->|PSI or MPC / SPU protocol traffic| RB
  EA -. public artifact references .-> S[RoomState / StateTransition - M2.5 verified]
  EB -. public artifact references .-> S
  S -. metadata only .-> CP[Control Plane - planned, absent from demos]
```

Raw data is read locally by its owner. The M2 handoff stays secret-shared across both nodes; the M2.5 code additionally encrypts each persisted local share at rest. Public state metadata describes policy, parentage, crypto context, and ciphertext commitments. The Control Plane is a future metadata coordinator and receives no raw datasets in the current demos because it is absent from their data path.

The fixed-shape join takes O(n×m) work and targets small, public capacities. AES-GCM at-rest encryption is separate from MPC confidentiality. State commitments are unsigned SHA-256 hashes, not proofs or signatures. Details: [architecture](ARCHITECTURE.md), [decisions](docs/DECISIONS.md), [runtime notes](engines/mpc/README.md).

## Run the synthetic demos

Use Node.js 22 (the CI version) and npm for PSI and the local test suite:

```bash
npm ci --ignore-scripts
npm test
npm run demo:psi
```

The PSI package includes precompiled WebAssembly. `--ignore-scripts` avoids an unnecessary dependency installer; it does not replace the cryptographic runtime.

M2 requires Linux containers and Docker Compose:

```bash
docker compose -f compose.private-join.yml up --abort-on-container-failure
docker compose -f compose.private-join.yml down
```

SecretFlow 1.14.0b0 is pinned by immutable image digest. The reviewed runtime uses its no-Ray production scheduler with CHEETAH/FM128. Its Python environment remains inside the container.

To exercise the verified M2.5 acceptance path:

```bash
docker compose -f compose.persistent-state.yml -f compose.persistent-state.persist.yml up --abort-on-container-failure
docker compose -f compose.persistent-state.yml -f compose.persistent-state.persist.yml down
docker compose -f compose.persistent-state.yml up --abort-on-container-failure
docker compose -f compose.persistent-state.yml down
```

The expected post-restart aggregate is `68`. The second phase has no source CSV mounts. State lives under ignored `.runtime/persistent-state/`; existing S1 files cannot be overwritten through the storage API. Keep these files and their keys private. Losing a node's key/share makes this demo state unrecoverable; there is no automated recovery procedure.

## Security model

The protocols assume participants follow the reviewed code. Matched identifiers are disclosed to neither participant by the authorized interfaces; future identifier disclosure requires explicit opt-in. Cardinality and other explicitly authorized aggregates can still reveal information through small or repeated queries. Public capacities, tensor shapes, and protocol traffic also disclose metadata.

Peer authentication, malicious security, host compromise resistance, signed state commitments, production key custody, anti-rollback, and distributed recovery are not implemented. The demos have no production deployment approval or independent security audit and must not be used with real medical or regulated data. See [SECURITY.md](SECURITY.md) and [THREAT_MODEL.md](THREAT_MODEL.md).

## Roadmap and repository guide

M3's persistent analytics gate is verified on the synthetic fixture. M4 persistent private NN training/evaluation is implemented but remains pending its authoritative Linux gate. Later work remains unimplemented. See the [ordered roadmap](docs/ROADMAP.md) and [milestone checklist](TODO.md).

- `nodes/krypt-node/`: participant PSI processes and local input boundary.
- `engines/mpc/`: verified SPU join and persistent encrypted RoomState implementation.
- `packages/manifests/`: job, policy, and RoomState schemas.
- `demos/cancer-collaboration/`: synthetic fixtures and manifests.
- `tests/` and `.github/workflows/`: integration, privacy, and reproducibility checks.
- `services/`, `apps/`, `chain/`, and FHE/ZK engine directories: future component placeholders.

[Project context](PROJECT_CONTEXT.md) preserves technical direction. [CONTRIBUTING.md](CONTRIBUTING.md) describes the review and evidence expectations.

## License status

No project license has been selected. Public visibility does not by itself grant a general reuse license; dependency licenses remain their own. A license decision will be made explicitly before encouraging downstream adoption.

