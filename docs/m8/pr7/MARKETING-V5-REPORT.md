# KRYPTROOM M8 — MARKETING V5 DESKTOP DESIGN & QA REPORT

Date: 2026-10-30, America/Toronto. PR [#20](https://github.com/e-sall/KryptRoom/pull/20), existing `feat/m8-responsive-accessibility-final-qa` branch. Starting HEAD `85fc1f6541e07ff71a52a4416a3717ae8866d561`. Final published SHA, exact-head CI and executed test ledger are maintained in the PR body. No merge authorization is implied.

## Desktop scale audit

Measured in actual Chromium CSS viewports, DPR 1, visualViewport.scale 1. No browser zoom alteration, global CSS zoom, page scale transform, essential clipping or artificial 100vh section. Measurements and matched screenshots at 1366×768, 1440×900, 1536×864, 1600×900 and 1920×1080. Founder physical-screen/CSS viewport cannot be inferred reliably from the provided reference image, so no claim of matching a personal device is made.

| Composition at 1366×768 | V4 height (px) | V5 height (px) |
|---|---:|---:|
| .marketing-navbar | 74.0 | 58.0 |
| .home-hero | 469.4 | 422.4 |
| .home-showcase | 745.6 | 696.7 |
| .how-it-works | 1313.4 | 574.4 |
| .founder-scene | 633.3 | 400.0 |
| .home-final-cta | 483.7 | 294.4 |
| product hero | 515.1 | 350.6 |
| technology hero | 436.8 | 306.6 |
| security hero | 436.8 | 248.3 |
| developers hero | 279.3 | 228.6 |

At 1366 the content width changes from 1286 to 1160 px; hero type from 86 to 68 px. Navbar height 58 px, body 15–16 px and section headings 42–44 px form a shared desktop scale. How It Works changes structure rather than simply shrinking type: heading and four short editorial controls occupy the left column, a restrained Room/participants/input/operation visualization occupies the right. Supplemental detail remains in the active explanation; mobile layouts retain the existing vertical presentation. The complete section and showcase frame are checked below the real navbar at the smallest desktop viewport.

V5 styles explicitly outrank the older homepage imports; an initial screenshot review caught this cascade conflict before acceptance. No zoom trick is used. Showcase reduction is more modest than How/founder/CTA because all state labels and context remain readable and later scenes add meaningful information. Founder remains the final authority on whether the resulting density is sufficient.

## Motion and product demonstration

Cycle 23.6 seconds instead of 42: dwell times 2.6 / 2.8 / 3.2 / 3.6 / 3.8 / 4.0 / 3.6 seconds. A scene-dependent timeout is cleared synchronously with suspension. Pause/resume/replay, offscreen/page-hidden suspension, reduced motion and static fallback remain covered by browser tests. `/demo` P05 is unchanged. Open full demo is removed from the homepage showcase; the footer retains the route.

Private computation and S2/S3 use the same 47% branch-axis constraint, with real center differences asserted below 1 CSS pixel. Exact existing graph edges and ordered parents are unchanged. Scene 5 adds a synthetic policy-gate/permitted-output card with no disclosed value. Scene 6 separates commitment, Not assessed proof and Not anchored status. Scene 7 becomes an S4 inspection card naming ordered [S2, S3] and protected artifacts. Reserved context space prevents layout shifts. These are illustrations, never real authorization, execution telemetry, values, verification or chain finality.

The new How SVG represents the shared Room, then independent participants, protected local inputs and the private-operation/RoomState stage. A real React hydration mismatch caused by multiple title text children was diagnosed in a local development build and fixed by rendering one title string. A labeled illustration wrapper was assigned its proper group role after Axe identified it. No runtime error or accessibility assertion was suppressed.

## Pages and controls

- Canonical K stays at the left. Compact Solutions uses a real rotating SVG chevron and four short industry names, preserving native disclosure, Escape/focus, touch and no-JS behavior.
- Hero preserves the tagline and two destinations, with a small **Incoming Quantum Computing Layer · Planned R&D** marker. No operational quantum/QPU/advantage/security claim.
- Why stays independent and static; technical foundation remains combined. Marketing actions use horizontal arrows.
- Founder preserves original bytes, responsive quality-92 delivery, crop, biography and desktop vertical alignment. Icon-only LinkedIn and GitHub have accessible names and 44 px targets. The public [e-sall profile](https://github.com/e-sall) explicitly identifies Elimane and KryptRoom; no guessed social profile.
- Final CTA is smaller and retains one Book a Demo action. A pointer-positioned soft halo and subtle dot field paint inside the surface, without text/button movement or heavy canvas/video. Keyboard focus remains visible; reduced motion disables pointer tracking.
- Product, Technology and Security remove redundant pre-headings, expose semantic editorial h1s and reduce title/row/visual spacing. Technical scope and operational limitations remain intact. Technology highlights planned-only quantum research.
- Developers gains a compact hero and real Architecture, Security and milestone documentation destinations. No SDK or API is invented. Four sector pages share the more compact editorial scale and preserve proposed-use/synthetic/maturity boundaries.
- Booking remains Coming soon with the exact founder-authorized email link, no form, calendar, availability or reservation service.

## Evidence and validation

Final local executions: **112 units, 157 Chromium passes plus two inherited exclusions,
30 Windows WebKit passes, 31 classifier tests, lint zero warnings, production build
and typecheck: PASS**. Browser suites used two local workers to avoid observed
CPU contention; no timeout or assertion relaxation. Exact-head hosted results
are recorded separately in PR20.

Supplementary V4 combined-technical-section captures were recovered from an
isolated archive of the exact starting SHA. This baseline-only build used Next’s
supported webpack backend because Turbopack rejects the temporary dependency
junction outside its isolated root. V5 and CI retain Turbopack unchanged. Other
V4 metrics/screenshots were captured before editing the running V4 build.


[Matched screenshot gallery](marketing-v5/README.md), [V4 metrics](marketing-v5/before-measurements.json), [V5 metrics](marketing-v5/after-measurements.json). Before images are the actual starting V4 build, not regenerated from V5. Five desktop sizes, matched sections and scenes 4–7, internal pages, founder, CTA and dropdown are captured. Screenshots were actually inspected; numbers alone do not establish aesthetic approval. Mobile/tablet checks are regression coverage, not founder aesthetic approval or an expanded redesign campaign.

Preserve baseline 112 units, 151 Chromium passes, 30 local WebKit and 31 classifier tests. Two V5 cases across three browser profiles add six Chromium executions for a target 157 passes plus the two inherited exclusions. Exact final executed outcomes and hosted workflows are recorded in PR20, not inferred from older commits. Original strict frame, scene-height, privacy/request, keyboard and Axe assertions remain. Existing tests change destinations/headings/timing only where expressly superseded by the founder directive. No skips or relaxed tolerances were added. No heavy cryptographic integration is requested by this frontend/docs diff.

## Security disposition

M8-SEC-001 remains ESLint 9 EOL development tooling only, owner e-sall. Expiry **2026-11-01 23:59 America/Toronto**, mandatory review before PR20 merge or expiration, whichever first. No renewal, broader risk acceptance or production deployment approval.

On October 30, official [support policy](https://eslint.org/version-support/) still marks 9 EOL; official React 7.37.5, JSX-a11y 6.10.2 and import 2.32.0 peers still exclude ESLint 10. No forced install or unsupported peer override. [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) remains withdrawn. Full and production npm audit results are saved outside Git during execution; their counts and final hosted clean-install result are reported in PR20. No new material security issue observed. Zero findings do not restore ESLint support.

M1–M7, protocols, fixtures, historical evidence, dependency pins/lock, CI and runtime security configuration remain unchanged. No Groth16, blockchain transaction, deployment, release tag, main change, merge or M9. Dev remains `8e8d8349db565278a866bd82f743f03fd1ee8c35`; main remains `1715b504e2041127056127ab5236a3248195a234` pending final recheck.

## Founder preview and verdict boundary

Current local production candidate: http://127.0.0.1:3002/ . Restart from the existing PR20 branch, verify HEAD against PR20 and a clean tree, then `npm run start -- --port 3002` in `apps/web`. A fresh checkout needs the pinned clean install and production build first. No public deployment.

The candidate may be **READY FOR FOUNDER DESKTOP VISUAL REVIEW** only when the exact published HEAD checks pass. Otherwise CHANGES REQUIRED or BLOCKED — CI / SECURITY applies. No M8 completion or visual approval is declared. Remaining limits: mobile/tablet await founder review, Windows WebKit is not Safari/real-device certification, no Firefox execution claimed, early scenes preserve stable reserved space and the film remains synthetic.
