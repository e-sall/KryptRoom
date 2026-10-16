# Architectural decisions

## ADR-010 — Persistent private cohort analytics consumes S1 and produces S2

**Decision:** Extend the existing StatePolicy with opt-in operator/input permissions and StateTransition with optional canonical bindings. Preserve legacy encodings. Retain the already-authorized cardinality at S1 creation for empty-cohort preconditions. Reuse the existing ArtifactRefs, RoomState commitment, native SPU dump/load and AES-GCM share store; implement exactly COUNT, SUM, MEAN and CROSS_MEAN. A separate RevealService checks committed requests and policy before reconstruction.

**Reason:** M3 needs exact input lineage, a second persistent state and policy-controlled scalar outputs without extracting a plaintext join. Bind the exact input ciphertext descriptors and parent commitment, public spec, code/workflow hashes, context, policy, requested reveals and output descriptors. Zero cohorts reject means before division, without a new comparison circuit.

**Consequences:** Previously created states do not gain permission retroactively. Only new explicitly opted-in S1 fixtures can execute M3. The absolute fixed-point fixture tolerance is 0.001; hashes remain unsigned and fresh ciphertexts have different digests. The architecture still has no production KMS, key rotation, context migration or malicious-host protection. See [full design](PRIVATE_ANALYTICS.md).

**Status:** Implemented, pending cryptographic integration validation.

## ADR-001 — SecretFlow PSI for initial exact matching

**Decision:** Use the maintained SecretFlow standalone PSI library and its v2 API for the first exact two-party PSI capability. Prefer `PROTOCOL_RR22` after runtime verification.

**Reason:** SecretFlow provides a mature implementation, an official container, and a documented two-party RR22 configuration. This avoids custom cryptography and matches the approved project stack.

**Alternatives:** SecretFlow SPU's older `psi_csv` interface; another maintained PSI library; a custom protocol. The standalone v2 library has the clearest current RR22 path. Custom PSI is rejected.

**Status:** Superseded for M1 by ADR-006. Retained as historical rationale, not a description of the implemented backend.

## ADR-002 — Two isolated containers for Milestone 1

**Decision:** Represent Lab A and Lab B as separate Linux containers on a private Docker network. Mount only each participant's own input and output directories into its container.

**Reason:** This makes data ownership and mount boundaries inspectable, keeps the Control Plane out of the PSI data path, and runs the official SecretFlow binary without a Windows-native dependency.

**Alternatives:** Two processes in one Python runtime; Kubernetes; two physical hosts. Containers are the minimum reproducible local boundary, but they are not equivalent to physical host isolation.

**Status:** Superseded for M1, which uses two independent processes (ADR-006). The two-container boundary is implemented and runtime-verified for M2 (ADR-007).

## ADR-003 — No Control Plane data-plane component in Milestone 1

**Decision:** The Milestone 1 demo has no Control Plane process in the protocol path. Orchestration is limited to starting two independent participant processes and collecting exit status. M2 uses two containers.

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

**Status:** Accepted and runtime-verified on the synthetic two-container fixture.

## ADR-008 — Immutable RoomState is the persistent computation boundary

**Decision:** Represent persistent private-computation state with an immutable `RoomState`. Every state has a list-valued `parentStateIds`, `ArtifactRef` entries, a `StateTransition`, a default-deny `StatePolicy`, a `CryptoContext`, and a `StateCommitment`. State and artifact paths use create-exclusive semantics; an existing state ID is never replaced.

**Reason:** Independent jobs lose the privacy-preserving intermediate state needed by later collaboration steps. An explicit state contract allows a subsequent MPC computation to consume prior secret artifacts without reconstructing them, while recording parentage, policy, and cryptographic compatibility.

**Alternatives:** Store anonymous job outputs; rejected because policy, lineage, and crypto binding would be implicit. Store a plaintext joined table; rejected because it violates the product privacy boundary. Implement branch merging now; rejected as outside M2.5.

**Consequences:** Parent IDs are modeled as a list so future state graphs are representable, but M2.5 implements only creation of the parentless S1 state. Branch UI and merge semantics are not implemented. SHA-256 state commitments identify deterministic public state content but do not replace signatures or defend against a malicious node owner who can rewrite both a document and its unsigned commitment.

**Status:** Accepted and runtime-verified on the synthetic Linux restart/reload fixture.

## ADR-009 — Persist native SPU shares with node-local authenticated encryption

**Decision:** Persist the three M2 SPUObjects through SecretFlow's native `SPU.dump`/`SPU.load` interface. Encrypt each local serialized share with AES-256-GCM under a participant-local 256-bit key and a fresh 96-bit nonce. Bind room, state, artifact, participant, cipher, and crypto-context identifiers as authenticated data. Exchange only ciphertext hashes and sizes as explicitly authorized metadata.

**Reason:** SecretFlow already owns the version-specific SPU metadata and share serialization. Using its public persistence boundary avoids inventing a secret-sharing format. Authenticated encryption protects local shares at rest and detects wrong-key, wrong-context, or modified-ciphertext loads before MPC resumes.

**Alternatives:** Serialize SPU internals directly; rejected as brittle and unsafe. Install a new database or central object store; rejected because it expands scope and trust boundaries. Share one encryption key between participants; rejected because a KryptNode should not be able to decrypt the other node's persisted share. Persist plaintext share files; rejected because at-rest encryption is required.

**Consequences:** The current demo key is a permission-restricted local file inside each node's state root. Production KMS/HSM integration, key rotation, backup policy, rollback protection, and crash-atomic multi-party commit are deferred. AES-GCM protects encrypted artifact confidentiality and authenticity against storage readers without the key; it does not protect a compromised running host.

**Status:** Accepted and runtime-verified on the synthetic Linux restart/reload fixture.

