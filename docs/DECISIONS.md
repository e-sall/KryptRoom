# Architectural decisions

## ADR-001 — SecretFlow PSI for initial exact matching

**Decision:** Use the maintained SecretFlow standalone PSI library and its v2 API for the first exact two-party PSI capability. Prefer `PROTOCOL_RR22` after runtime verification.

**Reason:** SecretFlow provides a mature implementation, an official container, and a documented two-party RR22 configuration. This avoids custom cryptography and matches the approved project stack.

**Alternatives:** SecretFlow SPU's older `psi_csv` interface; another maintained PSI library; a custom protocol. The standalone v2 library has the clearest current RR22 path. Custom PSI is rejected.

**Status:** Accepted; execution evidence pending.

## ADR-002 — Two isolated containers for Milestone 1

**Decision:** Represent Lab A and Lab B as separate Linux containers on a private Docker network. Mount only each participant's own input and output directories into its container.

**Reason:** This makes data ownership and mount boundaries inspectable, keeps the Control Plane out of the PSI data path, and runs the official SecretFlow binary without a Windows-native dependency.

**Alternatives:** Two processes in one Python runtime; Kubernetes; two physical hosts. Containers are the minimum reproducible local boundary, but they are not equivalent to physical host isolation.

**Status:** Accepted; runtime validation pending.

## ADR-003 — No Control Plane data-plane component in Milestone 1

**Decision:** The Milestone 1 demo has no Control Plane process in the protocol path. Orchestration is limited to starting the two participant containers and collecting exit status.

**Reason:** A premature service adds unnecessary exposure. The milestone can prove the fundamental PSI capability while making the zero-raw-ID Control Plane property structurally obvious.

**Alternatives:** A central service that receives hashes or plaintext inputs. Rejected because it would violate the architecture or create misleading privacy claims.

**Status:** Accepted.

## ADR-004 — Security claims require executed evidence

**Decision:** Source code and configuration alone do not qualify a cryptographic milestone as complete. Documentation must distinguish designed, implemented, and executed/tested states.

**Reason:** Cryptographic integrations often fail because of version, protocol, topology, or runtime differences. Truthful claims require runtime evidence.

**Alternatives:** Treat configuration review as sufficient. Rejected.

**Status:** Accepted.

## ADR-005 — Default output is cardinality only

**Decision:** Reveal matched identifiers to neither participant. The authorized Milestone 1 output is only the exact intersection cardinality. Any future identifier disclosure requires explicit opt-in authorization naming the recipients.

**Reason:** Matching patient identifiers are sensitive linkage information. Private join and MPC should consume alignment internally rather than disclose it to collaborators.

**Alternatives:** Reveal to both parties, or select a single receiver. Both are rejected as defaults.

**Status:** Accepted.

## ADR-006 — OpenMined PSI-CA replaces RR22 for Milestone 1

**Decision:** Use OpenMined PSI v2.0.6 with ECDH commutative encryption, `revealIntersection=false`, and its exact `Raw` container for Milestone 1.

**Reason:** SecretFlow PSI v2 RR22 always assigns a receiver that obtains the exact intersection. Its `broadcast_result` flag controls only whether senders also receive it. OpenMined's cardinality mode reveals the exact count without exposing matched identifiers, and `Raw` avoids probabilistic false positives.

**Alternatives:** SecretFlow RR22 with a hidden output file; rejected because a participant controlling the receiver node can inspect it. GCS or Bloom-filter cardinality; rejected for this small correctness fixture because they are probabilistic. Custom circuit PSI; rejected because KryptRoom does not invent cryptographic protocols.

**Consequences:** The backend does not create secret-shared matched rows. Private join/MPC handoff remains a separate gate requiring a mature circuit-PSI or secret-shared PSI implementation. The current security model remains honest-but-curious.

**Status:** Accepted and runtime-verified on the synthetic Milestone 1 fixture.

## ADR-007 — Fixed-shape private join inside two-party SPU

**Decision:** Recompute identifier equality inside SecretFlow SPU and keep the match mask and masked feature grids as fixed-shape secret SPU objects. Reconstruct only the intersection cardinality. Use CHEETAH with FM128 for the two-party runtime.

**Reason:** SecretFlow's receiver-oriented PSI interfaces materialize matched rows at a participant, which violates ADR-005. A fixed-shape MPC circuit can transfer each owner's input directly from PYU to secret shares, compare exact fixed-width identifier bytes, exclude identifiers from the handoff, and feed secret outputs into subsequent MPC calls. CHEETAH provides a two-party semi-honest backend without adding a preprocessing trust party.

**Alternatives:** Use `psi_df`/`psi_csv` and hide the result path; rejected because a participant controls the receiver host. Use SEMI2K's default trusted-first-party Beaver provider; rejected because it weakens the two-party privacy model and is documented as unsafe/debug-only. Add a trusted-third-party Beaver service; deferred because it expands the trust model. Implement a custom PSI protocol; rejected. Compact the joined rows; rejected because compaction reveals match positions or secret-dependent shapes.

**Consequences:** The join is exact for accepted identifiers and has O(n*m) work, so it is bounded to small public capacities. The configured capacity and tensor shapes are public. SecretFlow 1.14.0b0 supports Python 3.10/3.11 rather than Python 3.12, so this engine is isolated in its pinned official Linux image even though the future application backend targets Python 3.12. The beta runtime remains non-production until further review.

**Status:** Accepted and implemented; Linux two-container runtime verification pending.

