# KRYPTROOM M8 — PR3 IMPLEMENTATION REPORT

Date: 2026-10-22. Branch: `feat/m8-graph-workspace`.
Mandatory start/base: `a88df46a0213d7c422410db4d5cde32f8c3de897`.
Final published HEAD, PR URL and remote conclusions are recorded in the PR body
after publication, avoiding a self-referential commit hash in this file.

## PR2 integration verified

PR #15 was manually merged after explicit owner approval, with expected head
`6fad900730a0d2cd79585ed6f32006c13fa495e3` and unchanged dev base
`acf5f262b03d6c0db3ff36b413f330b61f1181d2`.
GitHub returned MERGED and merge commit
`a88df46a0213d7c422410db4d5cde32f8c3de897`.
All ten approved-head workflows passed; the five heavy MPC/FHE jobs and Groth16
were explicitly skipped, not reported as new cryptographic validation.
Post-merge dev: ten workflows passed (including M5/M7 reproducibility).
The migration documents and historical proof/anchor evidence remain intact.
Main remains `1715b504e2041127056127ab5236a3248195a234`.

## Audit and backend boundary

Read AGENTS, project context, architecture, security policy, ADR-008–017, recovered
P04 V3/P11 originals, engineering contracts, traceability and seven-PR roadmap.
PR1/PR2 code is present in the merged base. The three service directories
(Control API, orchestrator, proof service) contain placeholders, not a Workspace
API. The actual dataclasses in `engines/mpc/room_state.py` are frozen:
RoomState, ArtifactRef, StateTransition, StatePolicy, CryptoContext and
StateCommitment. Both state and transition use ordered list-valued parents;
serialized keys are camelCase. Artifact context binding and state hashing remain
entirely core concerns, not frontend calculations.

Only `/preview/rooms/[roomId]/workspace` renders the graph. Production
`/app/graph` remains unavailable, with no fixture fallback, authenticated Room,
API, persisted state or execution implied. The preview reuses the P03 Room IDs
and labels, adds an explicitly illustrative two-parent S4 to Supply Chain, and
keeps Research empty and Insights small. This is not the actual M1–M7 lineage.

## Architecture and interactions

- `model.ts`: readonly safe display projection, stable topological construction,
  ordered parent edges, duplicate/missing/self/cycle rejection, neighborhood.
- `layout.ts`: deterministic longest-parent-rank columns; stable sibling lanes,
  centered roots/leaves; transposed ranks on narrow canvases; viewport transforms.
- `fixtures.ts`: frozen, explicitly synthetic display labels, plus a separate
  24-node stress scenario. No cryptographic fixture imports or hashes.
- `state-canvas.tsx`: real HTML node buttons over directional SVG edges.
  Pointer/touch background pan, zoom buttons and modifier wheel, Fit View,
  Center selected, focus visibility and ordered accessible state list.
- `graph-inspector.tsx`: shared desktop/tablet/mobile inspector, ordered parent
  and child navigation, four Detailed tabs with distinct contents.
- `graph-workspace.tsx`: local selection/mode/scenario state; no storage or I/O.
  Future authorized integration must provide a separately reviewed safe
  projection, not spread full core metadata or freeze an invented API contract.

Classic defaults to compact nodes and a simple inspector without tabs.
Detailed adds operation/parent metadata and Overview / Inputs / Outputs /
Metadata tabs. Focus centers the selected state and emphasizes its immediate
parents/children; other nodes remain reachable and visually subdued. Returning
to full view restores the prior Classic/Detailed mode. Selection survives mode
switches. Above 115% zoom the selected compact node exposes its parent summary.

Keyboard: canvas arrows pan, +/− zoom, F fits; node Left/Right select first
parent/child, Up/Down traverse topological order, Home/End reach endpoints,
Escape deselects. All other parents/children are individually navigable in the
inspector and ordered list. Long-list selection scrolls the canvas into view.
Inspector tabs have roving focus, Left/Right, Home/End; the reused native modal
traps focus and restores the trigger. No graph mutation or edge editing.

No React Flow dependency was needed: this is a read-only DAG browser, not a node
editor. Native controls preserve existing accessible primitives and lockfile.
The layout is intentionally simple, not a general crossing-minimization engine.
Stress coverage is 24 nodes; very large graph virtualization, arbitrary imports,
pinch zoom and server authorization remain future work. Zoom is bounded 2–200%;
small overview text is supplemented by centered selection and the readable list.

## P04/P11 fidelity and explicit adaptations

Original source: consolidation archive's
`original-sources/P04-Graph-Workspace/chat-message-1.txt` (V3 corrected) and
`original-sources/P11-Responsive-Polish/chat-message-1.txt`.
The existing portable P04 preview still throws `React.useState` in its bundled
runtime. To inspect geometry, the existing converted JSX/JS was rendered
statically with the project's React 19 server renderer; only initial display
mode changed for each capture. Original files were not edited. These captures
are labelled converted static references, not an original interactive runtime.
The application is independently implemented in React/Next, not copied from it.

Unchanged source SHA-256 references:

- Archive: `a246398a95dd151cfa6bfc02b72a82b654a077e0796d1a2796274d2159df68bf`.
- Original P04: `3a9d761e8876e16bf67a7db334834cf27530da322a2fa681dab3f9171d720ebd`.
- Original P11: `833f9597342464eaf789f368b3f066609719d6db7715630eb3aa3dbafb486d4e`.

Compared Classic/Detailed/Focus, blue selected nodes, curved parent paths, thin
borders, warm surfaces, inspector hierarchy and mobile vertical topology.
Canonical thin P11 K and all PR1 tokens remain unchanged (old P04 thick K is not
restored). Desktop keeps sidebar + canvas + right inspector, tablet the compact
rail + below-content inspector, mobile bottom nav + vertical DAG + details sheet.

Necessary adaptations, not redesign claims:

- HTML text/buttons, 38–40px viewport controls, keyboard equivalent and explicit
  synthetic labels replace fixed SVG text targets and decorative controls.
- Classic nodes use 158×88 logical pixels (142px wide on narrow canvases);
  Detailed uses 184×144 (142px narrow), versus the smaller original SVG cards.
  Dynamic rank/lane spacing replaces four hardcoded coordinates.
- Classic/Detailed/Focus are adjacent semantic buttons; Focus emphasizes the
  selected neighborhood instead of cropping the original SVG viewBox.
- P03's existing S2 Private Join / S3 Analytics labels are preserved instead of
  silently rewriting PR2 to P04's different illustrative labels.
- No fabricated dates, protocol parameter sets, commitments, proof records,
  results or enabled disclosure actions. Readonly synthetic reference labels
  replace the prototype's apparent result action.
- Accessible help, the state list and unavailable-service explanations take more
  vertical space. Mobile page scrolling remains available outside the pan area;
  no horizontally overflowing page or hidden essential control at 320px.

No pixel-perfect claim; visual fidelity and these adaptations remain subject to
independent review. P09/P10 are extension points only, not implemented screens.

## Evidence gallery

- Converted references: [Classic](reference-p04-classic.png),
  [Detailed](reference-p04-detailed.png), [Focus](reference-p04-focus.png),
  [P11 desktop](reference-p11-desktop.png), [P11 mobile](reference-p11-mobile.png).
- Application: [Classic + selected S4](classic-desktop.png),
  [Detailed](detailed-desktop.png), [Focus](focus-desktop.png),
  [tablet](classic-tablet.png), [mobile](classic-mobile.png),
  [mobile viewport](classic-mobile-viewport.png), [bottom sheet](bottom-sheet-mobile.png).
- System states: [Empty](empty-desktop.png), [Loading](loading-desktop.png),
  [Blocked](blocked-desktop.png), [Error](error-desktop.png),
  [Unavailable](unavailable-desktop.png), [320px](narrow-320-mobile.png),
  [320px sheet](narrow-sheet-mobile.png), [long DAG](long-dag-desktop.png).

Full-page mobile screenshots include the fixed bottom navigation at the capture
viewport boundary; viewport captures distinguish that screenshot artifact from
the actual scrollable layout. All states are explicitly display examples.

## Tests, failures addressed and limits

- Lint, typecheck, production build: PASS; 29 prerendered pages.
- 54 units/components: PR1/PR2 regression plus DAG ordering, multi-parent, cycles,
  missing/duplicate parents, multiple roots, empty/long layouts, view transforms,
  mode/selection/inspector behavior and privacy boundary.
- Chromium production server: full PR1/PR2/PR3 suite, 40 PASS and two inherited
  non-mobile modal cases intentionally skipped (42 total, all nine PR3 cases pass).
  Desktop 1440×1000, tablet 834×1112, mobile 390×844 and 320×740.
  Includes Axe WCAG 2 A/AA and 2.1 AA automated checks, reduced motion, keyboard,
  pointer pan, actual CDP touch pan, modal focus/return, all system states and
  request/error audit. Automated Axe is not full WCAG 2.2 certification.
- Existing CI scope suite: 31 PASS; existing M5 Python: 13 PASS;
  existing M7 Python: 45 PASS. No changes to those tests or fixtures.
- Exact diff against merged base confirms no change in engines/nodes/packages/
  chain/core tests/workflows/CI classifier, including M5/M7 golden vectors.
  No generator, prover, live-chain workflow or crypto integration launched locally.

During implementation, lint caught effect-driven viewport synchronization; it
was replaced with a layout-keyed derived default plus explicit manual view state.
Typecheck caught a testing-library option error. Chromium caught a long-list
selection leaving the graph outside the page viewport; selection now scrolls
the canvas into view. Tests also needed hydrated transform comparisons and
viewport-safe pointer coordinates, not raw SSR style strings. No core test was
weakened or bypassed.

## Security, acceptance and remaining work

No network/storage/server-action/core import added. Only fictional metadata is
rendered. Proof is Not assessed, anchor and commitment are Unavailable; no
Verified/Finalized fixture verdict exists. Result actions remain disabled and
unknown authority never grants disclosure. Client labels are not authorization.
No new dependency, license, security claim or runtime setting.

M8-SEC-001 unchanged: owner accepted temporary lint-tooling debt, reevaluate
before PR7 or 2026-11-21, whichever comes first. No silent extension.

KR-DES/INT/ACC 011–015 covered in the isolated preview. 039–043 covered for this
screen only, not final PR7 certification. Production data integration and
authoritative access/verification remain unavailable; PR4–PR7 not implemented.
Merge readiness is technical frontend readiness subject to final-head CI and
independent design/security review. PR3 must remain open; do not merge it.
