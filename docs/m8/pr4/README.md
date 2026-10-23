# KRYPTROOM M8 — PR4 IMPLEMENTATION REPORT

Date: 2026-10-23. Branch: `feat/m8-computations-results`.
Verified base: `2c912bcfc52d281ecdfda5798fc75e47b87fdf1e` (PR #16 merged into dev).
Published HEAD, PR number and final remote CI conclusions belong in the PR body,
avoiding a self-referential commit hash here. PR4 must not be automatically merged.
Main baseline: `1715b504e2041127056127ab5236a3248195a234`; not changed by this work.

## Initial audit and scope

Rechecked remote dev, PR #16 merge and absence of concurrent source changes before
creating this branch. Read AGENTS, project context, architecture, security, relevant
ADRs, existing PR1–PR3 implementation, original P07/P08, P04/P11, M8 engineering
contracts, traceability and seven-PR roadmap. Control API, orchestrator and proof
service remain placeholder directories, not deployed Workspace APIs.

This is functional frontend presentation, **not** real execution integration.
All new interactive screens live under `/preview/rooms/[roomId]`. Production
`/app/computations` and `/app/results` retain unavailable module placeholders.
No fake response, endpoint, business persistence, credential, runtime configuration
or cryptographic fixture is introduced. No PR5–7 implementation is included.

## Modules and effective interactions

- `features/operations/presentation.ts`: closed PSI/Join/Analytics vocabulary,
  fixed cardinality/aggregate fixtures, ordered selections, always-denied business
  readiness and Room/state links. Result context derives from `graphFixture`.
- `computations-workspace.tsx`, `workflow-diagram.tsx`, `computation-inspector.tsx`:
  selection, operator, forward/back/direct phase navigation, finite emphasis,
  reset and two inspector tabs. No timers, run IDs, execution logs or percentages.
- `results-workspace.tsx`, `result-visuals.tsx`: one editorial result at a time,
  category routes, fixed PSI count, protected Join illustration, Analytics
  chart/table parity, native progressive details and contextual disclosure panel.
- `preview-controls.tsx`: shared Room chooser, contextual trail, keyboard tabs,
  explicitly labelled Empty/Loading/Blocked/Error/Unavailable display scenarios.
- `operations.css`: component-local composition using unchanged PR1 tokens,
  canonical K, shell, buttons, badges and dialog. No new chart/store dependency.
- New static Computations, Results/category and Workspace/state routes; existing
  graph adds cross-links and validated initial state selection. Shared shell
  optionally preserves the selected Room across Graph/Computations/Results.

P07 phases: Protected Inputs → Private Operation → New State & Review. Inputs
show ordered parent references, dependencies and non-resolvable artifact labels.
The dashed output has no state ID/digest and never enters the graph. Changing
operator returns to preparation; reset/reload discard local workflow choices.
Readiness distinguishes presentation selection from input availability, policy,
approvals, execution/disclosure authority and backend availability. Review covers
hypothetical transition and unavailable actual output. All Run/Approve/Save
controls stay disabled. A complete presentation is never a server permission.

P08 retains three distinct Premium V3 views, not three simultaneous result cards:
PSI displays **1,248** only; Join displays no table or row-level matches; Analytics
displays fixed **A=42, B=68, C=55, D=81** with the same array for chart and table.
These are arbitrary sample units, not actual patient counts, MSE or MPC outputs.
Reveal/Download remain disabled. Provenance is the fixed P08 design fixture,
not a receipt; proof is Not assessed and chain/commitment are Unavailable.
Blocked/system scenarios remove values and stale inspector context.

## P03 / P04 / P08 identity reconciliation

No duplicated RoomState catalog or mutation of PR3 fixtures. Supply Chain retains
S1 Initial State, S2 Private Join, S3 Analytics and the explicitly illustrative
two-parent S4 Private Analytics extension. Join links to S2; Analytics links to
S4 with ordered sources [S2, S3]. Research remains empty, with no invented result.
Insights retains its S2 PSI. Supply Chain PSI has no associated PSI state and is
explicitly hypothetical; it does not relabel S2 or claim a real transition.

Recovered P08 uses historical PSI S2 / Join S3 / Analytics S4 labels. These were
presentation examples, not canonical core lineage. PR4 deliberately preserves
the existing P03/PR3 identities instead of silently adopting the conflicting
Join S3. The fixed result shown after a workflow is independent of input choices
and clearly labelled as such. No new state/parent relationship is persisted.

Exact-state links use `/workspace/[stateId]`; static parameters and not-found
checks constrain both Room and state. Unknown result categories fail closed.
The full journey Rooms → Details → Graph → Computations → Results → Graph is
tested, including checking that the four-node synthetic graph remains unchanged.

## Design provenance and visual adaptations

Original inputs in `KryptRoom-M8-Source-Consolidation.zip`:

- `original-sources/P07-Computations/chat-message-1.txt`, SHA-256
  `dd3c3cb65ba5bbefd2586d402209db1f4dada4bf572e400ced74e0d8af986b49`.
- `original-sources/P08-Results-Analytics/chat-message-1.txt`, SHA-256
  `f033345a3b581f9e5209b1b43d967e9ba6486781e8301235ab0ed0c2f0de2faf`.

Original source text was inspected without modification. It is not a screenshot
of an executable original environment. `converted-*.png` are explicitly labelled
**static conversions** of the recovered portable JSX using the installed React
server renderer; initial display state was varied in memory for each view. They
are not native-original runtime captures and are not application screenshots.
`app-*.png` are actual production Chromium application captures. No pixel-perfect
claim or replacement of the locked source is made.

Preserved: warm dark surfaces, thin borders, blue operation emphasis, protected
inputs → central operation → dashed output, right inspector, P08 serif editorial
headlines and large number, overlap circles, two-organization join handoff,
four-bar chart, separate categories and progressive details.

Necessary adaptations:

- Semantic HTML controls replace fixed SVG hit targets. Three visible phase
  controls and input selection implement the explicitly requested Clean journey.
  The diagram uses responsive source cards and directional connectors instead
  of fixed prototype coordinates; parent order/dependencies are readable text.
- Current synthetic state references replace apparent local-data connections;
  no fabricated policy approval, receipt, date, commitment or proof verdict.
- Explicit preview labels and real disabled-action explanations take additional
  vertical space. The inspector covers all requested authority boundaries.
- Desktop sidebar/right inspector; tablet compact rail/below-content inspector;
  mobile stacked categories/inputs and bottom sheet, not scaled desktop controls.
- Mobile chart labels are larger; accessible SVG title/description and a semantic
  table provide alternate reading. At 320px the page remains within its viewport.
- Phase emphasis lasts 280ms and is removed under reduced motion. Phase selection
  remains visible without motion. Keyboard tabs support Left/Right/Home/End.
- Fixed bottom navigation may appear across a full-page mobile capture at the
  capture viewport boundary. Viewport screenshots distinguish this artifact
  from the actual scrollable layout; content remains reachable by scrolling.

### Evidence gallery

Converted references: [P07 Readiness](converted-p07-readiness.png),
[P07 Review](converted-p07-review.png), [P08 PSI](converted-p08-psi.png),
[P08 Join](converted-p08-join.png), [P08 Analytics](converted-p08-analytics.png),
[P08 Table](converted-p08-table.png).

Application desktop: [Inputs](app-inputs-desktop.png),
[Operation](app-operation-desktop.png), [New State/Review](app-review-desktop.png),
[Readiness](app-readiness-desktop.png), [PSI](app-psi-desktop.png),
[Join](app-join-desktop.png), [Analytics](app-analytics-desktop.png),
[Details/Table](app-table-desktop.png).

Responsive: [tablet workflow](app-inputs-tablet.png),
[tablet Analytics](app-analytics-tablet.png), [mobile workflow](app-inputs-mobile.png),
[mobile Analytics](app-analytics-mobile.png), [mobile viewport](app-analytics-mobile-viewport.png),
[Readiness sheet](app-readiness-sheet-mobile.png), [Result sheet](app-result-sheet-mobile.png),
[320px workflow](app-workflow-320.png), [320px result](app-result-320.png),
[320px sheet](app-result-sheet-320.png).

Display examples: [Empty](app-empty.png), [Loading](app-loading.png),
[Blocked](app-blocked.png), [Error](app-error.png), [Unavailable](app-unavailable.png).
The full browser run produces additional per-format/per-screen captures in the
GitHub frontend evidence artifact, with seven-day retention. Selected durable
captures above are committed; they contain only the synthetic interface.

## Validation and corrections

- Lint, TypeScript and optimized build: PASS, 50 prerendered pages.
- Frontend units/components: 67 PASS, including 13 PR4 cases and inherited PR1–3.
- Existing CI-classification suite: 31 PASS, no classifier modification.
- Existing M5 Python: 13 PASS; existing M7 Python: 45 PASS in `.venv-m7`.
  The default host Python initially lacked `cryptography`; using the existing
  project environment resolved the import failure without installing packages.
- Production Chromium PR1–PR4: **52 PASS, 2 inherited non-mobile sheet cases
  intentionally skipped** (54 total); all 12 new PR4 cases PASS. Desktop
  1440×1000, tablet 834×1112, mobile 390×844, narrow checks 320×740.
  Coverage includes keyboard/focus return, sheets, reduced motion, all five
  system states, exact-state navigation, immutable source state, storage empty,
  request/error audit and Axe WCAG 2 A/AA + 2.1 AA. Not full WCAG certification.
- The unchanged CI retains M5 native Rust contracts and M5/M7 reproducibility,
  M7 Foundry local contract tests and all applicable security/contract checks.
  Final-head conclusions, including deliberately skipped heavy integrations,
  are recorded in the PR body, not assumed from local test results.

Concrete defects addressed: insufficient contrast on active workflow labels and
decorative dots; mobile chart text too small; pre-existing Room mini-history SVG
`title` had multiple children, causing React hydration mismatch. It now uses one
string with identical content. Test-only errors included a reserved variable name,
ambiguous alert selector (Next route announcer) and testing-library option types.
No failed assertion or privacy/network audit was removed to obtain a pass.

The first Turbopack build hit a local worker/cache error before compiling app
code. Its generated `.next` cache was moved to a recoverable directory outside
the repository; fresh production builds passed. No runtime setting was changed.
A development-server-generated AGENTS file was removed from the PR scope after
reading its local Next guidance; no pre-existing instruction file was removed.

## Privacy, cryptographic controls and acceptance

Diff checks against the base must show no M1–M7 code, contracts, fixtures,
generators, workflows, CI classifier, dependencies or runtime security changes.
Browser checks allow only local GET navigation/assets, no API/RPC, mutation,
WebSocket, private runtime call or storage-based persistence. Source tests reject
crypto imports, network/storage APIs and fabricated commitment-like values.
All displayed Room/artifact/result labels are fixed synthetic presentation data.
No joined plaintext, matching identifiers, secret shares, keys or KryptNode paths
are read. UI tests are not evidence of new cryptographic execution or security.

No Groth16, blockchain transaction, deployment, MPC or FHE execution is launched
by this task. The existing CI filters must skip the five heavy integrations for
this frontend/docs-only diff, while retaining fast core controls. Historical
proofs, M5/M7 migration provenance and the finalized anchor remain unchanged.

KR-DES/INT/ACC 022–031 are addressed within the disconnected preview. Real
execution progress (026) is unavailable, not simulated with invented events.
Responsive/accessibility 039–043 are exercised for PR4, not claimed as final
PR7 certification. Production authorization, services, exports, private output
integration and proof/chain verification remain unimplemented by design.

M8-SEC-001 is unchanged: temporary lint-tooling debt, mandatory reevaluation
**before PR7 or 2026-11-21, whichever comes first**. No downgrade, forced audit
fix, new dependency, license or broader security claim. Technical merge readiness
requires green final-head CI and human design/security review; **do not merge PR4**.
