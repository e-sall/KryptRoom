> Marketing V4 follow-up (2026-10-29): see [current implementation and visual QA](MARKETING-V4-REPORT.md). Earlier evidence below remains historical; it is not a claim of founder acceptance of V4. PR20 stays open and unmerged.

# PR7 visual evidence and comparison

Actual production-build screenshots, captured 2026-10-25. No mockup or generated
image. Homepage widths: desktop **1440×900**, tablet **834×1112**, mobile
**390×844**. Additional showcase assertions/captures cover 1366×768,1280×800,
1024×768,768×1024,375×812,320×800. Baseline app desktop is 1440×1000.
Viewport dimensions describe CSS layout, not physical device certification.

## Every homepage section

| Section | Desktop | Tablet | Mobile |
|---|---|---|---|
| Hero | [image](home-desktop-section-1.png) | [image](home-tablet-section-1.png) | [image](home-mobile-section-1.png) |
| Autoplay showcase | [image](home-desktop-section-2.png) | [image](home-tablet-section-2.png) | [image](home-mobile-section-2.png) |
| Why KryptRoom | [image](home-desktop-section-3.png) | [image](home-tablet-section-3.png) | [image](home-mobile-section-3.png) |
| How It Works | [image](home-desktop-section-4.png) | [image](home-tablet-section-4.png) | [image](home-mobile-section-4.png) |
| Persistent State | [image](home-desktop-section-5.png) | [image](home-tablet-section-5.png) | [image](home-mobile-section-5.png) |
| Cryptographic Foundation | [image](home-desktop-section-6.png) | [image](home-tablet-section-6.png) | [image](home-mobile-section-6.png) |
| Founder | [image](home-desktop-section-7.png) | [image](home-tablet-section-7.png) | [image](home-mobile-section-7.png) |
| Final CTA | [image](home-desktop-section-8.png) | [image](home-tablet-section-8.png) | [image](home-mobile-section-8.png) |
| FAQ (last) | [image](home-desktop-section-9.png) | [image](home-tablet-section-9.png) | [image](home-mobile-section-9.png) |

First view: [desktop](home-desktop-viewport.png), [tablet](home-tablet-viewport.png),
[mobile](home-mobile-viewport.png). Product frame: [1366×768](showcase-1366-viewport.png),
[desktop](showcase-desktop-viewport.png), [tablet](showcase-tablet-viewport.png),
[mobile](showcase-mobile-viewport.png). Narrow showcase:
[320px scene 1](showcase-320-scene-1.png), [scene 4](showcase-320-scene-4.png),
[scene 7](showcase-320-scene-7.png). Full P05:
[Explore](app-demo-explore.png), [Presentation](app-demo-presentation.png).

Inspection: all section images were reviewed in a contact sheet, with individual
full-resolution inspection of hero, showcase, Why, How, persistence, technical
foundation, founder and FAQ across representative layouts. The entire desktop
product frame, including controls, measures about 572px tall at 1366px; aligned
below the navbar it occupies y110–682 in a 768px-high viewport. Mobile intentionally
uses ordinary page reflow for the complete graph and context; no inner scroll or
hidden inspector. Section clips exclude the sticky navbar when comparing section
content. Viewport images retain it and show the real scroll composition.

Long How It Works and FAQ content can span more than one desktop viewport; the
four explanations and all ten questions remain available without artificial
100vh clipping. The founder photograph has natural colors; all product visuals
are code-native and reuse the approved graph, warm neutrals and discreet blue.
Visual quality remains subject to independent founder review.

## Application and system states

- Rooms: [List](app-rooms-list.png), [Cards](app-rooms-cards.png).
- [Create Room](app-create-room.png), [Computations](app-computations.png),
  [Results](app-results.png).
- Graph: [Classic](app-graph-classic.png), [Detailed](app-graph-detailed.png),
  [Focus](app-graph-focus.png), [320px](app-graph-320.png),
  [mobile sheet](app-bottom-sheet.png).
- [Proofs](app-proofs.png), [Activity](app-activity.png).
- Display states: [Empty](state-empty.png), [Loading](state-loading.png),
  [Blocked](state-blocked.png), [Error](state-error.png),
  [Unavailable](state-unavailable.png). These are explicit display examples,
  never genuine service outcomes.

Before/after: fixed mobile nav focus [before](before-focus-bottom-nav.png) /
[after](after-focus-bottom-nav.png); sheet rotation [before](before-sheet-rotation.png)
/ [after](after-sheet-rotation.png); sticky marketing focus
[before](before-marketing-focus.png) / [after](after-marketing-focus.png).
The later click/scroll priority bug is a timing interaction reproduced by the
existing browser test; its retained assertions and documented correction provide
the regression evidence rather than a misleading static before/after claim.

## References and provenance

- Previous [PR6 source/fidelity report](../pr6/README.md), original converted
  P05 scenes and prior app captures remain unchanged. Compare
  [prior demo desktop](../pr6/app-demo-scene-7-desktop.png) to the current full
  `/demo` capture; homepage showcase is a new authorized composition.
- P11 [source-derived desktop](../pr3/reference-p11-desktop.png),
  [mobile](../pr3/reference-p11-mobile.png) versus app Graph/sheet captures above.
  These static conversion references do not certify original interaction execution.
- TryClean live site was opened and inspected as a structural reference only.
  No third-party image or proprietary asset is committed here. The [marketing
  report](MARKETING-REDESIGN-REPORT.md) records the comparison boundary and absence
  of separately accessible founder reference screenshots.

Further scenes, sizes, states, raw traces and screenshots are generated by the
full Playwright suites and retained by the unchanged CI artifact policy (7 days).
Committed selected captures remain available after that artifact expires. These
images establish no cryptographic, WCAG or production-readiness guarantee.
