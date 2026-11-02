# KRYPTROOM M8 — MARKETING V4 IMPLEMENTATION & VISUAL QA REPORT

Date: 2026-10-29, America/Toronto. Existing PR [#20](https://github.com/e-sall/KryptRoom/pull/20), branch `feat/m8-responsive-accessibility-final-qa`, base `dev`.
Starting reviewed HEAD: `1ce850e91a101b6d90d20c18b02f4d53624291ef`.
The published exact HEAD, tested tree and hosted check ledger are recorded in the PR body after publication. Earlier reports remain dated historical evidence.

**Candidate verdict: READY FOR FOUNDER VISUAL REVIEW only after the exact-head checks in PR20 pass.** No aesthetic approval, merge authority or M8 completion is implied. If those checks fail, this gate is BLOCKED — CI until diagnosed and corrected.

## Delivered structure

1. Editorial hero with the unchanged tagline, dominant Book a Demo and See how it works linking to the separate explanatory section. The superseded hero disclaimer and Explore Product CTA are removed.
2. THE PRODUCT, IN MOTION, without a second heading or long introduction. Existing seven-scene catalog, exact state parents, context and full `/demo` remain.
3. WHY KRYPTROOM?, a separate two-column narrative with a static original illustration of independent boundaries and permitted joint answers.
4. How It Works, with the exact four steps, clear active state, scroll/manual control, larger type and a conceptual visualization.
5. One combined Technology & Cryptographic Foundation composition, replacing the two previous homepage sections. Persistent protected state, reuse and separate reveal authorization remain explicit.
6. Who’s Building KryptRoom, original identity/biography, sharper responsive portrait, desktop vertical centering and exact accessible founder LinkedIn link.
7. One dominant Book a Demo final CTA in an original dark/light-gradient composition.
8. Ten keyboard-accessible Questions & Answers, including proof scope, blockchain, planned quantum research, maturity and contact.
9. Footer with secondary Security, implementation evidence, demo and synthetic workspace links.

## Navigation and internal pages

The canonical K and wordmark stay **at the left inside the floating navigation**. Desktop container remains centered; Product / Technology / Solutions / Book a Demo are the primary destinations. Security, Developers and Demo remain accessible outside the primary navigation.

Native details/summary supplies a four-industry Solutions disclosure with icons, descriptions, visible focus, Tab navigation, Escape/focus restoration and close-on-focus-leave behavior. It remains usable without JavaScript. Static pages:

- `/solutions-manufacturing`: independent manufacturer/supplier overlap and permitted aggregate.
- `/solutions-healthcare`: fictional Lab A/Lab B molecular and clinical cohort analysis.
- `/solutions-finance`: fictional institutional exposure comparison.
- `/solutions-research`: repeatable analysis across independent research environments.

Every scenario identifies problem, participants, sensitive data, proposed workflow, authorized output and maturity limitations. They are proposed uses, not customers or deployed integrations. The validated two-party boundary and absent dynamic membership remain clear.

Product now follows Room/Participants, Protected Inputs, private operations, immutable RoomState, Results, Proofs/Provenance and Activity through an illustrative experience. It reuses the canonical display graph and links to the existing synthetic workspace and full demo. A real visual-review defect (missing shared graph CSS on this route) was corrected and is guarded by actual SVG paint/noncolliding-card assertions.

Technology contains eight numbered sections, a sticky desktop in-page index, precise trust/operational limits, technical FAQ and CTA. Security shares the same explanatory source for overlapping claims, retains its route, and links back to the complete model. Incoming Quantum Computing Layer is explicitly **Planned Research & Development**, with no operational integration, quantum advantage or proven quantum-security claim.

`/book-demo` states **Coming soon**, offers the exact founder-authorized `mailto:elimanesall.eng@gmail.com?subject=KryptRoom%20-%20Demo%20Inquiry`, and invents no booking backend, availability or confirmation. The link opens the visitor’s email application; the site collects nothing.

## Typography, spacing and assets

Marketing-scoped aliases use self-hosted OFL Newsreader and DM Sans, with central title/spacing scales and WOFF2 preloads. Application design tokens and the canonical logo geometry are unchanged. The two font files total 168,932 bytes; font-only license notices and immutable downloaded-asset SHA-256 values are retained in [asset provenance](marketing-v4/ASSET-PROVENANCE.json). This does not add a project license. No remote font or new package is needed at runtime.

Off-white links, consistent arrows, neutral rules and hover/focus indicators replace the old blue underlined marketing links. Visible V4 marketing prose contains no em dash. Hero, narrative, portrait, CTA and FAQ spacing have been adjusted as a coherent marketing system.

The original portrait remains 1,900,114 bytes, SHA-256 `99c3f94ae1e61e9e53109ed533ff140aed095f43eb0cc85ad0bce91d85117160`. Local Sharp resize-only WebP renditions use quality 92 at 480/768/1200 widths (42,866 / 92,704 / 202,504 bytes). A picture/source width-descriptor srcset uses accurate responsive sizes, with a local 768 fallback. The Next image wrapper keeps intrinsic dimensions; native source selection avoids a second lossy optimizer pass without changing Next’s optimizer/security configuration. Crop remains 3:4, object-fit cover, focal point 50% 35%; alt is unchanged. At 390 CSS px, measured DPR1 uses 480 (42,866 bytes), DPR2 uses 768 (92,704 bytes), both HTTP 200. No AI image alteration or original-byte replacement.

## Motion and preserved boundaries

CSS illustration uses slow orbital transitions, abstract protected-flow dots, gradual opacity/blur, staged state appearance, and lineage emphasis. It advances only presentation, without fabricated execution, output values, proof verification, network events or transactions. S1 → S2, S1 → S3 and ordered [S2, S3] → S4 remain unchanged.

Pause/resume/replay, reduced motion, offscreen/document visibility suspension and complete no-JS explanations are preserved. Decorative animations pause with the stage; reduced motion disables them. Essential content retains stable reserved geometry across all seven scenes. A decorative background label crossing the explanatory copy was removed during actual screenshot review. No new heavy animation dependency.

Mobile uses readable ordered state cards, with ordinary vertical scrolling. It does not shrink the desktop graph into miniature text. Early scenes deliberately reserve the later graph’s space to avoid layout jumps; this creates more breathing room on mobile. Desktop full-frame/title/navbar rectangles are tested at 1440×900 and 1366×768 with strict bounds and no tolerance relaxation. A measured subpixel frame overrun was fixed by reducing frame/topbar padding, not changing assertions.

## Validation and evidence

Executed on the final source build locally: **lint zero warnings, 112 unit tests,
72-page production build, typecheck, 151 Chromium passes with two inherited
exclusions, 30 WebKit passes, 31 classifier tests: PASS**. No assertion/time-limit
relaxation or new skip. Hosted exact-head outcomes are recorded separately in
PR20 after publication.


Final results are enumerated in PR20 against its exact published HEAD. Commands preserve original assertions and the two inherited justified exclusions:

```powershell
Set-Location 'C:\Users\Admin\Documents\Codex\2026-09-29\https-github-com-e-sall-kryptroom\KryptRoom-M6'
python -m unittest discover -s .github -p test_ci_scope.py
Set-Location apps/web
npm run lint
npm run test -- --maxWorkers=1
npm run build
npm run typecheck
npx playwright test
npx playwright test --config=playwright.cross-browser.config.ts --project=webkit-desktop --project=webkit-mobile
```

Local unit execution uses one worker to avoid observed machine contention timeouts; assertions and test timeouts are unchanged. CI’s normal unit command is unchanged. No failure is converted to a skip. An initial restricted Turbopack process failure was resolved by cleaning only generated `.next` and rebuilding in the normal local runtime. No source workaround or CI change.

The baseline 106 units has six new cases (112 total); the baseline 145 Chromium passes has six new profile cases (151 passes, two inherited exclusions). The unchanged classifier suite has 31 cases; local WebKit retains its 30-case suite. Final executed outcomes and exact-head CI are in the PR body, without applying earlier results to a different tree.

[Visual gallery and review instructions](marketing-v4/README.md) · [Measured browser observations](marketing-v4/OBSERVATIONS.json) · [Asset fingerprints](marketing-v4/ASSET-PROVENANCE.json) · [Security evidence](marketing-v4/SECURITY-CHECKS.json).

93 PNGs: 15 before and 78 after, including 1440×900, 1366×768, 834×1112, 390×844, 320×800; all seven scenes at desktop/mobile; every homepage section; navigation disclosure; Product/Technology/Security, all four Solutions and booking at desktop/mobile. Browser regression matrices also cover 1280×800, 1024×768, 768 px and 375 px. Captures were actually inspected; the graph-style and decorative-text defects above were found through visual inspection, not inferred from CI.

## Security

M8-SEC-001 remains **ESLint 9 EOL only**, development tooling. Owner **e-sall**. Expires **November 1, 2026, 23:59 America/Toronto** (November 2, 04:59 UTC). Reevaluation is mandatory before PR20 merge or expiration, whichever comes first. This work does not renew or broaden it and authorizes no production deployment.

Official [ESLint policy](https://eslint.org/version-support/) still marks 9 EOL. Official npm metadata for React 7.37.5, JSX-a11y 6.10.2 and import 2.32.0 excludes ESLint 10; current eslint-config-next 16.4.3 still depends on those lines. No compatible supported direct official chain is established. Earlier strict isolated ERESOLVE evidence remains historical; no forced install or new compatibility probe is represented as executed here.

[GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) remains withdrawn as of October 23. Full and production audits on the unchanged lock return zero. Braces is absent from production dependencies; production NFT files contain no lint/brace package hits. No new material risk was found. Zero findings do not eliminate the unsupported-tooling residual risk. No forced dependency, audit suppression, disabled check, broader exception or runtime security change.

## Review boundary and remaining limitations

- Local Chromium/Axe and Windows WebKit are bounded engine checks, not Firefox, physical-device, Safari or WCAG certification. No new Firefox validation is claimed.
- The product film remains an explanatory synthetic animation, not a recording of a real cryptographic execution. Mobile intentionally scrolls and reserves stage space.
- Four industries are illustrative; production identity, multi-company coordination, connectors, orchestration, key management and connected UI execution remain absent.
- Original assets/text are KryptRoom’s; the supplied Clean reference informs composition only. No proprietary Clean asset, text or distinctive identity was copied.
- M1–M7, canonical fixtures, historical proofs/anchors, canonical demo catalog, dependency pins/lock, CI scope and runtime security configuration remain unchanged. No Groth16, blockchain transaction, deployment, tag, dev/main merge or M9.
- Dev remains `8e8d8349db565278a866bd82f743f03fd1ee8c35`; main remains `1715b504e2041127056127ab5236a3248195a234` at this review. PR20 stays OPEN and UNMERGED. Founder visual approval remains pending.

## Founder preview

The current PR20 production preview is local at [http://127.0.0.1:3002/](http://127.0.0.1:3002/). To restart it, select the existing branch, verify HEAD against the PR body and a clean tree, then run `npm run start -- --port 3002` from `apps/web`. This serves the already-built local candidate, not dev. A fresh checkout requires the pinned npm 10.9.4 clean install and `npm run build` first; no public deployment is performed.

Compute together. Reveal nothing.
