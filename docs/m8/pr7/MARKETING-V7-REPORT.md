# KRYPTROOM M8 — MARKETING V7 PARALLEL BUILD & DESKTOP QA REPORT

> Later local work: founder authorized targeted investigation and independent V7.1 visual corrections. See [V7.1 current report](MARKETING-V71-REPORT.md) and [minimatch investigation](MINIMATCH-INVESTIGATION.md). This interrupted-work record is historical; its security block on publication is still unresolved.

## Disposition: BLOCKED — SECURITY / incomplete implementation

Date: 2026-10-31, America/Toronto. This is an interrupted-work record, not a completed V7 acceptance report. No founder visual approval, M8 completion, new crypto validation or merge readiness is asserted.

PR20: https://github.com/e-sall/KryptRoom/pull/20

- Existing branch: `feat/m8-responsive-accessibility-final-qa`.
- Verified remote/local starting HEAD: `56b9a883977c8899b564e3e97ad6e82b70670a39`.
- Verified dev: `8e8d8349db565278a866bd82f743f03fd1ee8c35`.
- Verified main: `1715b504e2041127056127ab5236a3248195a234`.
- PR was OPEN and mergeable at inspection. No commit, push, merge or ref update performed in V7. Working tree contains unfinished V7 edits and evidence.
- No exact-head V7 CI exists. Historical V6 results do not validate these edits.

## New security finding and stop decision

The full npm audit now reports **16 moderate affected-package entries**, all propagated from **one advisory**, [GHSA-g3hv-75wg-m249 / CVE-2026-118764](https://github.com/advisories/GHSA-g3hv-75wg-m249). GitHub records the maintainer publication on October 27 and database review/update on October 30. This differs from the previous zero-finding V6 audit.

The advisory describes excessive CPU/memory use from attacker-controlled glob preprocessing with `optimizationLevel >= 2`. Its affected range is `<11.0.1`; the documented fix is `11.0.1`. Installed development dependencies include `minimatch@10.2.6` under `@typescript-eslint/typescript-estree@8.72.0`, and `minimatch@3.1.5` under ESLint/plugins.

Production audit: **zero findings**. `npm ls minimatch braces --omit=dev --all` is empty. No runtime exposure is established. A bounded read-only search found no explicit `optimizationLevel` setting in the inspected ESLint, config-array, eslintrc, TypeScript ESTree or React/import/JSX-a11y plugin distributions. Installed minimatch 10.2.6 defaults to level 1. This is **not** an exhaustive reachability proof or a dismissal of the advisory. Repository-supplied configuration remains a separate tool/CI trust boundary. No exploit was executed.

**M8-SEC-001 only covers ESLint 9 EOL**, not this advisory. Owner remains e-sall; expiration remains **November 1, 2026 at 23:59 America/Toronto**. No extension or expanded acceptance is recorded. Founder instructions require stopping and reporting a new material risk; build/publication work was stopped pending review of this newly flagged development dependency risk.

The previous braces [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) remains withdrawn. [ESLint support policy](https://eslint.org/version-support/) still marks 9.x EOL. Current npm ESLint is 10.14.0; official React 7.37.5, JSX-a11y 6.10.2 and import 2.32.0 peers still exclude ESLint 10. No supported drop-in chain has been established.

No installation, override, force option, dependency downgrade, suppressed audit, disabled security control or changed CI scope was used. npm's suggested major downgrades are not accepted remedies. Next step requires a separate founder decision for scoped reachability/remediation review; it must not be interpreted as renewal or blanket risk acceptance.

## Preserved parallel-work boundary

Prototype 12 remains exclusively reserved to chat 05. No unapproved SVG, storyboard, timeline or DESIGN LOCK was inferred. Git diff confirms the four protected files remain byte-for-byte unchanged:

- `business-story.ts`
- `business-visual.tsx`
- `home-showcase.tsx`
- `commercial.css`

Core M1–M7, fixtures, historical proofs/anchors, CI, dependency files, original portrait and canonical logo remain untouched. No Groth16, blockchain transaction, production deployment, main update, release or M9.

## Sources and partial UI work

Read the consolidated locked visual-token JSON, current token implementation, project instructions/context, V6 report/gallery and security records. The exact `Design System.txt` and `05 - KryptRoom Product Design.txt` documents are stored in the user's ChatGPT project and inaccessible through the available tools. The founder explicitly authorized continuing with existing locked sources and recording this limitation. Future comparison against those two documents remains outstanding.

The supplied eleven screenshots were available in the conversation. The supplied 32-second MP4 decoded successfully in Chromium; sampled frames at 0, 10 and 20 seconds were inspected. The bundled Playwright FFmpeg could not decode it; no claim relies on that failed attempt. Clean homepage text was accessible; its security URL was unavailable through the web tool. Reference assets/code were not copied.

Locked values reused: background `#10100F`, surface `#191918`, elevated `#242422`, border `#343432`, text `#F1F0EB` / `#A9A9A2`, blue `#7CAAD5`, muted blue `#334B60`. V6 Why/Technology panel `#20211E` and How `#20231F` are replaced locally with canonical surface; their noncanonical borders with canonical border. Technical demo's green frame/center/inspector surfaces are replaced locally with these neutral tokens. The reserved film's original colors and inherited tokens are untouched. No missing token was invented.

Unfinished local changes include inline desktop Quantum positioning, internal Why/How/Technology labels, 13px secondary links, 16px social symbols with existing 44px hit areas, compact Solutions, spaced Developers actions, a concise R&D module, Security page index, original decorative CTA motifs and a wider technical Presentation layout.

How's draft controller uses bounded wheel capture only near the visible section on desktop when its full height fits below the navbar. It accumulates small deltas, limits gesture bursts to one step, releases at boundaries and supports reverse traversal. Direct selection, explicit Technology exit, Escape, Tab, Home/End, anchors, resize, history and reduced-motion paths remain. No body overflow lock is applied. Native touch remains unchanged. This is partially tested, not a completed cross-browser or physical-trackpad validation.

## Validation completed before the security stop

- Production build: succeeded, 72 static pages, including TypeScript build validation. One subsequent source-only lint-warning correction was not rebuilt before the stop.
- Initial lint found one unused-parameter warning in the new hook. Corrected locally, but no subsequent clean lint run is claimed.
- Initial targeted Chromium runs passed forward/reverse wheel geometry, gesture burst, direct selection, keyboard/exit, responsive fallback, desktop positioning and editorial route cases.
- New technical Presentation regression failed because its `hasText: 'S2'` selector matched both S2 and S4's parent text. This test-harness ambiguity remains unfixed at the security stop; no success is claimed for it.
- The remaining browser run was interrupted when the audit result arrived. No completed V7 unit suite, full Chromium suite, WebKit suite, final screenshot gallery or hosted CI result is claimed.
- Before screenshots were recorded at 1366×768. Initial after hero/How screenshots were visually inspected from local scratch. The hero segments align on one line and the sampled How frame fits under the navbar; these are diagnostic evidence only.
- Protected-file/core diff check passed. No general frontend regression clearance is claimed.

The owned local V7 preview was stopped at the security gate. Retain local edits and valid historical V6 evidence; do not reset or discard them. Do not resume publication or merge under the old exception. Finish the targeted tests, remaining visual review, complete gallery, integration-readiness document and exact-head CI only after the new risk is explicitly dispositioned.
