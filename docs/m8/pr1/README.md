# M8 PR1 — Design System & App Shell implementation evidence

## Scope and baseline

Branch: `feat/m8-design-system-shell`. Audited `origin/dev` baseline:
`090f65eed8a96dc90f24ec7531b01be555542e31`. `apps/web` contained only `.gitkeep`.
No application API or production Control Plane was found. M1–M7 remain frozen.
This PR does not merge itself, alter `main`, run Groth16 or broadcast transactions.

The source is the user-supplied `KryptRoom-M8-Source-Consolidation.zip`.
README, source manifest, recovery inventory, preparation, export validation and
repo audit were inspected before implementation, followed by the design system,
final design report, engineering contracts, traceability, roadmap, accessibility,
motion and crypto visual-language handoff. All 12 original-source SHA-256 hashes
matched the supplied manifest. Original sources remain unmodified outside Git.

Primary source identifiers (SHA-256 of the original chat-source file):

- P01: `9afeec9e672a6fc6c37bacfdfa0aad8063705edad9dff5779d9c7b19bf3ab67f`.
- P03 list: `bb23db43775a7faec1ad440e7971eee420ad5037559d8696ad8c0edfe3bf0d39`.
- P03 cards: `6a598440703cdcfcfdced68829b5d620f1ddfe5b648ae944c76ddcdf73fde990`.
- P04: `3a9d761e8876e16bf67a7db334834cf27530da322a2fa681dab3f9171d720ebd`.
- P11: `833f9597342464eaf789f368b3f066609719d6db7715630eb3aa3dbafb486d4e`.

Traceability: KR-DES-001–004 are addressed only for shared identity/hero/navigation
foundation, not the PR6 marketing site. KR-DES-039–041 cover the three layout
classes. KR-DES-042–043 are addressed for shared states and keyboard behavior,
not a completed product-wide PR7 accessibility audit. Rooms list/cards, creation,
DAG, computation, results, proof and activity interactions remain deferred.

## Architecture and decisions

Next.js 16.4.2 / React 19.3.1 / TypeScript 5.9.3 / Tailwind 4.3.3, with exact
dependency versions and a standalone app lock. See ADR-016 in `docs/DECISIONS.md`.
No root workspace migration or core dependency update. Static App Router pages
carry public presentation only; narrowly scoped client components own navigation,
dialogs and component examples. No API routes, server actions, network adapters,
browser persistence, analytics SDKs or remote fonts were added.

Reusable foundation: K mark, brand, decorative stroke icons, three button
variants, disabled/loading states, neutral/warning/error badges, cards, labelled
fields, empty/loading/blocked/error/unavailable states, native dialog with explicit
Tab wrapping, focus return, Escape/backdrop dismissal, reduced-motion override.

Responsive shell: desktop sidebar + right inspector at >=1200 CSS px; tablet
76px rail + inspector below at 768–1199px; mobile bottom navigation + details
sheet below 768px. Route changes update the breadcrumb/current item and main
focus. Unknown routes return 404. The route catalog is the extension point,
not a proposed backend DTO.

## Visual comparison and adaptations

The checked-in PNGs are evidence captures, **not pixel-diff golden baselines**.
Reference images were rendered from the ZIP's supplied conversions, whose SVG
geometry was cross-checked against original source; they are not new mockups.

- [P01 supplied reference](reference-p01.png) and [implemented hero](marketing-desktop.png):
  warm palette, light/gray K, serif single-line desktop tagline, text-first layout,
  compact pill actions and negative space retained. The real page uses a 1280px
  max-width HTML layout instead of scaling an 840×470 SVG. A foundation footer
  labels the scope. Full marketing narrative/booking remains PR6.
- [P03 supplied cards reference](reference-p03-cards.png) and [implemented shell](rooms-desktop.png):
  sidebar/surface hierarchy, fine borders, muted blue selection and compact
  typography retained. Fake rooms/cards, counts, participants and state graphs
  are deliberately absent; unavailable content and a context inspector replace
  them. The PR1 shell is not a completed P03 Rooms implementation.
- [Tablet](rooms-tablet.png): compact rail and below-content inspector, checked
  against P11 source geometry/principles.
- [Mobile](rooms-mobile.png) and [details sheet](inspector-mobile.png): fixed bottom
  navigation, scrollable content, contextual sheet and safe-area spacing. `More`
  gives access to every deferred module without suggesting a selected Room;
  it temporarily replaces the prototype's direct Results tab. PR2 can restore
  room-scoped navigation once a real Room context exists.

Important reference limitation: the unmodified portable viewer rendered P01 and
both P03 variants, but **P04 and P11 failed in Chromium** with
`React.useState is not a function or its return value is not iterable`.
No interactive parity PASS is claimed for those conversions. Their original
SVG/source remains authoritative for layout. Their embedded synthetic S1–S4
lineage is not the actual M1–M7 state contract and was not copied into the app.
The K uses the exact P04 three-path geometry/colors, shared with marketing;
P11 contains another gray-branch geometry, so no pixel-identical P11 logo claim.
Product/design review of these explicit adaptations remains required.

## Executed local checks

Executed on Windows, Node 24.12.0, pinned Chromium 156.0.8078.4 (Playwright 1.64.1):

- Production `npm run build`: PASS, 20 generated pages. Initial sandbox-only
  Turbopack subprocess failure was resolved by running the same build outside
  the sandbox; no bundler downgrade or application workaround.
- `npm run lint`: PASS, zero warnings. `npm run typecheck`: PASS.
- `npm test`: PASS, 24 tests across two files. Button variants, disabled/loading,
  field semantics, cards/brand/links, all state variants, closed module routing,
  all nine unavailable modules, locked palette/motion/breakpoints and source I/O guard.
- `npm run test:e2e`: PASS, 16 executed tests; 2 intentional skips because the
  inspector-sheet test is mobile-only. Desktop 1440×1000, tablet 834×1112,
  mobile 390×844, plus 320px narrow checks. Real production server, no mocks.
- Browser checks: every module route, active breadcrumb, disabled creation,
  sidebar/rail/inspector positions, no horizontal overflow, visible keyboard
  focus, Tab/Shift+Tab containment, Escape/focus restoration, error/loading
  examples, reduced motion, skip link, marketing links and 404.
- axe WCAG 2 A/AA and 2.1 AA rule subsets: zero violations on tested shell,
  hero and gallery views; mobile inspector also scanned. This is **not** a full
  WCAG 2.2 certification, screen-reader audit or all-browser guarantee.
- Browser boundary check: zero third-party requests, zero mutations, no page
  errors, no cookies/localStorage/sessionStorage on the tested Rooms entry.
- `npm audit --omit=dev --audit-level=moderate`: zero reported vulnerabilities
  at execution time; not a guarantee against future advisories.
- Clean `npm ci`: PASS. Full audit: **5 high-severity development-only findings**
  from one unpatched `braces` stack-exhaustion issue, propagated through
  micromatch/fast-glob/Next's lint plugin/config. See
  [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm).
  Registry latest braces is 3.0.3, still affected; no forced downgrade to Next 14
  was applied. These packages are absent from the production dependency audit.
  Lint inputs/globs are repository-controlled, not user service input. Read-only,
  secret-free CI and its timeout bound exposure; this is not an upstream fix.
  ESLint is pinned to the latest 9.x patch (9.39.5) allowed by eslint-plugin-react's
  published peer range; ESLint 9 is out of support. ESLint 10 is deferred until
  the official Next lint dependency stack declares compatibility. Maintainer
  acceptance or remediation of this tooling debt is an explicit merge gate.

Two defects were caught during iteration: native dialog Tab could advance to
browser chrome (fixed with explicit wrapping), and the test's generic alert
locator also matched Next's route announcer (scoped the assertion to `main`).
All results above refer to reruns after those corrections.

## CI, security and remaining gates

`M8 Web Foundation` runs on relevant PRs to dev/main and relevant dev/main pushes.
There is no duplicate feature-push run. It installs the exact app lock, lints,
tests, builds, typechecks and runs Chromium on Ubuntu 24.04 / Node 22.22.0;
reports/screenshots are retained seven days. It has read-only repository
permissions and no secrets, crypto jobs or chain operations. Existing workflows
are unmodified; M5's expensive acceptance path filter does not match this PR.
CI outcome is reported on the PR, not asserted in advance in this document.

No runtime security finding was observed in this bounded, disconnected UI.
This is not a production authentication/access-control implementation. No private
data was supplied to it. No `Verified` or `Finalized` badge can be selected from
the current badge type. No keys, shares, proofs, transaction credentials or
participant fixtures are included. Existing threat-model limitations are unchanged.
Headers set no-referrer, nosniff, frame DENY and disable camera/microphone/location.
Production TLS, CSP/nonces, authentication, authorized API integration and a full
security/accessibility review belong to later deployment/integration work.

Acceptance: foundation starts, components/routes and three layouts work, targeted
local tests pass, no fake cryptography/backend, PR2–7 remain separate. Visual
comparison is partial with the precise reference limitations above. Ready for
technical and design review; **not automatic merge approval**. CI and human
product/design/security review, including the development-tooling debt above,
must be accepted before a maintainer merges into dev.
