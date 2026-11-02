# How It Works — viewport-fitted scroll review

> Disposition de publication actuelle : KRYPTROOM-M8-MAIN-RELEASE-READINESS.md.
> La vidéo complète est conservée hors Git, voir RELEASE-ARTIFACTS.md.


**READY FOR FOUNDER VIEWPORT REVIEW.** Local implementation only. This supersedes
the rejected tall-card architecture in HOW-SCROLL-PROGRESSION-REPORT.md.

## Corrected architecture

One compact card contains four navigation entries on the left and one persistent
SVG with only the active explanation/detail on the right. The four giant rows
and expanded descriptions have been removed. Card height is constant across states.

Only the exterior section carries scroll travel. The card sticks below the real
navbar while the native document position selects stages 01→04 and 04→01. Travel
is 422, 495, 475 and 560 CSS px respectively at the four required desktop sizes,
approximately 106–140 px per stage. It is not four viewport-height spacers.
The sticky card occupies that runway, so no blank spacer is revealed. After the
last stage the card leaves naturally and Technology follows with its normal gap.

Navbar bounds and actual innerHeight determine the sticky top and available
height: navbar.bottom +16 px, then min(600, innerHeight − top −20) px. It is not
100vh. Short viewports reduce padding, title/navigation typography and SVG height.
The panel has no internal scrolling or hidden-overflow clipping workaround.

One passive document scroll listener samples geometry through requestAnimationFrame.
There are no wheel/touchmove interceptors, preventDefault, scroll locks or scene
timers. Button/keyboard selection remains available and aligns the exterior
runway position to the requested stage. Reduced motion preserves stage changes
and removes opacity animations. Otherwise SVG transitions last 180 ms.

Below 1200 px width, the layout uses normal document flow and compact manual
step navigation, preserving the V7.2 small-screen selection behavior. The desktop
pinning/runway is not imposed on mobile. No automatic mobile-scrolling claim.

## Actual geometry and browser acceptance

Chromium and WebKit both passed the required four desktop sizes:
1366×768, 1440×900, 1536×864 and 1920×1080, checking real innerHeight.
For every stage in both directions, the card was **600 px high, top 88 px,
bottom 688 px**. At 1366×768 that leaves 80 px below the card and at least 16 px
below the navigation. The other sizes have larger bottom margins.

The tests verify all four panel bounds, exact constant height, navbar clearance,
no internal overflow, actual text Range rectangles inside the card, SVG containment,
one SVG, no page horizontal overflow, and automatic content changes through
**01→02→03→04→03→02→01**, without clicking. Each stop checks aria-current,
counter, title, explanation and SVG organizations/inputs/output opacities.
They then descend again and verify native exit to Technology, including the
normal gap after the released card. The scene changes alone cannot pass this test.

Eight focused browser scenarios validated across Chromium/WebKit, including
targeted reruns. A first reduced-motion WebKit run used its uncalibrated Windows
viewport and entered the mobile layout; calibrating actual CSS pixels fixed the
test setup. The rerun also checked the compact card at **1366×640** with reduced
motion, without card overflow. Click, Enter/Space, Tab escape, PageDown and mobile
selection/document scroll pass. No physical device/trackpad or Firefox validation.

Lint, typecheck and 14 targeted marketing unit tests pass. No full production
build, full browser matrix, GitHub CI or cryptographic validation is claimed.

## Review evidence and local URL

Open **http://127.0.0.1:3002/#how-it-works** and scroll while the full card is visible.

- Actual uninterrupted Chromium wheel recording (vidéo conservée dans l’archive locale, voir RELEASE-ARTIFACTS.md).
- [Recording geometry and state sequence](how-viewport/recording-metrics.json).
- [Real viewport/card dimensions, both engines](how-viewport/viewport-metrics.json).
- [Chromium 1366, stage 1](how-viewport/chromium-fitted-1366-step-1.png) and
  [stage 4](how-viewport/chromium-fitted-1366-step-4.png).
- [WebKit 1366, stage 1](how-viewport/webkit-fitted-1366-step-1.png) and
  [stage 4](how-viewport/webkit-fitted-1366-step-4.png).
- [All sizes and stages](how-viewport/README.md).

The video starts from the homepage and uses wheel input only. It shows the complete
card throughout the active interval, descent, reversal, second descent and exit.
No application preview controls, clicks, time seeking or screenshot assembly.

## Preservation and gate status

Local changes: How component, its refinement layout rules, browser acceptance
and documentation/evidence, atop the preserved local tree. M1–M7, fixtures, CI,
dependencies, `/demo`, logo and other V7.2 sections remain untouched. The rejected
Prototype 12 stays isolated outside the checkout; its backup is unchanged.

HEAD remains d2bc56ef55e9cadb319954a3dda4170f842039e6 on the existing PR20 branch.
No commit, push, merge, main change or deployment; no Groth16/chain operation.

At 2026-11-01 22:29:47 Toronto / 2026-11-02T03:29:47Z, M8-SEC-001 still expires
tonight at 23:59 Toronto. M8-SEC-002 expires November 4 at 02:00:41 Toronto.
minimatch remains unresolved. No exception extended or new risk acceptance;
security gates require reevaluation before any publication. This verdict concerns
the local viewport review, not merge readiness or M8 completion.
