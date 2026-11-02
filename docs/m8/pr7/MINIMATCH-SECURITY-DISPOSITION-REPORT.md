# KRYPTROOM M8 — MINIMATCH SECURITY DISPOSITION REPORT

Later founder disposition: [M8-SEC-002](M8-SEC-002.md) now explicitly authorizes
trusted-source V7.2 development/build validation and PR20 publication only for
72 hours. The technical findings below remain unresolved. This historical
recommendation is not rewritten as a fix or unrestricted acceptance.

Decision at investigation time: **BLOCKED** for publication. **No risk acceptance is granted.** A separate, tightly scoped founder exception would be required to resume publication without a complete fix. Existing safeguards reduce observed exposure; they do not make this advisory FIXED.

Investigation: November 1, 2026. Clock verified at **06:48:31 UTC** and **06:53:06 UTC**, corresponding to **01:48:31 EST** and **01:53:06 EST, America/Toronto**, after the daylight-saving fallback. Final decision clock: **06:55:12 UTC / 01:55:12 EST**. M8-SEC-001 expires **today at 23:59 EST / November 2 at 04:59 UTC**. It remains active at this decision time for **ESLint 9 EOL only**. No renewal or new exception is inferred.

## Workspace preservation

- Repository `e-sall/KryptRoom`; branch `feat/m8-responsive-accessibility-final-qa`.
- HEAD remains `56b9a883977c8899b564e3e97ad6e82b70670a39`; PR20 is not merged or published anew by this task. No remote mutation was performed.
- Before investigation, all **145 existing modified/untracked files** were saved with byte sizes and SHA-256 values in a local archive and manifest under `work/security-gate-20261101/` outside the repository. This captures V7/V7.1/V7.2 source, tests, evidence and Next-generated files without touching the running tree.
- [Final preservation check](security-disposition-20261101/preservation-check.json): **145 checked, zero changed**. Existing package.json, lockfile and installed application dependencies remain unchanged. The working tree remains intentionally dirty with V7.2 plus this new report/evidence.
- The preview continues serving **http://127.0.0.1:3002/** and returned HTTP 200 during investigation.
- Diff checks confirm M1–M7, crypto fixtures, CI, public image assets, canonical brand and the four reserved commercial-film files remain unchanged. No reset, destructive cleanup, crypto execution, transaction, deploy, merge, push or commit occurred.

## Registered installations and the 16 findings

Executed `npm ls minimatch --all`, `npm explain minimatch`, full audit and production audit. [Tree](security-disposition-20261101/npm-ls.txt), [complete parent explanations](security-disposition-20261101/npm-explain.txt), [full audit](security-disposition-20261101/audit-full.json), [production audit](security-disposition-20261101/audit-production.json).

Two npm-tracked minimatch installations:

1. **3.1.5**, `apps/web/node_modules/minimatch`. ESLint 9.39.5 directly requests `^3.1.5`; config-array 0.21.2 and eslintrc 3.3.7 also consume this shared installation. Next lint config 16.4.2 brings React 7.37.5, JSX-a11y 6.10.2 and import 2.32.0 plugins that use this legacy API.
2. **10.2.6**, `apps/web/node_modules/@typescript-eslint/typescript-estree/node_modules/minimatch`. Next lint config → typescript-eslint 8.72.0 → ESTree 8.72.0 → minimatch `^10.2.2`; parser/type-utils/utils share ESTree transitively.

The full audit reports **16 moderate affected-package entries**, **18 unique affected installation paths**, **one underlying advisory URL**, and **two actual minimatch package installations**. The [inventory](security-disposition-20261101/inventory-and-runtime.json) includes every affected package's installed version, path and dev flag. Propagated findings include ESLint and its config/utilities, Next lint config/plugin, TypeScript ESLint modules and the three plugins. They are not 16 independent vulnerabilities.

`npm audit --omit=dev`: **zero findings**. `npm ls minimatch --omit=dev --all` and the equivalent braces query are empty. These results do not account for every copy bundled inside another package; see the additional build-tool finding below.

## Conditions and concrete calls

The [official advisory](https://github.com/advisories/GHSA-g3hv-75wg-m249) remains active. It flags versions `<11.0.1` and describes amplification of glob-part arrays followed by quadratic processing when **optimizationLevel >= 2**. Version 11.0.1 is the first announced fix. The [upstream fix](https://github.com/isaacs/minimatch/commit/77a0f5c4b80bdc641c3c930a1d9edf5ad2db57f8) bounds array growth and avoids pairwise deduplication for large sets. It does not establish that all glob matching is free of availability risk.

- Installed 10.2.6 defaults to level **1**. ESTree's distributed `useProgramFromProjectService.js:244` calls its named `minimatch(filePath, pattern, {dot:true})` for `allowDefaultProject` patterns. The repository does not enable projectService/allowDefaultProject or level 2. This specific shipped call does not select the documented problematic mode.
- Installed 3.1.5 has no `optimizationLevel` or `firstPhasePreProcess` implementation. The broad advisory range nevertheless flags it. That discrepancy warrants upstream version-range clarification; this investigation does not silently remove the npm finding or declare the package generally safe.
- The React `forbid-component-props` rule invokes the legacy default function with configured property patterns; import `order` invokes it with configured path groups/pattern options; JSX-a11y helper matching uses configured component names. These are repository/tool settings, not website form values.
- No application source imports minimatch/lint tooling or accepts HTTP/upload patterns for glob evaluation. External website users have no demonstrated path to these lint calls.

### Additional bundled copy: Next build tooling

The prior npm-only analysis was incomplete. `next@16.4.2` contains embedded minimatch code in **`node_modules/next/dist/compiled/@vercel/nft/index.js`**. Its embedded glob constructs Minimatch with **`optimizationLevel:2`**; its first preprocessing routine grows the work list without the upstream limit, and its second routine performs the unbounded pairwise pass. The bundle's package.json declares the nft name but no embedded minimatch version, so no precise embedded semver is invented.

Next's `dist/build/collect-build-traces.js` imports that bundle and calls `nodeFileTrace` during build tracing. Repository source, dependency files and build configuration affect tracing inputs. No malicious pattern was supplied and end-to-end exploitability of a particular source edit was not demonstrated. A successful ordinary build is not evidence that the vulnerable routine received an attacker-controlled pattern.

Next also bundles legacy minimatch-style implementations in compiled glob and serve-handler. Those do not contain the cited optimization routines. They remain part of the bundled-code inventory, not extra npm installations. The nft finding broadens the investigation's risk boundary to **build tooling**, not just lint tooling, even though the package containing it is a production dependency.

### Production artifacts and limitations

Inspected **22 available production NFT trace files**: no minimatch package path or the nft/glob/serve-handler compiled bundles were listed. Inspected **178 generated `.next/server` / `.next/static` JavaScript files**: no minimatch identifier or cited optimization routine marker was found. Source has no public glob-evaluation endpoint. These observations support a build/developer/CI exposure boundary for the current application.

This is static artifact/path inspection, not proof that no lazy module can ever load or that arbitrary future Next deployment configurations are safe. `npm audit --omit=dev == 0` alone is insufficient to dismiss bundled code. A production installer still installs Next's package files, including tools not presently referenced in the serving traces.

## Remediation evaluation, in requested order

1. **Compatible parent update:** [fresh official npm metadata](security-disposition-20261101/metadata.json) shows ESLint 10.14.0 requests minimatch `^10.2.6`, config-array 0.23.5 requests `^10.2.4`, ESTree 8.72.1 requests `^10.2.2`, eslintrc 3.3.7 requests `^3.1.5`, and current React/import/JSX-a11y versions still request `^3.1.2`. Their compatible ranges do not select patched major 11. ESLint 10 also remains outside the declared React/import/JSX-a11y ESLint peers. A supported full-chain upgrade is not established.
2. **Transitive resolution:** registry metadata still ends the 3.x line at 3.1.5 and 10.x at 10.2.6. No patched release within the existing major ranges was found. A lock refresh cannot supply a patch that does not exist in those ranges.
3. **Targeted override:** official minimatch **11.0.3** was installed only in a sibling scratch API probe with lifecycle scripts disabled. Its own audit is zero. The package's CJS export is an object, while 3.1.5 exports a function. Reproducing the legacy plugin's direct call with 11 immediately throws **TypeError: fixed is not a function**. A blanket 3→11 substitution therefore fails the interface prerequisite. Seven small benign named-API comparisons between 10 and 11 agreed, but these do not establish complete compatibility. Even a successful ESTree-only override leaves 3.x and Next's embedded nft code unresolved. No partial override was applied or presented as a fix.
4. **Next patch update:** current official Next is **16.4.3**. Its official npm tarball was inspected without installing it. All three compiled bundles above are **byte-identical** between 16.4.2 and 16.4.3. Thus the current framework patch does not remediate the embedded implementation. In particular the nft file SHA-256 in both is `e436d398b2263fb87a2d8ee3d9dab8db2544c684ba9bc1c0d4ab4e67acbab207`. [Full comparison](security-disposition-20261101/next-bundled-comparison.json).
5. **Minimal local backport:** the upstream algorithmic limits could be backported, but patching ESTree's transitive library alone leaves the embedded nft copy. Editing Next's generated minified bundle would introduce an application-maintained dependency patch, integrity/reproducibility obligations and potential semantic differences. The 3.x audit range would still need explicit disposition. A homemade legacy export adapter or changed version label would not establish a security fix. No unreviewed fork, generated-bundle patch, audit suppression or npm audit fix --force was used.

No complete correction passed prerequisite compatibility review, so **no candidate was promoted into the application**. A failed interface probe was rejected before expensive frontend validation. This is a characterized blocker, not a claim that every possible future backport or lint-stack redesign is impossible.

## Tests and reproducibility

- Fresh full/production audits and package tree/explanation: executed, results above.
- Safe official 11.0.3 API probe: legacy-call failure reproduced; seven named-API cases agreed; no DoS input executed.
- Scratch `npm ci --ignore-scripts`: succeeded against its isolated lock and reported zero findings. This is API-probe reproducibility only, not app install acceptance. Probe host was **Node 24.12.0 / npm 11.6.2**, distinct from CI's **Node 22.22.0 / pinned npm 10.9.4**. No broader claim is transferred across those environments.
- V7.2 files were not changed, so its already-recorded successful lint/typecheck/build (72 pages), 112 unit tests, 5 targeted Chromium cases and 15 film/navigation regressions were not repeated. They validate the existing UI baseline, not a patched dependency chain.
- No full candidate clean-install, lint, typecheck, build, unit or browser result is claimed. Any future applied fix must run all those checks with the pinned package manager, repeated clean installation, both audits, exact lock diff, production boundary checks and V7.2/film regressions.
- Isolated commands initially had working-directory/output-path errors; corrected runs succeeded. These were probe orchestration errors, not application failures. No application state was reverted or reset.

## CI, compensating controls and confidence

Existing CI has read-only repository permissions, no persisted checkout credentials, hosted ephemeral Ubuntu runners, a 15-minute job timeout, pinned Node/npm checks, normal npm ci, lint/unit/build/typecheck/browser checks and retained evidence. There is no pull_request_target workflow for this frontend job. These controls were read, not modified.

**Audit nuance:** the current frontend workflow has no separate fail-on-npm-audit step. npm ci reports findings but its report alone is not an enforced security disposition. Existing tests exclude the previous lint chain from production traces but do not explicitly name minimatch or inspect nested compiled nft code. Neither control was silently described as broader than it is. Security review remains necessary even if hosted checks are green.

Confidence is **high** for installed versions, API incompatibility, unchanged Next bundles and current artifact inventory; **moderate** for full exploit reachability. No network-user input path is demonstrated. Adversarial repository/build input can reach tooling, and dependencies/configuration can change that boundary. Current raw application records/crypto paths are unrelated; no confidentiality/integrity compromise is established by this availability advisory.

Existing isolation/timeouts reduce impact to developer/CI availability. Additional controls that could support a narrowly authorized bridge include maintainer review of dependency/config/build-path changes before execution, disposable runners with CPU/memory/time limits, no confidential data/secrets in builds, production dev-dependency omission plus artifact verification, separate audit evaluation of bundled tooling, and monitoring of upstream backports. These are proposals, not changes applied by this investigation or proof that the advisory is fixed. A hosted-job timeout limits duration, not all resource exhaustion.

## Required decision and bounded exception proposal

Recommendation remains **BLOCKED**. Prefer a maintained compatible upstream fix/backport and a framework fix for embedded code. If the founder instead elects a temporary risk disposition, it must explicitly cover **development/build/CI availability for this advisory, including Next's embedded nft code**; it must not claim runtime safety or broaden M8-SEC-001 implicitly.

The maximum bridge I would recommend for review is **72 hours from explicit approval**, ending sooner at a compatible fix, material risk change or any integration/production deployment. This is an engineering recommendation to limit exposure, not a scientific safe-duration guarantee, approved exception or automatic timer. Reevaluate before any PR publication/merge, any dependency/build/glob configuration change, and at least daily during that bridge. Any extension requires another explicit decision. No production deployment should be authorized under this bridge.

The separate ESLint EOL exception still expires today at 23:59 Toronto. A minimatch decision does not extend it; later work requiring that exception needs its own explicit founder disposition. No approvals are requested or inferred from green tests. Until the relevant gates are explicitly satisfied, **do not commit/push/merge/release/deploy** this work under this report.

## Evidence and changed files

This task adds only this report and `security-disposition-20261101/` evidence. Existing V7.2 files remain byte-for-byte preserved. Scratch packages/Next tarball/backups stay outside the Git repository under `work/security-gate-20261101/`.

[Inventory/runtime](security-disposition-20261101/inventory-and-runtime.json) · [audits](security-disposition-20261101/audit-full.json) · [parent metadata](security-disposition-20261101/metadata.json) · [safe API results](security-disposition-20261101/api-probe-results.json) · [Next comparison](security-disposition-20261101/next-bundled-comparison.json) · [preservation](security-disposition-20261101/preservation-check.json).
