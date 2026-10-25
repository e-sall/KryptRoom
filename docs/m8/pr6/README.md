# KRYPTROOM M8 — PR6 IMPLEMENTATION REPORT

## Scope, base and delivery

Base verified on GitHub: merged PR #18, `dev`
`b2459744ef9b10971a8e95a9abb2da26f4b75d6e`. PRs #14–#18 are merged.
Branch: `feat/m8-marketing-interactive-demo`. Delivery is a PR to dev, left open
for independent review. Main baseline is
`1715b504e2041127056127ab5236a3248195a234`; neither main nor dev is updated.
The exact final publication SHA, PR URL and CI run identities are recorded in
the PR delivery description, avoiding a self-referential commit hash here.

This is a presentation milestone, not new cryptographic validation. PR7 is not
started. No public deployment, Groth16, blockchain transaction or real booking.

## Audit and canonical sources

Read repository instructions, project context, architecture, security/threat
model, ADRs, PR1–PR5 evidence, Engineering Contracts, Design Traceability,
Marketing Experience, Demo Specification, motion/responsive guidance and the
supplied original P01/P02/P05/P11 plus portable conversion. Existing production
routes and placeholder services establish no operational frontend adapter.

Paths below are relative to the supplied
`KryptRoom-M8-Source-Consolidation`, retained unchanged outside the checkout.
SHA-256 identifies exact original bytes, not a runtime proof:

- P01 `original-sources/P01-Marketing-Hero/chat-message-1.txt`:
  `9afeec9e672a6fc6c37bacfdfa0aad8063705edad9dff5779d9c7b19bf3ab67f`.
- P02 `original-sources/P02-How-It-Works/uploaded-original.svg`:
  `994902af3232ac5be55d5f97808996e506e76850da4c6bbf2fe3ad4365e6d5b3`.
- P05 `original-sources/P05-Interactive-Demo/chat-message-1.txt`:
  `2bae8b7848f5bc92e0f0a8d42597b77324b51e9f74dd3ff6769d8a747d921127`.
  Its actual heading is **Prototype 5 — Demo Experience · V1 restaurée**,
  explicitly rejecting V1.2 and restoring proportions/left rail.
- P11 `original-sources/P11-Responsive-Polish/chat-message-1.txt`:
  `833f9597342464eaf789f368b3f066609719d6db7715630eb3aa3dbafb486d4e`.
- Supporting `portable-viewer/P05-Interactive-Demo.jsx`:
  `05a10453f2284c38845c84052f0c4a7eb60a19851b1f0de50fce5bd8c3c24431`.

The recovered P05 DIL still contains an older thick, light-upper-arm K.
`P05-LOGO-ADAPTATION.md` explicitly describes the conversion's replacement;
that conversion is not an independently recovered final corrected original.
The current founder instruction and later P11 geometry establish the approved
thin light-stem/two-gray-arm mark. The application's already canonical
`components/k-logo.tsx` is reused unchanged. There is no claim that a missing
post-correction full DIL was recovered or that the old portable runtime ran.

## Original, conversion and application distinctions

- Original P05: viewBox 1040×620; three widths 231/493/248; scene index 3;
  presentation false; seven scenes; bounded Previous/Next and numeric seeking;
  Presentation changes explanatory labels without column movement. No autoplay,
  fullscreen, timer or automatic scene progression is present.
- Conversion: DIL state syntax becomes React state, wrappers become portable
  components, and the mark is adapted as documented. Its static SVG captures
  below are rendered with the project's React server renderer, selecting each
  initial scene and mode in a temporary harness. Original files are untouched.
  These images do **not** certify interactive fidelity of that old runtime.
- Application: actual Next production build, semantic HTML buttons/text and
  decorative SVG paths. Desktop retains the exact relative column widths and
  stable height across modes. Tablet uses rail + visualization with context
  below; mobile stacks all three. Source-absent keyboard navigation, clickable
  left scene labels, reset and state inspection meet the mission/contracts.
  Default is scene 04; Restart returns to scene 01 and Explore. Mode changes
  preserve the current scene and selected state. All behavior is tested.
- P05's generic S2/S3 operation labels become the existing PR3 labels. S4 keeps
  ordered parents [S2, S3]. Four paths represent S1→S2, S1→S3, S2→S4, S3→S4;
  the mobile rendering uses those same four edges, not a linear chain.
- Source dimmed future stages become visibility-hidden reserved areas, avoiding
  illegible text while preserving layout. The S4 parent label uses primary text
  for contrast. Progressive explanation and context scrolling preserve readable
  metadata and keyboard-reachable links without resizing the desktop columns.
- Original P02 has four conceptual labels (Protected collaboration,
  Cryptographic layers, Network, Persistent state). The explicit PR6 mission
  takes precedence: Create Room, Invite Participants, Connect Data, Run
  Computation. The layered/network diagram motif remains; copy distinguishes
  encrypted computation from at-rest encryption. Desktop reversible scroll
  selection and a bounded local mouse perturbation implement the handoff;
  the supplied static SVG does not prove those original interactions.
  Touch/direct selection works without hover; reduced motion disables scroll
  selection/perturbation while keeping all explanations available.
- P01 keeps its tagline, restrained hero and canonical K. Explore Product now
  leads to the real interactive /demo, rather than unavailable production.
  Additional explanation uses existing surfaces/tokens; no design-system rewrite.

## Seven scene results and navigation

1. Organizations: fictional A/B, separate environments and shared goal.
2. Protected Inputs: abstract input paths; no records, identifiers or shares.
3. Private Computation: conceptual operation, never an executing job.
4. State Creation: existing synthetic S4 and true branched ordered lineage.
5. Authorized Result: output concept only; no value or permission is granted.
6. Proof & Provenance: Not assessed / Not anchored; progressive explanation
   distinguishes Layer A inclusion/finality, B document consistency, C explicit
   proof verification. No historical proof is attributed to the scene.
7. Explore the State: inspect existing S1–S4 metadata and ordered parents;
   valid exact-state links into PR3 Graph and PR5 Provenance preserve context.

Both navigation bars support direct selection and Arrow/Home/End keys with
focus movement. Previous/Next are disabled at their respective bounds. Native
buttons support keyboard and touch. Scene and mode changes are deterministic,
ephemeral and independent of the Rooms draft provider.

Marketing navigation covers Product, Technology, Security, Developers and Demo.
Book a Demo explains unavailable scheduling, offers the self-guided demo and
collects nothing. There is no provider, invented calendar URL or confirmation.
Product explicitly separates Interactive Product Preview, Verified Cryptographic
Core (bounded fixtures) and future Integrated Operational Product. The technical
pages retain semi-honest/trusted-host, bounded FHE/proof and unaudited-product
limitations; there is no general compliance or medical suitability claim.

## Traceability

The supplied Design Traceability matrix remains an immutable reference.
This implementation mapping supplements it:

- KR-DES/INT/ACC-001–004: existing hero/Brand/KLogo, marketing shell and CTA;
  existing foundation tests plus new marketing tests and hero captures.
- 005–007: HowItWorks four steps, layered/network/state SVG, reversible desktop
  scroll and local pointer effect; static text fallback, SVG title/description.
- 016: seven immutable scene descriptions, initial/reset state, bounded controls,
  direct seeking and keyboard tests in marketing unit/browser suites.
- 017: DemoDiagram imports existing graph fixture/model; multi-parent paths,
  S4 context and exact-state links; catalog immutability and browser assertions.
- 018: shared grid with 231:493:248 desktop proportions; bounding-box equality
  across modes, selected S2 retained; responsive screenshots.
- 019: no I/O/core imports or fake verification; runtime request, socket, cookie
  and storage guards plus existing frontend source-boundary tests.
- 039–043: existing P11 workspace regression retained; responsive marketing
  adaptations validated at 1440, 834, 390 and 320. PR7 consolidation remains future.
- 044: honest unavailable booking fallback, no provider or slots; tested route
  and absence of form/input/iframe. Provider-backed booking is not implemented.

## Captures

All `app-*` images come from the actual production browser tests, not a mockup.
Full-page captures can be taller than the viewport; widths remain the tested
1440/834/390/320. P02 is a document-coordinate section capture to avoid the
sticky header covering its heading during automated element scrolling.

- Source P02 SVG, rendered unchanged: [original](original-p02.png).
- P01 conversion: [reference](converted-p01.png);
  app [desktop](app-hero-desktop.png), [tablet](app-hero-tablet.png),
  [mobile](app-hero-mobile.png), [320 full page](app-home-320.png).
- P02 application: [desktop](app-how-it-works-desktop.png),
  [tablet](app-how-it-works-tablet.png), [mobile](app-how-it-works-mobile.png).
- P05 conversion scenes:
  [01](converted-p05-scene-1.png), [02](converted-p05-scene-2.png),
  [03](converted-p05-scene-3.png), [04](converted-p05-scene-4.png),
  [05](converted-p05-scene-5.png), [06](converted-p05-scene-6.png),
  [07](converted-p05-scene-7.png), [Presentation](converted-p05-presentation.png).
- P05 executed desktop scenes:
  [01](app-demo-scene-1-desktop.png), [02](app-demo-scene-2-desktop.png),
  [03](app-demo-scene-3-desktop.png), [04](app-demo-scene-4-desktop.png),
  [05](app-demo-scene-5-desktop.png), [06](app-demo-scene-6-desktop.png),
  [07](app-demo-scene-7-desktop.png).
- Final scene [tablet](app-demo-scene-7-tablet.png),
  [mobile](app-demo-scene-7-mobile.png); selected S2 Presentation
  [desktop](app-presentation-s2-desktop.png),
  [tablet](app-presentation-s2-tablet.png), [mobile](app-presentation-s2-mobile.png).
- Small mobile [Presentation S4](app-demo-320-presentation.png),
  [selected S3](app-demo-320-selected-s3.png).

## Local validation

- Lint, TypeScript and production build: PASS; 68 generated pages.
- Full unit/component suite: **104 PASS** (90 prior +14 new).
- Full production-browser PR1–PR6 suite: **100 PASS, 2 inherited skips**
  (85 prior +15 new). The two non-mobile inspector-sheet skips are unchanged.
- 15 targeted marketing browser cases cover all three viewport projects plus
  explicit 320px, all scenes, modes/geometry, keyboard focus, touch, reduced
  motion, navigation and context continuity.
- Axe WCAG 2 A/AA and 2.1 AA tagged rules: zero violations in checked routes
  and scenes; horizontal-overflow checks pass. This is not WCAG certification,
  a manual screen-reader audit or cross-browser certification.
- Unchanged CI scope suite: **31 PASS**. No fixture generator was run.
- No request outside local Next GET assets/routes, business API, RPC, prover,
  WebSocket, cookies or browser storage during marketing journeys.
- Initial validation found an SVG description association issue and insufficient
  S4 parent-label contrast (4.34:1). Both were corrected; original tests were
  neither removed nor weakened. The source test guards still cover all src.

Remote workflow outcomes must be read on the exact published HEAD. Existing
frontend-only classification is preserved: fast contract/privacy/reproducibility
checks stay active; heavy MPC/FHE and Groth16 acceptance skips are expected and
must not be described as fresh cryptographic executions.

## Inventory, invariants and remaining work

Changed application files: homepage, marketing section route, marketing shell.
Added `features/marketing/`: demo-model, demo-diagram, interactive-demo,
how-it-works, product-boundary, marketing-pages and marketing.css.
Added unit/browser marketing tests. Documentation: this report/captures,
ADR-021, project context, architecture, changelog and TODO.

Unchanged: M1–M7 code/protocols, node/runtime configuration, package manifests and
locks, CI/classifier, M5/M7 generators and fixtures, Solidity, all historical
proof/anchor artifacts, canonical K/tokens and PR3–PR5 presentation catalogs.
No synthetic StateProof descriptor is claimed to satisfy Layer C. No computation
or reveal decision is made by the browser. No new license.

**M8-SEC-001 stays open**, with the same dev-tooling limitation and mandatory
reevaluation **before PR7 or 2026-11-21, whichever comes first**. No dependency
upgrade/downgrade, exception renewal or wider input exposure is introduced.
Booking, authentication, authorized metadata adapters and operational execution
remain unavailable. P11 cross-browser/manual accessibility consolidation belongs
to PR7; it is not started here.

Verdict after final-head green CI: **READY FOR INDEPENDENT REVIEW**, not permission
to merge and not pixel-perfect or cryptographic certification. Reviewers should
assess the explicitly documented source-to-HTML/responsive adaptations.
