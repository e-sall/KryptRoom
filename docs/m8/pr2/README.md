# KRYPTROOM M8 — PR2 IMPLEMENTATION REPORT

## Baseline and scope

Branch: `feat/m8-rooms-easy-setup`.
Verified base: `acf5f262b03d6c0db3ff36b413f330b61f1181d2`, the merged PR #14.
Fetched origin/dev and checked GitHub's merged status before editing. The owner
authorized targeted CI scope conditions on 2026-10-22; see [CI scope](CI-SCOPE.md).
Final-head GitHub evidence is recorded in the PR. No automatic merge; main unchanged.

Only M8 PR2 presentation and the explicitly authorized CI scope conditions are
implemented. No M1–M7 code, dependency pins, schema, runtime, protocol or security
claim changes. A separately authorized exception refreshes exactly six synthetic
M5 metadata fixtures using the unchanged generator; it is not new proof validation.
See [migration evidence](M5-FIXTURE-MIGRATION.md). No PR3–7 implementation. No license.

## P03 — Rooms Home

- List by default; Cards uses the approved editorial selection + detail panel.
- Case-insensitive name/summary/organization search, status filter and clear/reset.
- Expand/collapse individual list rows; mini-history and snapshot refer to that row.
- Selected Room inspector, example organizations, illustrative status/activity,
  latest example state, detailed page and scoped Workspace navigation.
- Workspace destination is explicitly unavailable for PR3, not a fabricated graph.
- Empty/no-match, Loading, Blocked, Error and Unavailable examples are reachable;
  they remove stale fixture details from the inspector. The scenario selector is
  confined to preview, never a backend failure simulator in the application.
- List/Cards, filters, expansion and setup draft survive navigation inside the
  preview layout in memory. Reload starts fresh; no persistent Room store.

## P06 — progressive Easy Setup

1. Identity: 3–80-character fictional name, optional bounded description,
   restricted visibility. Continue validates fields but creates nothing.
2. Participants: optional organization/email pair with validation; fixed invitation
   examples pending/accepted/blocked/unavailable. No phantom participant is added.
3. Protected data: owning example organization and optional opaque `example-*`
   reference. Paths, URLs and raw rows fail reference validation. No file input,
   read, upload, real connector or raw-data transfer exists.
4. Policies: deny by default, optional aggregate-review draft preference,
   required organization approval, unavailable authenticated access, proof not
   assessed. Review/reset controls affect only the draft. No policy is saved.

Step selection is nonblocking so prerequisites can be explored at any time;
Continue validates the current fields, Back retains them. A completed draft does
not mark readiness green: Create Room, Send invitation, Connect data source,
Save Room policy and Run Computation are disabled with visible explanations.
No execution/reveal callback is present. A disabled button is not advertised as
a security enforcement mechanism; the service authority is simply absent.

## Actual backend boundary

`services/control-api`, `services/orchestrator`, `services/proof-service` contain
only `.gitkeep` at the inspected baseline. No authenticated Room API, room
persistence, invite service, protected connector service, policy/readiness service
or browser authorization session was found. Current core demos are not Workspace
APIs and were not invoked or repackaged as APIs.

- `/app/rooms`: honest unavailable collection; explicit link into synthetic preview.
- `/app/rooms/new`: creation unavailable; no editable production form.
- `/preview/rooms`: fixed `demo: true` fixtures, React-only view/draft state.
- `/preview/rooms/new`: explorable synthetic setup.
- `/preview/rooms/{fixture}`: details; unknown identifiers return 404.
- `/preview/rooms/{fixture}/workspace`: scoped unavailable destination, no PR3 graph.

Presentation types are not invented backend DTOs. Future integration requires
reviewed authenticated, policy-filtered contracts and server-derived decisions.

## Source fidelity and explicit adaptations

Read the original P03 V1/V2, P06 and P11 chat sources, prototype specs/interactions,
engineering contracts, traceability and seven-PR roadmap from the supplied ZIP.
The older handoff's source-recovery gaps are superseded by the recovered originals.
Original SHA-256 values:

- P03 List: `bb23db43775a7faec1ad440e7971eee420ad5037559d8696ad8c0edfe3bf0d39`.
- P03 Cards: `6a598440703cdcfcfdced68829b5d620f1ddfe5b648ae944c76ddcdf73fde990`.
- P06: `b5c46ca54f93bf84f40e16d11327f87222663772fb3c1ab39e9ec165836f551a`.
- P11: `833f9597342464eaf789f368b3f066609719d6db7715630eb3aa3dbafb486d4e`.

Original files remain outside Git, unchanged. Reference PNGs were rendered from
the archive's converted SVG components, with real React 19.3.1 server rendering
and Chromium. This replaces the archive viewer's pre-hooks React runtime only in
an external QA harness; it does not repair or relabel the archive as an original
interactive export. Selected initial states generate P06's four views and P11's
three device compositions. Static comparison is not interactive prototype parity.

Preserved: P03 full-width heading/search/filter controls, compact expandable rows,
editorial Cards with selected detail, dark surfaces/fine borders/blue selection;
P06 serif panel headings, simple identity then progressive steps/checklist;
P11 desktop inspector, tablet rail + inspector below, mobile navigation + sheet.
Canonical thin K and all PR1 tokens stay byte-unchanged.

Necessary HTML/authority adaptations (not pixel-perfect claims):

- PR1 navigation retained instead of reintroducing the older P03 three-item sidebar.
- Explicit preview banner, example status labels and unavailable authority add
  vertical space; no green approval is inferred from a selected step.
- Native labelled inputs/selects/buttons replace decorative SVG controls. Touch
  sizes, visible focus, text wrapping and 320px reflow take priority over scaling
  the entire desktop SVG. Controls and metadata can wrap instead of clipping.
- P03's illustrative S1/S2/S3 topology is retained **only as a labelled example**;
  it is not M1–M7's actual lineage and is not emitted as RoomState JSON.
- Cards has a wider contextual panel than List; tablet stacks it below content.
  The List inspector is retained from PR1/P11 alongside its inline expansion.
- P06's apparent create/send/connect/save actions remain disabled. Continue
  preview and Review example fields demonstrate progression, never success.
- No photos, new icon library, chart package, React Flow or Design System fork.

## Screenshots

Evidence captures, not pixel-diff golden baselines:

- List: [desktop](rooms-list-desktop.png), [tablet](rooms-list-tablet.png), [mobile](rooms-list-mobile.png); [P03 reference](reference-p03-list.png).
- Cards: [desktop](rooms-cards-desktop.png), [tablet](rooms-cards-tablet.png), [mobile](rooms-cards-mobile.png); [P03 reference](reference-p03-cards.png).
- Identity: [desktop](setup-identity-desktop.png), [tablet](setup-identity-tablet.png), [mobile](setup-identity-mobile.png); [P06 reference](reference-p06-1.png).
- Policy: [desktop](setup-policies-desktop.png), [tablet](setup-policies-tablet.png), [mobile](setup-policies-mobile.png); [P06 reference](reference-p06-4.png).
- [Mobile Room sheet](room-sheet-mobile.png); P11 [desktop](reference-p11-desktop.png), [tablet](reference-p11-tablet.png), [mobile](reference-p11-mobile.png) layout references.

Remaining setup-stage screenshots, 320px captures and browser report are generated
under `apps/web/test-results` / `playwright-report` and retained by frontend CI.
Full-page mobile captures include the fixed bottom navigation at the viewport's
bottom edge, not the document's end. Additional actual viewport captures show
[List](rooms-list-mobile-viewport.png), [Cards](rooms-cards-mobile-viewport.png),
[Identity](setup-identity-mobile-viewport.png) and
[Policy](setup-policies-mobile-viewport.png) without that full-page composition.

## Executed validation and exact limits

Local Windows / Node 24.12.0, pinned app dependencies and Chromium:

- Lint: PASS, zero warnings. Unit: PASS, **40 tests** (28 PR1 + 12 PR2 cases).
- Production build: PASS, **29 generated pages**. Typecheck: PASS.
- `npm audit --omit=dev`: PASS, zero reported production vulnerabilities.
- Playwright production-server run: **31 passed, 2 intentional non-mobile skips**.
  All 12 PR2 cases execute over desktop 1440×1000, tablet 834×1112, mobile 390×844;
  existing PR1 tests continue. Additional 320×740 checks exercise both views/setup.
- Search/filter, expansion/collapse, selection, navigation, all steps, invalid
  name/email/reference, optional prerequisites, draft retention/reset/reload,
  disabled business mutations, error/unavailable states and unknown fixture 404.
- Keyboard focus transfer, sheet Tab containment/Escape/focus return, visible
  focus and reduced motion. axe WCAG 2/2.1 A/AA subsets pass on captured views.
  No full WCAG 2.2 certification, screen-reader or cross-browser claim.
- Boundary tests: no external requests or non-GET mutations on tested journey,
  empty cookies/browser storage, no fixtures in application routes, no input file,
  network/storage/server action/core imports. Production traces exclude lint chain.
- First browser iteration caught missing route focus and low caption contrast on
  the protected-connection panel. Corrected with focus management and the existing
  primary text token; reruns pass. No tests weakened to conceal these failures.

Browser state is transient, not secure secret storage: users are explicitly told
to enter fictional metadata only. No auth/access-control implementation is claimed.
No participant dataset, key, secret share, identifier match, proof or output was
read. No cryptographic operation or blockchain transaction was launched locally.
CI outcome and which workflows executed must be read from the final PR evidence;
this report does not assume success or authorize cryptographic CI execution.

## Files and traceability

- `src/features/rooms`: presentation model/fixtures, isolated provider, room
  details/mini-history, home orchestration, Easy Setup/readiness and scoped CSS.
- `src/app/preview/rooms`: layout and home/new/detail/workspace pages.
- `src/app/app/rooms/new`: unavailable production boundary.
- Existing `app-shell.tsx` gains optional header/inspector slots; placeholder gains
  explicit preview entry. Existing component library and dependency locks unchanged.
- `tests/rooms.test.tsx`, `tests/browser/rooms.spec.ts`: new tests.
- Context/architecture, ADR-017, changelog, TODO, web README, evidence and security
  exception follow-up updated. M1–M7 implementation remains frozen.

KR-DES / KR-INT / KR-ACC 008–010: covered in synthetic P03 only; no real accessible
Rooms listing. 020: minimal identity interaction covered, **actual persisted
creation unavailable**. 021: progressive setup covered; no real completion.
022: fail-closed UI gate covered; no server readiness integration. 039–041:
three layouts/sheet covered for PR2. 042–043: bounded states/accessibility covered,
not the final PR7 audit. 011–019 and 023–038 / PR3–7 remain outside this PR.

## Residual debt and merge gate

M8-SEC-001 remains in force with unchanged dependencies/expiry: reevaluate before
PR7 starts or **2026-11-21**, whichever is earlier. No forced update/downgrade or
audit suppression. See [the exception](../pr1/SECURITY-EXCEPTION.md). Browser app
inputs do not reach lint; untrusted repository contributions remain a tooling DoS
risk and ESLint 9 remains unsupported.

Local PR2 implementation is ready for technical/design/security review, not a
production service launch. Human acceptance of documented visual adaptations,
tooling debt and final-head CI is required. Leave the PR open; do not merge main.

### CI scope authorization

The owner selected targeted frontend CI scoping rather than heavy cryptographic
execution. Six integration jobs retain every original step behind a shared scope
condition. Security/contract jobs still run. Existing manual execution and branch
events remain. No live-chain workflow was touched or dispatched. See
[CI-SCOPE.md](CI-SCOPE.md) for algorithm, test cases, protection inspection and limits.
