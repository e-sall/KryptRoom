# KRYPTROOM M8 — PR5 IMPLEMENTATION REPORT

## Scope and base

Base: verified merged PR #17, `origin/dev`
`60ede3fcc13d6cc7c008ed425e751894d625342f`.
Branch: `feat/m8-proofs-provenance-activity`. Delivery: open PR to dev, never
automatic merge. Main and PR6/PR7 are outside scope.

P09 V3 and P10 V1 are **synthetic frontend previews**, not operational services.
No proof or chain validation is claimed by this work.

## Audit and backend truth

Read the repository instructions, project/architecture/security/threat model,
ADRs (including M5/M7, frontend boundaries and exact PR2 fixture migrations),
original final P09/P10 and P04/P08/P11, Design System, Engineering Contracts and
Design Traceability. Inspected existing PR1–PR4 navigation, safe presentation
types, graph fixtures and tests.

Core read-only audit:

- `engines/mpc/room_state.py`: immutable RoomState with ordered parents,
  transition, artifact/context binding and commitment; not a frontend DTO.
- `packages/manifests/state-proof.schema.json` and M5 host verification:
  descriptors alone are insufficient; the actual verifier binds program,
  serialization, public values and real proof bytes. **Not invoked.**
- `packages/manifests/chain-anchor.schema.json`,
  `engines/chain_anchor/model.py`, `verifier.py`, `verify_anchor.py`:
  immutable inclusion identity, separate dynamic status, Layers A/B/C.
- `services/control-api`, `orchestrator`, `proof-service`: placeholders,
  not authenticated Workspace endpoints. Production `/app/proofs` and
  `/app/activity` stay unavailable, without preview fallback.

Layer A means actual chain inclusion/canonical finality, **not** structural
validation. Layer B means exact document/commitment consistency. Layer C means
separate explicit M5 cryptographic verification. None is executed here.
A coherent StateProofDocumentCommitment, receipt or fixture does not imply a
valid Groth16 proof. Historical M5 proofs, PR2 synthetic M5/M7 vector migrations,
Base Sepolia deployment and the historic finalized anchor remain untouched and
are never assigned to preview states.

## Implemented interactions and journey

- P09 four selectable stages, previous/next boundaries, S1–S4 picker and
  state-specific context. Lineage uses exact ordered incoming edges, clickable
  parents/children and selected-edge highlighting. Evidence distinguishes
  commitment, metadata, cryptographic artifact and receipt; selection changes
  the inspector. Three selectable check concepts distinguish structural,
  documentary and cryptographic assessment; all remain Not assessed.
  Anchoring separates preparation, publication, canonical inclusion and finality.
- P10 List is default; Graph uses the same immutable Room topology. Type and
  state filters intersect, selection survives List/Graph changes, filtered-out
  selection is replaced by the first matching example, and no match clears
  the inspector. Previous/next respects filtered bounds. Overview/Context/
  Diagnostic tabs and progressive details explain exactly what is unavailable.
- Room-scoped routes include optional existing state IDs. Invalid Room/state
  pairs are rejected. Graph, Results, Proofs and Activity link to the exact
  selected state; shell navigation preserves it when available. The PR3 stress
  graph is not linked to nonexistent provenance states.
- Rooms → Graph → Computations → Results → Proofs → Activity remains connected.
  Research stays empty; Insights keeps its existing two states. No new
  RoomState catalog, state mutation or transition ID is invented.
- Empty/Loading/Blocked/Error/Unavailable demonstrations clear stale inspector
  data and explicitly remain display examples, not backend responses.

Only Sample / Illustrative / Conceptual / Not assessed / Unavailable are used
for provenance and activity. No success, pending or finalized state is inferred.
No actor or audit timestamp is fabricated. Seven Supply Chain examples derive
from PR3 states plus conceptual access/security boundaries; their sequence is
presentation order, not execution history. Verify, anchor, approve and download
controls are disabled with an authorized-service explanation.

## Original references, conversions and application captures

Original archive: `KryptRoom-M8-Source-Consolidation`, supplied by the user.
The original text and portable JSX remain unchanged outside this repository.
SHA-256 provenance:

- Original P09 `chat-message-1.txt`:
  `1e99df1b9293e9f65953fb26fe12cc22af80890d549410bbb9441e43bb848a8a`.
- Original P10 `chat-message-1.txt`:
  `4f6f4f55bdb16e8d1dff7afa7059d557ad13fca90e0150463e2a13bc8e98d5b3`.
- Converted P09 JSX:
  `60f913c7c15c564132aeeb1088dced4be300c50006ce303059c2569c9562ffa7`.
- Converted P10 JSX:
  `c19bbfeb589696262fd8152e30b1e8c423e90c0b160c1eacb19bfecc25295391`.

`converted-p09-*.png` and `converted-p10-*.png` are static React renderings of
the recovered prototype geometry at 1440px, NOT running application evidence.
Only initial presentation state is varied during conversion; no original source
is rewritten. `app-*.png` are real production Next.js/Chromium captures.

Intentional HTML/React adaptations, not a pixel-perfect claim:

- Retain the approved thin K, warm palette, editorial titles, blue selection,
  understated panels, four-step rail and existing P11 shell. Stage rail becomes
  a two-column control group on mobile; inspector moves below at tablet and to
  the existing focus-trapped bottom sheet on mobile.
- Preserve one catalog: original P09/P10 S2 PSI / S3 Private Join become existing
  PR3 S2 Private Join / S3 Analytics. S4 retains ordered S2, S3 parents. No
  historical core state is imported. Room names use the established Room catalog.
- Use semantic buttons/ordered lists with decorative SVG edges instead of
  SVG text hit targets. Lineage is vertically ranked to keep complete titles
  and ordered relationships readable in the existing shell and at 320px.
- Verification's three boxes explicitly expose the required structural,
  Layer B and Layer C distinctions, with a separate no-verdict panel.
  They explain checks rather than animate an executed verifier.
- Evidence category selection and anchoring's four conceptual steps expose
  distinctions required by the brief, without guessed digests or transactions.
- P10 replaces prototype fake times and Recorded/Pending/Blocked outcomes with
  sample sequence numbers and conceptual wording. It retains list/graph,
  filters, selection, editorial hierarchy and the three inspector tabs.
- Full-page mobile screenshots include the fixed bottom navigation at the
  viewport position; this is screenshot stitching, not a second in-flow bar.
  Open bottom sheets are captured at viewport size, without stitching.

Traceability (KR-DES / KR-INT / KR-ACC): 032 → four separate scenes; 033 → state/stage/evidence
inspector; 034 → no inferred verification; 035 → no submitted/finalized claim;
036 → default List and Graph; 037 → filters/event selection; 038 → inspector
tabs; 039–043 → responsive/keyboard/system-state checks within PR5 scope,
not PR7 certification.

## Validation and limitations

Commands in `apps/web`: `npm run lint`, `npm run typecheck`,
`npm run build`, `npm test`, `npm run test:e2e`.
Final local results (2026-10-24): lint PASS; typecheck PASS; production build
PASS (68 static pages); **79 unit/component tests PASS**; full Chromium suite
**73 PASS, 2 inherited non-mobile sheet skips** (75 total). All 18 PR5 browser
cases pass; rerun after the viewport-only sheet capture adjustment also passes.
The unchanged read-only CI scope suite passes **31 tests**, including exact
historical migration and negative core-classification cases, without regeneration.

### Screenshot inventory

44 captures: six converted references and 38 real application captures.

- Converted P09: [Lineage](converted-p09-lineage.png), [Evidence](converted-p09-evidence.png),
  [Verification](converted-p09-verification.png), [Anchoring](converted-p09-anchoring.png).
- Converted P10: [List](converted-p10-list.png), [Graph](converted-p10-graph.png).
- P09 desktop: [Lineage](app-proof-lineage-desktop.png), [Evidence](app-proof-evidence-desktop.png),
  [Verification](app-proof-verification-desktop.png), [Anchoring](app-proof-anchoring-desktop.png).
- Dynamic inspector: [S1](app-proof-selected-s1.png), [S2](app-proof-selected-s2.png),
  [S3](app-proof-selected-s3.png), [S4](app-proof-selected-s4.png),
  [evidence](app-proof-evidence-inspector.png), [Layer C concept](app-proof-layer-c.png).
- P10 desktop: [timeline](app-activity-timeline-desktop.png), [graph](app-activity-graph-desktop.png),
  [Security filter](app-activity-filter-security-desktop.png), [Context](app-activity-context-inspector-desktop.png),
  [Diagnostic](app-activity-diagnostic-desktop.png).
- Tablet: [P09](app-proof-lineage-tablet.png), [P10](app-activity-timeline-tablet.png).
- Mobile: [P09](app-proof-lineage-mobile.png), [P10](app-activity-timeline-mobile.png),
  [390px sheet](app-proof-sheet-390.png).
- 320px: [Lineage](app-proofs-320-lineage.png), [Evidence](app-proofs-320-evidence.png),
  [Verification](app-proofs-320-verification.png), [Anchoring](app-proofs-320-anchoring.png),
  [proof sheet](app-proofs-320-sheet.png), [List](app-activity-320-list.png),
  [Graph](app-activity-320-graph.png), [activity sheet](app-activity-320-sheet.png).
- P09 system states: [Empty](app-proofs-empty.png), [Loading](app-proofs-loading.png),
  [Blocked](app-proofs-blocked.png), [Error](app-proofs-error.png), [Unavailable](app-proofs-unavailable.png).
- P10 system states: [Empty](app-activity-empty.png), [Loading](app-activity-loading.png),
  [Blocked](app-activity-blocked.png), [Error](app-activity-error.png), [Unavailable](app-activity-unavailable.png).

Tests cover PR1–PR4 regressions and PR5 selection, parent order, links, event
filtering, check/evidence distinctions, disabled real actions, no verdicts,
display-state clearing, immutable fixtures and source import/I/O guards.
Browser journeys check 1440, 834, 390 and 320px, no horizontal page overflow,
keyboard/tabs/focus return, sheet focus containment, reduced motion and Axe.
Requests must be local GETs, never API/RPC/prover/chain calls; WebSockets,
cookies and local/session business storage are absent in the tested journeys.
No private dataset, identifiers, shares, keys or artifact contents are supplied.

Local initial failures: stale Windows Turbopack subprocess/cache state was
resolved by moving only the generated `.next` cache outside the checkout and
rebuilding; no dependency or build configuration change. Two invalid testing
library options and two inaccurate new-test accessible names were corrected.
No core or existing regression assertion was weakened.

No complete WCAG certification, multi-browser certification, real backend,
authorization, verification, audit retention, chain query or finality guarantee.
Future adapters must supply authenticated, field-filtered metadata and distinct
authoritative assessments. Core tests do not authorize this UI.

## Invariants and debt

M1–M7 implementation, crypto configurations, contracts, generators, fixtures,
historical proofs/receipts/SHAs and chain evidence are unchanged. No Groth16,
blockchain transaction, deployment or RPC is run. No fixture migration or manual
regeneration is performed. Existing CI reproducibility jobs retain their
generator-and-clean-diff checks in disposable CI workspaces; those checks must
leave the tracked vectors unchanged and are not new cryptographic acceptance.
CI conditions, security settings, package/lock dependencies and PR3 fixtures are
unchanged. No license added, no new UI library, no PR6/PR7 work.
The existing broad `proofs/` ignore rule is unchanged; only the two reviewed
frontend `proofs/page.tsx` route source files are explicitly tracked.

M8-SEC-001 is preserved, not renewed or broadened. Mandatory reevaluation remains
**before PR7 or 2026-11-21, whichever occurs first**, with the additional triggers
in the original exception. No dependency change or new external pattern input
is introduced. Production dependency exclusion remains covered by frontend tests.

Final CI conclusions belong to the exact published HEAD / PR checks, not a
self-referential commit hash inside this report. The PR is left open for
independent review; green CI is not a new cryptographic acceptance.
