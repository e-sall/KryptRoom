# Architectural decisions

## ADR-021 — Marketing replay is a view over synthetic presentation states

**Decision:** Implement P01/P02 and P05 restored V1 in the existing marketing
routes. Preserve the desktop 231:493:248 column ratio across Explore and
Presentation, seven bounded scenes, initial scene 04 and canonical thin K.
Reuse the PR3 Supply Chain catalog and ordered S4 parents rather than introducing
another state model. Restart returns to scene 01 and Explore. Mode changes
preserve scene and selection; there is no autoplay or hidden execution.

**Reason:** Marketing must explain persistent private collaboration without
impersonating its operational backend. The recovered original DIL identifies
restored V1; the portable conversion is supporting geometry evidence, not a
certified interactive original. The founder's current logo correction and the
existing P11 canonical component supersede the recovered older mark.

**Consequences:** Semantic buttons, keyboard navigation, responsive reflow,
progressive explanations and exact-state preview links adapt the source to the
application. Future diagram stages are hidden rather than made illegible by
low opacity. P02 uses the four labels explicitly requested in the PR6 mission
and retains the layered/network motif; scroll/pointer behavior is a documented
engineering adaptation, not recovered interaction evidence. Booking remains
unavailable without a real provider. No API, verifier, runtime, storage,
permission grant or disclosure is introduced. M8-SEC-001 stays open with its
original before-PR7 / 2026-11-21 earliest deadline. See `docs/m8/pr6/README.md`.

## ADR-020 — Provenance presentation never establishes proof or chain authority

**Decision:** Add P09 V3 / P10 V1 only to Room-scoped synthetic preview routes.
Derive all state references and ordered relationships from the unchanged PR3
catalog. Local stage, evidence, conceptual-check, event and filter selection
affects presentation only. Exact-state routes validate Room/state pairs; links
and the shared shell retain selected state context where it exists.

**Reason:** Inspection of RoomState, StateProof, ChainAnchor and the actual
M5/M7 verifiers establishes data contracts, not a Workspace API. Control API,
orchestrator and proof service are placeholders. No authenticated metadata,
verification, activity or anchoring adapter exists.

**Consequences:** Evidence availability is not a verdict. Structural validation
is distinct from M7 Layer A (chain inclusion and canonical finality), Layer B
(document/commitment consistency) and explicit separate M5 Layer C verification.
A consistent StateProofDocumentCommitment does not establish Groth16 validity.
No verifier, hashing, artifact reading, RPC, transaction, browser business
storage or permissions are introduced. Verify/anchor/approve/download remain
disabled. No fixture is regenerated and no historical acceptance evidence is
attached to a synthetic RoomState.

P10 sample sequence numbers replace fictitious audit times; event wording is
conceptual, not a claim of a completed run, approval, denial or invitation.
P09/P10 older S2/S3 labels are reconciled with PR3, not copied into a competing
catalog. Responsive HTML controls and decorative SVG relationships preserve
keyboard access and the existing P11 shell. Converted source captures are
distinct from application evidence; no pixel-perfect claim. M8-SEC-001 and its
before-PR7 / 2026-11-21 earliest deadline remain unchanged.
See `docs/m8/pr5/README.md` for traceability and validation.

## ADR-019 — Explanatory workflows and fixed results are not computation authority

**Decision:** Implement P07/P08 in isolated Room-scoped preview routes. Reuse the
PR3 readonly state catalog and ordered parents; keep local phase/input choices
separate from the fixed P08 values. Never insert a hypothetical node into the
graph. Exact-state links select an existing validated Room/state pair. Shared
presentation vocabulary is not an operation API or policy contract.

**Reason:** The Workspace services remain placeholders. A complete checklist,
animation, result page or state link must not imply actual computation, storage,
approval or disclosure. M1–M7 capabilities do not establish frontend authority.

**Consequences:** PSI cardinality and four aggregate values are fixed synthetic
design fixtures. Join has no rows or matched identifiers. Actions remain disabled,
proof is Not assessed, commitments and chain status are unavailable. No network,
browser storage, key access or private runtime import. P08 historical state labels
are reconciled explicitly with PR3 rather than silently replacing its states.
Production Computations/Results stay unavailable. HTML controls and finite motion
provide accessible desktop/tablet/mobile navigation without a second design system.
No new dependency, CI exception, crypto validation or M1–M7 change.
Evidence and limitations: `docs/m8/pr4/README.md`.

## ADR-018 — Read-only synthetic graph presentation, separate from core authority

**Decision:** Implement PR3 as an isolated preview DAG with a readonly display
projection, deterministic topological/rank layout, HTML node buttons, SVG directed
edges and local viewport/selection state. Preserve ordered multiple parents.
Use existing shell/modal controls for desktop, tablet and mobile inspection.
Do not introduce React Flow for this bounded read-only surface or invent a
Workspace API. No raw RoomState serialization is passed into browser fixtures.

**Reason:** RoomState is immutable, while server authorization and production
Workspace services are still absent. Display navigation must not imply state
creation, secret access or proof verification.

**Consequences:** Preview interactions are real frontend behavior over labelled
synthetic data, not backend integration. Production Graph stays unavailable.
Layout performance is bounded by the tested 24-node example; advanced layout,
virtualization, edit operations and server adapters require separate review.
No dependency, CI exception or M1–M7 change. P09/P10 remain future work.
Evidence and visual adaptations: `docs/m8/pr3/README.md`.

## PR #15 maintenance decision — exact synthetic M5/M7 CI migration

Owner-approved CI trigger changes alter the workflowHash bound into synthetic
M5 metadata. Regenerate only the authorized six M5 and two dependent M7 vectors
with unchanged original generators. Pin exact old/new file bytes in CI routing,
check transitive M5 inputs, preserve all core/mixed/manual behavior and keep both
reproducibility jobs active. Never exempt the fixture directories generally.

M7's representative descriptor retains fixed proof fields but its updated
commitments have no new Groth16 coverage. This is Layer B consistency only;
historical Layer C proofs and finalized on-chain acceptance remain immutable.
No new architecture, crypto implementation or live acceptance is introduced.
Evidence: `docs/m8/pr2/M5-FIXTURE-MIGRATION.md` and
`docs/m8/pr2/M7-FIXTURE-MIGRATION.md`. PR remains subject to human review.

## ADR-017 — Isolate PR2 synthetic Rooms and ephemeral Easy Setup

**Decision:** Keep `/app/rooms` explicitly disconnected. Put P03/P06 interactive
examples under `/preview/rooms` with conspicuous synthetic labels, noindex metadata
and a layout-owned React provider. Use presentation-only types, not speculative
backend DTOs. Persist only across preview route transitions in React memory;
reload clears the draft. No application storage, network, server action or core
runtime import. Creation, invitations, connections, policy writes and execution
remain disabled even for valid example fields.

**Reason:** At verified dev `acf5f262b03d6c0db3ff36b413f330b61f1181d2`, the
Control API/orchestrator/proof service directories contain placeholders only.
Implementing a fake API or browser-backed Room store would misrepresent authority.

**Consequences:** P03 discovery/navigation and P06 progressive forms are testable,
but no real collaboration can be created. The original P03 synthetic topology is
labelled illustrative and is not an M1–M7 runtime contract. Readiness has no allow
path. A future separately reviewed service must supply scoped metadata and exact
authorization decisions; do not adapt these fixtures into production responses.
Reuse PR1 primitives and shell slots, keeping the canonical K and tokens unchanged.
The optional header slot preserves P03's full-width heading/filter composition.

**Validation:** See `docs/m8/pr2/README.md`; targeted unit/browser tests and
source-boundary guards. Human design/security review and final CI remain merge
gates. M8-SEC-001 expiry is unchanged. No merge is authorized by this ADR.

## ADR-016 — Isolate the M8 presentation foundation from the frozen core

**Decision:** Implement PR1 in `apps/web` using pinned Next.js App Router, React,
TypeScript and Tailwind with its own lockfile. Render static public presentation
and explicitly unavailable business modules. Keep local component specimens on
a separate route. Use semantic HTML and a native dialog with explicit keyboard
wrapping; preserve the recovered palette and P11 layout principles. Final PR #14
review supersedes the initial P04 K with the later thin P11 mark, consistent with
corrected P05/P06. `KLogo` and semantic logo colors are the single production source.

**Reason:** The audited web directory contained only `.gitkeep`; there is no
production workspace API or Control Plane. A closed route catalog and component
boundaries support the later six PRs without inventing auth, data or crypto services.

**Alternatives:** Root npm workspace migration, a generated component template,
React Flow before graph implementation, or a fake API were rejected as unnecessary
scope or misleading capability. Shared fonts use the prototype's Arial/Georgia/
monospace families with local fallbacks, not external font requests.

**Consequences:** No API/schema integration, real rooms, uploads, computations,
proofs, verification badges or chain actions. More mobile navigation substitutes
for the prototype Results shortcut until room-scoped routing exists. Pixel-exact
parity is not asserted for a disconnected HTML shell versus synthetic SVG data.
P04/P11 portable conversions fail in-browser; original source and explicit visual
limitations are recorded in `docs/m8/pr1/README.md`. PR1 is reviewable independently;
production auth, CSP, service contracts and full cross-browser/WCAG audit remain later gates.

**Status:** Implemented and locally tested; maintainer/design review and PR CI required.

**PR #14 final follow-up:** No compatible published fix was found for the
development-only braces advisory / ESLint 9 EOL combination. The requested
temporary exception M8-SEC-001 (`docs/m8/pr1/SECURITY-EXCEPTION.md`) records
reachability, compensating controls and owner. It expires before PR7 starts or
2026-11-21, whichever comes first; maintainer merge approval must include it.

## ADR-015 — Fail-closed M7 deployment and anchor recovery

**Decision:** Treat Base Sepolia contract
`0xd090b5f1834d41c1db39cfbb642edb3acbbce96b`, created by transaction
`0x86fa94f71d74ee43bb87ca2c0b31b0f0f69938936dc3d9c71bf56bda4f706f9a`,
as the authoritative M7 V1 deployment. The live workflow has explicit
`deploy`, `resume_existing_deployment`, and `resume_existing_anchor` modes. Deployment resume requires normalized
immutable identifiers and never invokes `forge create`. Deploy requires the
expected sender nonce and passes that nonce to `forge create`, so retrying the
same failed deployment attempt cannot silently create another contract.

**Reason:** Live run 39377159223 deployed successfully, then its Python RPC
client received HTTP 403 before it could build the manifest or publish an
anchor. Ephemeral runner files could not prevent a duplicate deployment. The
RPC client now sends the stable `KryptRoom-M7/1` User-Agent, and recovery
validates the transaction, receipt, canonical block, exact pinned runtime, and
absence of the deterministic acceptance anchor before any anchor transaction.

**Consequences:** The stateless permissionless contract and commitment
semantics remain unchanged. The official workflow serializes attempts and
checks the exact commitment in bounded log ranges, but it cannot stop an
unrelated external account from publishing the same permissionless event. If a
run fails after publishing an anchor, an ordinary retry fails closed instead of
emitting a duplicate. Evidence-only recovery requires the exact existing anchor
transaction and log index, never broadcasts, and requires exactly one canonical
matching event. Receipt recording polls boundedly until the receipt block hash
matches the canonical block view; disappearance, incompatible receipt movement,
or timeout fails with an explicit pending/orphaned classification.

**Status:** Accepted. The existing deployment passed read-only Base Sepolia
validation with runtime hash
`0xd0ceef826a9258089d4d2dcdc0171aefe288ef987d92a5954bb6579de1370755`.
Run 39379898215 sent the exact state-only acceptance anchor in transaction
`0x983e17727bd1aac518bc38b1889a9b27c16e840fa0d393f6e573a8a6959dce50`.
Read-only forensics found exactly one canonical matching event at log index 282.
Evidence-only run 39381943437 reused it without broadcasting, reached Base
`finalized`, passed standalone Layers A/B, and uploaded the authoritative public
package.

## ADR-014 — Stateless event-only Base anchor with separate verification layers

**Decision:** Implement M7 as a chain-agnostic commitment protocol with one
Base Sepolia V1 deployment. Publish only a domain-separated `bytes32`
AnchorCommitment through a stateless, permissionless event-only contract. Keep
the immutable inclusion record outside RoomState and maintain finality/reorg
status separately. Verification has three explicit layers: public-chain
inclusion, exact state/evidence package matching, and optional existing M5 SP1
proof verification.

**Reason:** A minimal event provides durable public inclusion evidence without
turning public consensus into KryptRoom's state machine or publishing private
collaboration metadata. Separating package hashing from proof verification
prevents a StateProof document commitment from being misrepresented as SP1
validity. Base `safe`/`finalized` heads provide canonical OP Stack finality
semantics without inventing a fixed confirmation rule.

**Alternatives:** On-chain RoomState fields, a registry mapping, ownership,
upgradeability, tokens/payments, and computation were rejected as unnecessary
disclosure and authority. A fixed confirmation count was rejected. Embedding
ChainAnchor/status in RoomState was rejected because chain inclusion and reorg
observations must not mutate immutable private-computation state.

**Consequences:** Anyone may submit or duplicate a commitment; the sender does
not represent a participant or approval. A reorg creates an orphaned status,
not a mutated record. M6 state-only packages use NONE/ZERO32 without reading
FHE material. M5 proof validity remains a separate command. Status is
**VERIFIED** for the bounded state-only acceptance: the V1 deployment and sole
canonical event are finalized, the standalone verifier passed, and the public
artifact package was produced. M7 still does not prove the underlying private
computation.

See [M7 protocol, vectors, evidence, and limits](PUBLIC_CHAIN_ANCHOR.md).

## ADR-013 — Single-owner BGV ciphertext addition as the first FHE transition

**Decision:** Implement M6 as exact element-wise addition of two fixed
four-integer ciphertext vectors with the official OpenFHE Python 1.5.1.0.24.4
Ubuntu 24.04 wheel. Use BGV-RNS, plaintext modulus 65537, multiplicative depth
zero, batch size four, OpenFHE-selected `HEStd_128_classic` parameters, and
binary serialization. Persist input state `S5_fhe_inputs` and child state
`S6_fhe_sum`. Lab A is the sole private-key owner; the evaluator receives only
digest-bound public context material and ciphertexts. Computation and final
decryption use separate StatePolicy authorizations.

**Reason:** Ciphertext addition validates persistence, restart/reload,
CryptoContext binding, immutable lineage, policy separation, and a genuinely
secret-key-free FHE computation without adding multiplication keys, approximate
CKKS semantics, a generic analytics surface, or fake threshold cryptography.

**Alternatives:** CKKS was rejected because the chosen operation is exact
integer arithmetic. Decrypt-compute-reencrypt and ordinary at-rest encryption
were rejected because neither is FHE. Threshold OpenFHE was deferred because it
would materially expand the key protocol and is not required to validate the
state-machine boundary. A general operator framework was rejected as premature.

**Consequences:** Lab A can decrypt any ciphertext under its key outside the
reviewed interface, so this does not enforce policy against a malicious key
owner. The fixed vector length, key epoch, scheme, exact parameters, public
material hashes, artifact hashes, code/workflow hashes, and output transition
are committed. There is no multiplication, arbitrary program, threshold key,
production KMS, input signature, side-channel defense, or ZK proof of EvalAdd.

**Status:** Accepted, implemented, and runtime-verified on the bounded synthetic
Linux OpenFHE fixture; see [M6 evidence](FHE_STATE_TRANSITION.md).

## ADR-012 — Bounded M5 committed evaluation proof

Use SP1 6.9.0 CPU Groth16 for exactly one M4 evaluation metadata relation.
Preserve M1–M4 state formats and json-sort-keys-v1 hashes. Hash historical S3
content as exact Python bytes; recompute only float-free evaluation semantics.
Keep full policy/context/holder metadata private; expose a domain-separated
64-byte public claim. External StateProof avoids circular S4 commitments.
Derive verifier identity from its embedded ELF. Metadata fixtures use synthetic
ciphertext descriptors; M4's independent regression tests actual MPC execution.
Do not claim computation correctness or participant approval. Signatures remain
deferred to M5.1. Status and limits: STATE_PROOF.md.

**Validation status:** M5 VERIFIED. After two preserved hosted-runner shutdowns,
the unchanged gate passed on a temporary repository-scoped, unique-label,
ephemeral WSL2 runner: real SP1 6.9.0 CPU Groth16 generation, persisted public
proof bundle, standalone verification, negatives and leakage checks. The runner
was one-job only and deregistered automatically. Keep the real CPU
proof/standalone-verification gate unchanged; do not substitute mock, network
proving, execution-only success or weaker claims. `KRYPTROOM_M5_RUNNER` names
optional pre-provisioned infrastructure; it changes no proof semantics. See
[measurements](M5_VALIDATION.md).

## ADR-011 — Persistent private NN model and exact multi-parent evaluation

**Decision:** Train one fixed direct-JAX Dense 1→2, square, Dense 2→1 network directly from S1 under CHEETAH/FM128. Use public deterministic SHA-256 initialization, four full-batch gradient-descent steps, and secret masked MSE. Persist only four final secret parameter tensors in S3. After runtime destruction, evaluate by loading exact parents `[S3_model, S1]`, persist only secret MSE in S4, and reuse RevealService for the sole `model.evaluation.mse` disclosure.

**Reason:** M4 must prove persistent collaborative secret data can evolve into a persistent secret model and participate in a later computation without plaintext recovery. Exact parent, input, model, training/evaluation, initializer, code, workflow, context, policy, reveal, and output descriptor bindings preserve the existing immutable RoomState architecture.

**Consequences:** S2 is not a parent. S1 data is not copied into S3. Legacy and M3-only S1 states receive no M4 permission. The model, optimizer, fixture, normalization, and MSE bound are fixed; this is not general private ML or a biomedical claim. Existing semi-honest/trusted-host/key-management limitations remain.

**Status:** Accepted and runtime-verified on the bounded synthetic Linux fixture; [CI evidence](https://github.com/e-sall/KryptRoom/actions/runs/38846097654). See [M4 design](PRIVATE_NN.md).

## ADR-010 — Persistent private cohort analytics consumes S1 and produces S2

**Decision:** Extend the existing StatePolicy with opt-in operator/input permissions and StateTransition with optional canonical bindings. Preserve legacy encodings. Retain the already-authorized cardinality at S1 creation for empty-cohort preconditions. Reuse the existing ArtifactRefs, RoomState commitment, native SPU dump/load and AES-GCM share store; implement exactly COUNT, SUM, MEAN and CROSS_MEAN. A separate RevealService checks committed requests and policy before reconstruction.

**Reason:** M3 needs exact input lineage, a second persistent state and policy-controlled scalar outputs without extracting a plaintext join. Bind the exact input ciphertext descriptors and parent commitment, public spec, code/workflow hashes, context, policy, requested reveals and output descriptors. Zero cohorts reject means before division, without a new comparison circuit.

**Consequences:** Previously created states do not gain permission retroactively. Only new explicitly opted-in S1 fixtures can execute M3. The absolute fixed-point fixture tolerance is 0.001; hashes remain unsigned and fresh ciphertexts have different digests. The architecture still has no production KMS, key rotation, context migration or malicious-host protection. See [full design](PRIVATE_ANALYTICS.md).

**Status:** Accepted and runtime-verified on the synthetic two-restart Linux fixture; [CI evidence](https://github.com/e-sall/KryptRoom/actions/runs/38841137327).

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

