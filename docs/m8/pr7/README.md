> Current Marketing V6 candidate (2026-10-30): [commercial demo and visual QA report](MARKETING-V6-REPORT.md). Earlier reports/captures below remain historical. PR20 is open and unmerged; founder desktop visual approval is pending.

> Marketing V4 follow-up (2026-10-29): see [current implementation and visual QA](MARKETING-V4-REPORT.md). Earlier evidence below remains historical; it is not a claim of founder acceptance of V4. PR20 stays open and unmerged.

# KRYPTROOM M8 — PR7 IMPLEMENTATION REPORT

**PR20 independent review follow-up (2026-10-26):** F01–F04 targeted corrections
and the current validation/security disposition are in the
[Final Review Fix Report](REVIEW-FIX-REPORT.md). Earlier captures and results below
remain historical evidence. PR20 stays open; founder visual approval is pending.

Date: 2026-10-25, America/Toronto. Branch:
`feat/m8-responsive-accessibility-final-qa`. Base: merged PR #19 / dev
`8e8d8349db565278a866bd82f743f03fd1ee8c35` (verified again after the marketing
mission). Main remains `1715b504e2041127056127ab5236a3248195a234`.

This is a **candidate for independent review**, with no merge or release approval.
Final publication/check results are recorded against the exact head in the PR.

## Work preserved and completed

The founder's final marketing mission supersedes the older marketing priorities,
while retaining PR7 QA and the security gate. Existing uncommitted PR7 changes
were inspected and preserved. No reset, clean, discard or core rewrite.

Three observed keyboard defects were reproduced before correction:

1. A focused Room expansion control was below the fixed mobile navigation:
   bottom 793.22px vs navigation top 772.5px at 390×844. Document scroll padding
   now reserves that area. Before: [capture](before-focus-bottom-nav.png).
2. A mobile inspector remained modal after rotation to 834px, kept body scrolling
   locked, and Escape left focus on body because its trigger was hidden. The shell
   retires both mobile panels when leaving the mobile breakpoint. Dialog cleanup
   restores a visible trigger or the main region. Before: [capture](before-sheet-rotation.png).
3. Reverse keyboard navigation on the 320px homepage placed a How It Works button
   at y100.48–171.08 under a sticky header ending y175.09. Scroll padding belonged
   on the document, not the non-scrolling marketing shell. Before:
   [capture](before-marketing-focus.png).

The first two new browser regressions failed on the initial build and passed
after correction. The third was captured by a real keyboard audit and now has
forward/reverse focus coverage. Graph inspector copy that still reserved
Provenance/Activity for PR5 now describes the existing synthetic screens accurately.

A fourth regression surfaced in the complete suite: scroll-following in How It
Works could overwrite a clicked step after the browser scrolled it into view.
Manual selection now remains authoritative until a deliberate wheel/touch/scroll
key gesture. The historical click and scroll assertions are retained; the scroll
case explicitly supplies a new user gesture. No failing assertion was removed.

WebKit exposed two additional browser differences: native focus scrolling can
leave a control clipped despite scroll padding, and pointer clicks do not always
focus the modal opener. A small shared focus-visibility guard completes native
keyboard scrolling after paint, without moving pointer/tap targets; sheet openers explicitly receive focus before showModal,
so Escape restores the right control. Explicit modal Tab traversal includes links
and summaries regardless of native Tab preferences. Next links use documented
`prefetch={false}` after speculative preloads caused WebKit errors; hrefs and
client navigation remain intact. First activation may fetch a route rather than
using a speculative cache. No authorization or core behavior changes.

The marketing extension adds a dedicated homepage composition and autoplay
showcase. `/demo` and its catalogs, P05 modes, graph geometry and seven scenes
remain separate. See [MARKETING-REDESIGN-REPORT.md](MARKETING-REDESIGN-REPORT.md).

## Validation and evidence

Clean `npm@10.9.4 ci`: PASS, 454 packages added, zero audit findings. Direct pins
and lock unchanged. Local Node 24.12.0; CI uses pinned Node 22.22.0/npm 10.9.4.
Lint, full unit/component suite (**106**), production build (**68 pages**) and
typecheck pass. Two new unit cases retain all 104 baseline cases; the original
hero CTA assertion now checks both required CTA placements with the same route.

The final clean Chromium full run passes 133 cases plus the two inherited
non-mobile exclusions. An earlier host network suspension and successful unchanged
rerun are recorded transparently in Freeze QA.
WebKit has 22 successful representative cases; Firefox was blocked before launch
by Windows side-by-side configuration and is not claimed validated.

Final browser and CI totals: see [Freeze QA](FREEZE-QA-REPORT.md) and the PR's
published-head check ledger. The new suite adds complete journeys, eight-width
module coverage, nine showcase viewport sizes, focus/rotation, state clearing,
invalid routes, local destinations, autoplay, reduced motion and static fallback.
Existing test files and their assertions remain active. Two historical skips
apply only to the mobile-sheet test in desktop/tablet projects; their UI has no
mobile trigger. New resize tests cover entering/leaving those layouts in all
projects. No failure was changed into a skip.

Screenshots are real production-build browser captures, not generated mockups.
The [visual inventory](VISUAL-EVIDENCE.md) identifies the route, viewport and
reference. Images were opened for visual inspection. Captures are evidence of
appearance, not cryptographic proof, accessibility certification or founder design
approval. The comprehensive test report remains available as a CI artifact.

## Scope and security

Changed application areas: shared shell/dialog focus behavior, document focus
scroll padding, Graph guidance, homepage and its scoped marketing components/CSS.
Added optional cross-browser Playwright configuration, regression tests, portrait
asset and M8 documentation. Generated test reports remain under the existing ignored report directories.
A test-only CSS-viewport helper verifies dimensions under Windows WebKit DPI
scaling; no ESLint rule/configuration or workflow was weakened. No added
package or license; package/lock, CI/classifier, M1–M7 code, contracts, tests,
fixtures, runtime settings, historical proofs/receipts/anchor artifacts unchanged.

The [security reevaluation](PRE-PR7-SECURITY-REEVALUATION-REPORT.md) records the
founder's limited ESLint 9 EOL renewal, through **2026-11-01 23:59 Toronto**, with
reevaluation before merge or expiry. The withdrawn advisory portion is closed.
No force, audit suppression, security-control removal or wider exception.

Source/privacy guards and browser audits permit only local Next GET assets/routes,
no API/RPC/prover calls, mutation, WebSocket, cookies or browser storage. Numerical
samples and state metadata remain synthetic. No real records, matched identifiers,
joined dataset, secret shares, keys or operational authorization are accessed.
No MPC/FHE invocation, Groth16, chain transaction, deployment, M9 or main change.

## Review gate

Assess the new marketing direction aesthetically as well as technically. Read the
[Freeze QA report](FREEZE-QA-REPORT.md), [P01–P11 matrix](TRACEABILITY.md),
[debt inventory](DEBT.md) and current security decision before considering a merge.
The founder must reevaluate the exception and explicitly authorize any merge.
No M8 COMPLETED claim, release tag or production readiness is authorized here.
