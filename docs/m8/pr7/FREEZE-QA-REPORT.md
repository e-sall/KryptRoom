# KRYPTROOM M8 — FINAL RELEASE / FREEZE QA REPORT

**Freeze candidate, not M8 closure or release authorization.** Reviewed 2026-10-25
on branch `feat/m8-responsive-accessibility-final-qa`, based on merged PR #19 / dev
`8e8d8349db565278a866bd82f743f03fd1ee8c35`. Exact published head and final CI
outcomes are linked in the PR; no merge is authorized by this report.

## A. Design implementation verdict

**Candidate ready for independent aesthetic review after final checks.**
P01–P11 are represented within the approved synthetic frontend scope, with the
new founder-directed homepage replacing prior marketing priorities. Section order,
autoplay showcase, portrait and final FAQ are implemented. The full P05 remains
separate and uses the same catalog. The application preserves P11's distinct
desktop/tablet/mobile compositions. See the [44-ID mapping](TRACEABILITY.md),
[marketing report](MARKETING-REDESIGN-REPORT.md) and [visual evidence](VISUAL-EVIDENCE.md).

Actual site renders and image captures were inspected, including all homepage
sections in three layouts, multiple scenes, app modes, mobile inspectors and
320px. This is not founder design approval, original-font certification or
pixel-perfect equivalence to source prototypes/Clean. No generated imagery or
copied Clean asset masks discrepancies.

## B. Frontend quality verdict

**Final executed totals are recorded below and on the PR.**

- Clean pinned npm installation, lint, typecheck and production build pass.
- **106 unit/component tests pass**, preserving all 104 prior cases.
- Final clean Chromium full suite: **133 PASS, 2 inherited non-mobile sheet skips**
  (135 total, 4.8 minutes). Chromium 156.0.8078.4 / Playwright 1.64.1.
  An earlier run was interrupted by host `ERR_NETWORK_IO_SUSPENDED`; all seven
  affected cases passed unchanged on explicit rerun, then the final full suite
  passed cleanly. No error filter or skip was added for the interruption.
- Firefox: blocked before launch by the host’s side-by-side runtime configuration.
  WebKit 27.2: **22 PASS**, all new freeze/home cases on desktop and narrow
  layouts, including real focus, modal traversal, autoplay and all frame sizes.
  Command: `npx playwright test --config=playwright.cross-browser.config.ts
  --project=webkit-desktop --project=webkit-mobile --workers=1`.
- **31 unchanged CI classifier tests pass**, including conservative negative cases.
- Both full and production npm audits: **zero findings**.

The new tests add the exact Landing → seven-scene Demo → S4 → Graph → S2 →
Computations → Results → Proofs S3 → Activity S3 → no-result filter → different
Room → Rooms → empty Research Graph journey in every baseline layout. Existing
tests retain exact-state links and chart/table parity. Invalid Room/state/category
deep links return 404, without fabricated proof/results. System-state examples
remove stale selection/inspectors before displaying empty/loading/blocked/error/
unavailable content; Room changes do not carry an obsolete event or result.

Responsive module matrix: 1440,1280,1024,834,768,390,375,320 CSS pixels. Showcase
additionally checks 1366×768, plus the requested heights and all seven scenes.
Containment, no inner clipping/scrolling, stable scene height, no horizontal page
overflow, parent edges and visible labels are asserted. Narrow layouts reflow;
they do not force all content into 100vh. Rotation crosses 766/834/1024 and
844×390 landscape; selected state survives while the modal retires correctly.

Keyboard: focus visibility around fixed navigation/header, Tab/Shift+Tab wrap,
Escape, restoration to visible trigger/main, nonmodal traversal, skip link,
tabs/Home/End/arrows, native FAQ and disabled actions. Representative button/nav/
segmented targets have >=24px dimensions; existing controls generally use 44px.
Axe checks WCAG 2 A/AA, 2.1 AA and, in the new suites, 2.2 AA tagged rules. No
violations in analyzed states. Semantic SVG titles/descriptions/Table alternatives
are retained; graph relationship text carries the same ordered data.

Autoplay advances every six seconds only when visible, document-visible and
motion allowed; it loops, pauses/resumes/replays deterministically, stops offscreen
and on a deterministic hidden-tab visibility event. No late timer or random reset.
Reduced motion uses manual scenes, no auto transition. Server rendering/no-JS
fallback is tested. Running changes are not announced every six seconds.

**Limitations:** no NVDA/VoiceOver/TalkBack test, formal WCAG audit, real mobile
hardware or actual Safari/iOS session. 200% reflow is simulated as a 640 CSS-pixel
layout for a 1280px window, not an executed browser-toolbar zoom certification.
Local Chromium uses the pinned Playwright distribution; WebKit reports 27.2.
Local engines are Playwright on Windows; CI remains Chromium. Firefox 157.0
  (build 1555) could not start: Windows reports an incorrect side-by-side
  configuration, and Playwright reports spawn UNKNOWN before page creation. No
  Firefox site validation is claimed. Installing machine-wide runtime components
  was not silently attempted. WebKit 27.2 initially exposed 667 CSS pixels for an
  834px request because of the host’s 125% display scale. A test-only helper now
  normalizes viewport requests and asserts actual innerWidth/innerHeight; no
  browser security setting or assertion was bypassed. CSSOM scroll widths round
  up fractional pixels, so overflow comparisons use the ceiling of the actual
  visual viewport. Keyboard assertions wait for the next rendered frame. WebKit
  also required a real focus visibility correction and explicit opener focus,
  implemented in shared UI and covered by the same regressions.
Two original desktop/tablet skips concern the mobile-only inspector trigger;
no new skip or suppressed assertion was introduced. New transition tests exercise
the previously untested resize boundary in every project.

## C. Security / operational readiness verdict

**Conditionally accepted development-tooling risk; operational platform unavailable.**
The founder approved M8-SEC-001 for ESLint 9 EOL only until **2026-11-01 23:59
America/Toronto**, reevaluate before PR7 merge or expiry. The GHSA portion is
closed by official October 23 withdrawal. Peer-compatible direct ESLint 10
migration fails ERESOLVE; no forced install, downgrade or audit suppression.
Current decision/evidence/owner/exit criteria: [Phase 0 report](PRE-PR7-SECURITY-REEVALUATION-REPORT.md)
and [canonical exception](../pr1/SECURITY-EXCEPTION.md). A bounded read-only watch
monitors upstream through expiration; new material risk stops work. This is not
production approval or an automatic extension.

The frontend remains synthetic and disconnected. Source and browser guards reject
business I/O, storage/private data access, crypto imports, fabricated commitments,
RPC/prover/WebSocket and mutation calls. No matched identifiers, joined rows,
shares or keys are rendered. No plaintext joined dataset is materialized by the
frontend. This source/browser boundary check is not a fresh cryptographic proof.

M1–M7, protocols, dependency pins, CI controls/classifier, generators, fixtures,
historical proof/receipt/SHA/anchor evidence and runtime security settings are
unchanged. No Groth16, blockchain transaction, deployment or costly cryptographic
acceptance was executed for frontend QA. Existing fast CI controls remain active;
heavy scoped skips must not be reported as fresh core execution.

Authentication, production Control Plane, KryptNode integration, orchestration,
operational KMS/keys, real permission/reveal services, proof APIs and booking are
not available. The product preview, bounded core evidence and integrated
operational platform remain explicitly distinct. [Debt inventory](DEBT.md) lists
the retained risks and future integration requirements without starting M9.

## Publication and independent-review gate

The PR must target dev and remain **OPEN / UNMERGED**, with auto-merge off.
Inspect every workflow against the published head, including expected heavy-job
skips. Do not modify main or create a release tag. Working tree must be clean
and local feature branch synchronized with its remote, not tracking dev.

Before any future merge: independent aesthetic/technical review, security
reevaluation within the limited approval, and explicit founder authorization.
No `M8 COMPLETED` claim is made. Speculative Next Link prefetching produced page errors in WebKit while explicit
navigation worked. M8 links now use the documented `prefetch={false}` option;
hrefs, routing and guards are retained. Route inventories await completion before
starting another navigation, and the Room-change test now asserts the destination
URL/header before checking absence of stale data. Modal Tab traversal explicitly
includes all visible controls/links, even if host-native settings skip links.
No page-error filter, disabled security flag or new skip was added.

[Machine-readable local observations and source fingerprints](BROWSER-VALIDATION.json)
retain the exact browser versions, outcomes and WebKit case names. These are
unsigned diagnostics, not proof or certification.

Final disposition is recorded in the PR after
CI inspection; unfinished or failed material gates require CHANGES REQUIRED.
