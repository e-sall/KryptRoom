# KRYPTROOM M8 — MARKETING V7.1 FOUNDER CORRECTIONS & DESKTOP QA

> Superseded locally by the founder-directed [V7.2 corrections](MARKETING-V72-REPORT.md): How now uses natural document scrolling and direct selection only. V7.1 gesture-lock results remain historical evidence.

2026-10-31, America/Toronto. Local V7.1 corrections on `feat/m8-responsive-accessibility-final-qa`, starting/published HEAD `56b9a883977c8899b564e3e97ad6e82b70670a39`. Work remains uncommitted; no push, merge, deployment, release or M9. PR20 has no newly published V7.1 HEAD or CI result. Founder visual approval remains required.

## Implemented corrections

- Quantum: centered baseline group with 10px gap; infrastructure and Planned R&D share canonical neutral color, only the incoming-layer text is blue. Desktop computed rectangles and colors are tested.
- Secondary links: 13px visible type, no decorative lower border or permanent underline, including hover. Click areas and existing visible keyboard focus remain. Actual computed styles and close-up captures verify the result.
- How: removed the wrapper's actual `border-top` in home.css; the panel border is preserved.
- Technology: its narrative column now aligns to the top, placing the label within the top padding rather than vertically centering the entire block. The graph's states, geometry and ordered parents remain intact.
- Founder: moved the label into the narrative column immediately before the title. Photograph, biography, dimensions and 16px social icons remain unchanged.
- CTA: retained the original static points, restrained graph and halo. Removed the additional permanent pattern. A deterministic original SVG layer of glyphs/nodes appears through a radial mask at the pointer; opacity fades on exit. It adds no transaction/proof status. Reduced motion disables this extra layer. Title/button geometry stays fixed.
- R&D: one paragraph with the requested connected copy and uniform body typography; removed only the following FAQ's decorative top divider, preserving the card border.

## How scroll mechanism and measured evidence

The retired V6 implementation interpolated phases over a short document track. It allowed continued page movement, and the external sticky label could overlap the navbar. The initial V7 local draft introduced bounded gesture capture; V7.1 makes rearming explicit and removes the remaining wrapper separator.

The controller captures wheel intentions only near this section, at desktop widths where the entire panel fits under the actual navbar rectangle plus 24px. Crossing its entrance pins the document at that coordinate and selects Create Room. Four indexed states are deterministic. A minimum 600ms viewing interval and 180ms quiet interval prevent one inertial burst from skipping acts. Small deltas accumulate to 45px. No timer advances a phase. Subsequent distinct gestures select Invite Participants, Connect Data and Run Computation; the following gesture releases native scrolling. Reverse traversal enters at the fourth step and exits above the first. Body overflow is never disabled.

Direct buttons, explicit Technology exit, Escape, Tab, Home/End, anchor/history navigation, resize, hidden-page and reduced-motion changes release capture. Native touch remains available. Listeners are removed when the section leaves the observer region and on unmount. If browser enhancement APIs are unavailable, direct buttons continue working.

The tests use actual browser wheel events and record scrollY, panel/navbar rectangles and the next section. All four phases must have **identical scrollY**, the complete panel must fit below the navbar and within 768px, and Technology must remain below the panel before release. They then verify native movement, reverse phases and exit. Small-delta bursts, immediate large duplicate events, PageUp/PageDown, explicit selection, Escape, reduced motion, resize, anchors, reload and history are also covered. These are automated input checks, not physical Windows mouse/trackpad hardware certification. No video was recorded.

## Evidence and validation

[Gallery](marketing-v71/README.md) contains actual desktop captures at 1366×768 and 1440×900, with additional hero/geometry checks at 1536×864 and 1920×1080. Zoom is 100%; no scale reduction is used. Included: hero, Why, close-up link, Technology, Founder, R&D, four How phases, release/reverse, CTA at rest/four pointer positions/after exit. WebKit captures are stored separately. [Before V7 captures](marketing-v7/local-preview/) and earlier V6 gallery remain historical evidence.

- Lint and typecheck passed after the application corrections.
- 112 unit/component tests passed. The first run found missing enhancement APIs in jsdom; the application now preserves direct-button fallback when those APIs are absent. No test assertion was disabled.
- Production build passed, 72 static pages.
- Eight targeted Chromium V7/V7.1 tests passed; the final screenshot-only refinements also passed their two affected tests.
- The broader production-server desktop run passed 25/27 initially. The two failures expected intentionally superseded V6 behavior: position-interpolated How phases and identical Explore/Presentation widths. Tests now require real gestures, wider desktop Presentation, exact Explore restoration, preserved selection and catalog edges. All five marketing.spec.ts cases then passed. Thus all 27 affected Chromium scenarios have successful results across the initial run and targeted rerun; no single all-27 green rerun is claimed.
- Final local Windows WebKit rerun: **8/8 passed**. Initial runs passed 5/8. The three failures were fractional Windows geometry: visual viewport 1366.4 vs integer innerWidth 1366 (document width rounds to 1367), and subpixel spacing. Read-only diagnostics found no element beyond the viewport. The tests now use the existing suite's ceil(visualViewport.width) method and a 0.05px spacing tolerance; no overflow is hidden. The final eight-case rerun passed; this is engine coverage, not Safari or physical-device certification.
- The diagnostic attempt to run legacy tests against dev port 3002 failed their fixed production-port/no-WebSocket boundary assertions. It was stopped and replaced with the unchanged production-test server on 3000. Those diagnostic failures are not app security failures or acceptance results.

No full 169+ Chromium suite, Firefox, physical device, assistive-technology audit or WCAG certification is claimed. New assertions and captures are concentrated on this mission. The supplied V7.1 defect descriptions were available; no additional screenshots were attached to the V7.1 message, so no unseen image is claimed inspected.

## Security and preserved boundaries

See [minimatch investigation](MINIMATCH-INVESTIGATION.md): 16 moderate propagated package findings, one advisory, two minimatch installations, zero production findings. No compatible complete remediation has been established; current parent ranges exclude patched major 11. No install, override, force, lockfile modification or automatic exception was applied. Local visual corrections are explicitly authorized despite this unresolved publication gate. M8-SEC-001 remains ESLint 9 EOL only, expires **2026-11-01 23:59 Toronto**, and is not extended.

Git diff verifies the four reserved film files are unchanged: business-story.ts, business-visual.tsx, home-showcase.tsx and commercial.css. No Prototype 12 design, new scene or timing was integrated. M1–M7, fixtures, proofs/anchors, CI, dependencies, logo and original image assets are untouched. No Groth16 or blockchain action.

Additional changed application files are home.css, home-page.tsx, refinement.css, final-cta.tsx, marketing-pages.tsx and use-how-scroll.ts. Corresponding tests are marketing-v7.spec.ts, new marketing-v71.spec.ts, marketing-v6.spec.ts and marketing.spec.ts. Previous V7 edits remain preserved. `next dev` generated apps/web/AGENTS.md and changed next-env.d.ts to its dev type paths; these generated effects are left uncommitted and documented rather than silently cleaned.

## Local preview and remaining decision

The dev server remains bound to **http://127.0.0.1:3002/**. Run from apps/web: `npm run dev -- --port 3002` using existing dependencies. It serves the uncommitted V7.1 working tree. No public service is deployed.

Desktop founder review remains outstanding, especially the physical-wheel feel and CTA subtlety. Security publication remains **BLOCKED**, requiring a reviewed compatible fix or a separate explicit founder risk disposition. This report grants neither. No commit/push/merge will follow automatically.
