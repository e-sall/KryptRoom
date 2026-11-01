# KRYPTROOM M8 — MARKETING V7.2 PRECISION VISUAL QA REPORT

2026-11-01, America/Toronto. Publication follow-up: the founder separately approved
[M8-SEC-002](M8-SEC-002.md) for trusted-source V7.2 development/build validation
and PR20 publication only. The historical blocked disposition below is superseded
for that exact scope; minimatch remains unresolved. No merge/deployment authority.
The [publication report](V72-PUBLICATION-REPORT.md) records current validation;
final published SHA and hosted results are maintained in PR20 to avoid a
self-referential commit. M8-SEC-001's earlier deadline is unchanged.

2026-11-01, America/Toronto. Existing branch `feat/m8-responsive-accessibility-final-qa`; published HEAD remains `56b9a883977c8899b564e3e97ad6e82b70670a39`. All V7/V7.1 work is preserved locally. No commit, push, merge, deployment, Groth16 or blockchain action. These results cover the local working tree, not new hosted CI.

## Six corrections

1. Hero positioning is now a content-sized inline-flex group with baseline alignment and **6px** separation. Infrastructure and Planned R&D remain canonical neutral, incoming-layer text remains KryptRoom blue. Real rectangles verify 5–7px separation, one line and no overflow at 1366×768, 1440×900 and 1536×864.
2. Why's label is raised **8px** through its margin. Its lower margin increases by the same amount, preserving title/paragraph positions and frame height. No transform or title-size change.
3. How no longer imports or ships the wheel controller. No wheel interception, scroll-position progression, timer, observation listener or body scroll lock remains in this component. React selection alone controls the same four steps and visual. Buttons work with click/Enter and retain focus, aria-current and live caption. Native document scroll leaves the selected step unchanged; reduced motion remains supported.
4. Technology uses two structural grid rows in its narrative: the label stays at top, the editorial group centers in the remaining height. Graph, parent references, right column, copy, title scale and frame remain unchanged.
5. Founder uses shared grid/subgrid rows to align the left label's top with Elimane Sall's heading, within **3px** in browser tests. A 6px discrepancy caused by different parent/subgrid row gaps was fixed by making those row gaps consistently zero. Column widths, image bytes/crop, biography and icons are preserved.
6. CTA retains the static background and existing halo. The radial reveal grows from 210 to **260px**; interactive SVG opacity is **1**, glyph opacity **.95**, font 14px and stroke 1.2. Previously a higher-specificity rule silently capped the whole interactive SVG at .14. The fix scopes the stronger rule to the interactive layer only. At rest the layer stays invisible, it fades out on exit, remains behind text/button and is disabled under reduced motion. No extra animation dependency or SVG reconstruction per pointer event.

## How replacement boundary

`collaboration-steps.ts` holds the immutable four-step content independently of rendering. `HowItWorks` owns a single selected index and renders the existing diagram/caption. There are no global listeners to migrate or release. Preserve the four labels, descriptions/details, keyboard-accessible buttons, SVG title/description, ordered selection and reduced-motion/no-JS explanations when a separately approved design arrives. No new experience was designed in V7.2.

The unused V7.1 controller was removed from application source. Its historical text is preserved in `marketing-v71/retired-use-how-scroll.ts.txt`; it is not imported, built or executed. V7.1's documented scroll acceptance is historical and superseded by the explicit founder decision to restore native scrolling. Tests now assert real document movement and unchanged selected state instead of the retired lock contract. No skip or disabled assertion conceals that decision.

## Captures and tests

[V7.2 gallery](marketing-v72/README.md), compared with [V7.1 captures](marketing-v71/README.md). Actual browser captures, CSS viewport scale 1. Section crops preserve original pixel size; no zoom reduction or mockup is used. Includes hero, Why, Technology, Founder, four clicked How steps and CTA rest/top-left/center/button/right/exit at 1366 and 1440, with additional layout checks at 1536. The wider historical V7.1 evidence is retained. No new six screenshot attachments accompanied the V7.2 text, so implementation uses the precise descriptions without claiming unseen images were inspected.

- Lint: pass after removing the unused Page test import.
- Typecheck: pass.
- Unit/component suite: **112 passed**.
- Targeted V7/V7.2 Chromium suite: **5 passed**. Measures actual gap/colors/rectangles, Founder alignment, no overflow, pointer-layer opacity and fade, direct selection, reverse native wheel movement and keyboard/reduced-motion escape.
- Production build: pass, **72 static pages**.
- Film/navigation regression suite: **15 passed**, covering autoplay/pause/offscreen/reduced-motion, unchanged film geometry and data boundaries, DAG, portrait, click steps and technical demo navigation. No cryptographic suite or new CI was run.

Initial diagnostic runs of stale V7.1 tests expected the removed wheel contract and were stopped. Those tests were replaced by the new founder-approved native-scroll contract, not made permissive. An initial Founder alignment test failed at 6px; the underlying subgrid gap was corrected and the strict <3px assertion then passed. No Firefox, physical mouse/trackpad hardware, WebKit V7.2, mobile aesthetic acceptance or full WCAG certification is claimed.

## Changed files and preserved scope

V7.2 application changes: `home-page.tsx`, `how-it-works.tsx`, `refinement.css`, new `collaboration-steps.ts`, removal of unused `use-how-scroll.ts` from the local V7 draft. Tests: `marketing.spec.ts`, `marketing-v7.spec.ts`, `marketing-v71.spec.ts`. M8 report/gallery updates and historical controller text complete this delta. Preexisting V7/V7.1 edits remain uncommitted. Next dev's generated AGENTS.md and next-env.d.ts effects are preserved, not cleaned destructively.

Git checks confirm unchanged M1–M7, crypto fixtures, CI, package/lock files, public image assets and canonical brand component. The four reserved film files remain byte-for-byte unchanged: `business-story.ts`, `business-visual.tsx`, `home-showcase.tsx`, `commercial.css`. No Prototype 12 scene, timing or design was integrated. Product, Security, Developers, Solutions, R&D page, FAQ and technical demo receive no V7.2 redesign.

## Local preview and security

**http://127.0.0.1:3002/** serves the uncommitted V7.2 code using the existing installed dependencies and `npm run dev -- --port 3002`. The server is left running for founder inspection.

[Minimatch investigation](MINIMATCH-INVESTIGATION.md) remains unresolved. Last collected evidence: one GHSA, two installed minimatch versions, 16 propagated moderate package findings and zero production findings. No new audit/remediation claim is made by these UI checks. No install, lockfile change, forced dependency or added exception. Publication stays **BLOCKED — SECURITY** pending an authorized disposition.

M8-SEC-001 remains solely ESLint 9 EOL, expiring **November 1, 2026 at 23:59 America/Toronto**. That deadline is today; no renewal or broader risk acceptance is inferred. V7.2 is available for local visual review, not cleared for merge or production release.
