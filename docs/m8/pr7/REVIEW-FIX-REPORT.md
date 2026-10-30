> Marketing V4 follow-up (2026-10-29): see [current implementation and visual QA](MARKETING-V4-REPORT.md). Earlier evidence below remains historical; it is not a claim of founder acceptance of V4. PR20 stays open and unmerged.

# KRYPTROOM M8 — PR20 FINAL REVIEW FIX REPORT

Date: 2026-10-26, America/Toronto. Follow-up to independent review of
`9ca04473b81faf65991628b110691da3223c746e`, on the existing
`feat/m8-responsive-accessibility-final-qa` branch. PR20 remains open and unmerged.
This report supersedes the previous visual-readiness assessment, not historical
test results. Final published SHA and exact-head CI outcomes are recorded in PR20.

## Targeted corrections

- **F01:** retain the floating navbar and entire product frame. At large desktop
  widths the showcase title uses one line; compact internal spacing reserves room
  for the title and full frame at 1366×768. The regression aligns the section below
  the actual navbar rectangle, then asserts that heading/title are below its bottom,
  title precedes the frame and the whole desktop frame ends inside the viewport.
  An intermediate run correctly rejected a frame 33 px below the viewport; the
  assertion was retained and the layout corrected.
- **F02:** hydrated autoplay progressively introduces protected inputs, then the
  illustrated operation, then the lineage at State Creation. Before that, the
  reserved lineage area explains the current stage. Authorized Result emphasizes
  S4, Proof & Provenance emphasizes its edges and unassessed evidence fields, and
  Explore highlights all states. Every scene displays its existing catalog note,
  including the absence of execution, disclosure, proof or chain activity. Concealed
  stages retain their dimensions and are hidden from accessibility output. Server
  output without JavaScript retains the complete static graph; reduced motion
  retains manual navigation, with autoplay disabled. Existing pause/replay,
  offscreen and document-visibility suspension are retained and exercised.
  A WebKit mobile run exposed one timer tick after the DOM announced suspension;
  timer setup/cleanup now uses a layout effect so teardown occurs in that same
  commit. The unchanged regression then passed five consecutive executions.
- **F03:** below 768 px, readable full-width ordered cards replace miniature
  positioned nodes. State headings are 14/16 px; caps and parent references are
  12 px. Essential context, scene controls and disclosure caveats are at least
  12 px. Vertical scrolling is intentional. No mobile connecting line suggests
  a false S2→S3 transition: the exact parent lists and summary preserve
  S1→S2, S1→S3, S2→S4, S3→S4, with S4 parents **[S2, S3]**. The separate persistent
  state illustration shares these readable cards and the unchanged canonical model.
  The first hosted Linux run exposed a 4 px scene-height drift: its trace shows
  all four hidden cards shrinking by exactly 1 px between Organizations and
  Protected Inputs (115.1875→114.1875 px per card), while the context height is
  unchanged. Explicit 20 px line boxes for mobile IDs/titles replace platform
  `normal` font metrics. The original <1 px scene-stability assertion is retained;
  the targeted mobile regression also checks both computed line heights.
  Exact measurements and upstream run/artifact references are preserved in
  [LINUX-HEIGHT-DIAGNOSTIC.json](review-fixes/LINUX-HEIGHT-DIAGNOSTIC.json).
- **F04:** remove only `unoptimized`, supply breakpoint-specific `sizes` and use
  the existing Next.js default local image optimizer. No Next configuration,
  dependency, CDN, remote source or security header changes. Intrinsic dimensions,
  alt text, 3:4 CSS crop, `object-fit: cover` and `50% 35%` focal position remain.
  The regression delays the optimizer response and compares reserved dimensions
  before and after decoding, checks the local request, response type/size, `srcset`
  and crop. [Next's documented responsive delivery](https://nextjs.org/docs/app/api-reference/components/image#sizes)
  is compatible with the existing server build; this is not a static-export setup.

Original portrait remains **3367×3958**, byte-for-byte SHA-256
`99c3f94ae1e61e9e53109ed533ff140aed095f43eb0cc85ad0bce91d85117160`.
No AI alteration or substitute portrait. See measured rendition widths, bytes,
crop, viewport rectangles and source fingerprints in
[OBSERVATIONS.json](review-fixes/OBSERVATIONS.json).
At DPR 1 all five measurements fetched a 384 px rendition, 13,692 bytes, rather
than the 1,900,114-byte original. These are local measured responses, not a global
performance benchmark or a guarantee of the same encoding on every client.

## Before / after inspection

Actual Chromium captures at each requested CSS viewport, at scene 7. Before files
were taken from the reviewed production build before source edits. Both sets use
the same section alignment below the floating navbar. The original review's
[overlapping 1366 capture](showcase-1366-viewport.png) is also preserved unchanged;
the new baseline framing exposes that the old full frame cannot fit below the title.
No historic evidence image was overwritten.

- 1440×900: [before viewport](review-fixes/before-1440-viewport.png),
  [after viewport](review-fixes/after-1440-viewport.png),
  [before section](review-fixes/before-1440-showcase.png),
  [after section](review-fixes/after-1440-showcase.png).
- 1366×768: [before viewport](review-fixes/before-1366-viewport.png),
  [after viewport](review-fixes/after-1366-viewport.png),
  [before section](review-fixes/before-1366-showcase.png),
  [after section](review-fixes/after-1366-showcase.png).
- 834×1112: [before viewport](review-fixes/before-834-viewport.png),
  [after viewport](review-fixes/after-834-viewport.png),
  [before section](review-fixes/before-834-showcase.png),
  [after section](review-fixes/after-834-showcase.png).
- 390×844: [before viewport](review-fixes/before-390-viewport.png),
  [after viewport](review-fixes/after-390-viewport.png),
  [before section](review-fixes/before-390-showcase.png),
  [after section](review-fixes/after-390-showcase.png).
- 320×800: [before viewport](review-fixes/before-320-viewport.png),
  [after viewport](review-fixes/after-320-viewport.png),
  [before section](review-fixes/before-320-showcase.png),
  [after section](review-fixes/after-320-showcase.png).

The [capture directory](review-fixes) additionally contains scenes 1–7 at 1440
and 320 px, and fully decoded founder sections at all five viewports. Tall section
captures show content accessible through ordinary vertical scrolling; they do not
claim that mobile content fits into one screen. Viewport captures retain the navbar.

## Validation

- Clean pinned npm 10.9.4 installation: PASS, zero findings. Initial Windows EPERM
  was a native-module lock held by the preview server; stopping that identified
  process allowed the unchanged clean-install command to succeed.
- Final-source lint (zero warnings), **106 unit/component tests**, production
  build (68 pages) and typecheck: PASS.
- Complete local Chromium before the hosted line-metrics follow-up: **145 PASS / 2 inherited justified non-mobile
  inspector exclusions**, 147 total, 3.5 minutes. Baseline 133 passes retained,
  plus four targeted cases across three profiles. No added skip or retry.
- CI classifier: **31 PASS**, unchanged. Browser request, storage, page-error,
  disclosure and production trace exclusion guards remain active.
- The initial complete WebKit follow-up produced 29 passes and the offscreen
  suspension failure described above. After the timer correction, that unchanged
  scenario passed **five consecutive WebKit mobile executions**.

- Complete local Windows WebKit before the hosted line-metrics follow-up: **30 PASS**, 2.9 minutes. All 22 baseline
  cases retained, plus four targeted cases across desktop/mobile. Chromium is
  156.0.8078.4; WebKit is the pinned Playwright 27.2 engine.
- Hosted Linux on first published `5c575b8`: 144 Chromium passes, 1 mobile
  stability failure and 2 inherited exclusions. Trace inspected and correction
  scoped to explicit mobile line boxes; unchanged stability assertion retained.
  After correction: lint, 106 unit tests, build, typecheck, **21 targeted Chromium
  passes** and 31 classifier passes. Final complete-suite and exact-head CI
  outcomes are recorded in PR20 after publication; no earlier green run is
  represented as a green hosted run of this changed head.

Exact published commit and hosted workflow/check results are maintained in PR20
to avoid creating another commit merely to embed its own SHA. No error suppression
is introduced. Final founder-review readiness requires that exact-head CI ledger
to be green; automated success is not founder visual approval.

Executed commands in `apps/web`: `npx --yes npm@10.9.4 ci`, `npm run lint`,
`npm test`, `npm run build`, `npm run typecheck`, `npm run test:e2e`, and
`npx playwright test --config=playwright.cross-browser.config.ts --project=webkit-desktop --project=webkit-mobile --workers=1`.
Classifier: `python -m unittest discover -s .github -p test_ci_scope.py` at repo root.

## Changed-file inventory

Five source/test files: `apps/web/src/features/marketing/home-page.tsx`,
`home-showcase.tsx`, `home.css` in that same directory;
`apps/web/tests/home.test.tsx` and `apps/web/tests/browser/home.spec.ts`.
Seven documentation/tracking files: `CHANGELOG.md`, `TODO.md`,
`docs/DECISIONS.md`, `docs/m8/pr1/SECURITY-EXCEPTION.md`,
`docs/m8/pr7/README.md`, `FREEZE-QA-REPORT.md` and this report.
The [review-fixes directory](review-fixes) adds **39 PNG captures** plus
`OBSERVATIONS.json`, `SECURITY-CHECKS.json` and `LINUX-HEIGHT-DIAGNOSTIC.json`:
**54 changed files** in this follow-up against the independently reviewed head.

## Security reevaluation

Rechecked 2026-10-26. Full and production npm audits report **zero findings**.
`npm ls --omit=dev braces eslint eslint-config-next` is empty (npm returns 1 for
an empty named-package selection, not an audit failure). Runtime file-trace checks
remain active in the browser suite. Lint configuration takes repository paths,
not user-supplied HTTP patterns; there is no new pattern-processing or upload API.

[GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm)
remains withdrawn on October 23 as not practically exploitable; that portion stays
closed. [ESLint's support page](https://eslint.org/version-support/) still marks v9
EOL since August 6. Current registry ESLint 10.13.0 with official Next config
16.4.3 still fails an isolated **strict** peer-resolution probe (`ERESOLVE`):
eslint-plugin-import 2.32.0 accepts only through ESLint 9; current react/jsx-a11y
plugins also exclude 10. No force, peer bypass, package downgrade or audit
suppression was applied. Installed pins and lock remain unchanged.

**M8-SEC-001 remains valid only for ESLint 9 EOL**, under the recorded explicit
founder approval, owner e-sall, expiring **2026-11-01 23:59 America/Toronto**.
Reevaluation before PR7 merge or expiration, whichever comes first; no automatic
extension. Existing read-only CI permissions, dependency isolation, restricted
credentials and security checks are unchanged. No new material issue was observed
in the executed checks; zero audit findings do not remove unknown EOL risk.
The [canonical exception](../pr1/SECURITY-EXCEPTION.md), exit criteria and bounded
monitoring remain in force. No production service deployment is authorized.

## Boundaries and remaining limitations

Only homepage presentation, corresponding tests, M8 evidence and change tracking
are changed. M1–M7, graph catalog, ordered parent relationships, cryptographic
fixtures, historical proofs/receipts/anchors, dependency pins, Next runtime security
configuration and CI scope are unchanged. No Groth16, chain transaction, deployment,
merge, main update or M9. Local optimization requests fetch only the existing public
portrait; no business API, private data or synthetic result reconstruction.

Chromium and Windows Playwright WebKit are engine checks, not Firefox, Safari,
physical-device, assistive-technology or full WCAG certification. No Firefox run
is claimed for this follow-up. Mobile deliberately uses vertical scrolling; the
reserved scene geometry can leave whitespace before State Creation. These are
synthetic explanatory scenes, not a recording of cryptographic execution.

Founder visual confirmation remains required. M8 is not declared completed.
