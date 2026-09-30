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

