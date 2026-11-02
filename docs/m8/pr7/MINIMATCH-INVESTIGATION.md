# GHSA-g3hv-75wg-m249 — bounded local investigation

Date: 2026-10-31 America/Toronto. No exception renewal, dependency change, exploit, commit or publication. Founder authorized investigation and local visual work separately from the security publication gate.

## Observed dependency and audit evidence

`npm ls minimatch --all` and `npm explain minimatch` were executed. Complete outputs: [tree](marketing-v7/minimatch-tree.txt), [explanation](marketing-v7/minimatch-explain.txt).

Two installed versions/locations:

- `node_modules/minimatch` **3.1.5**, shared by ESLint 9.39.5, config-array 0.21.2, eslintrc 3.3.7, React 7.37.5, JSX-a11y 6.10.2 and import 2.32.0 plugins.
- `node_modules/@typescript-eslint/typescript-estree/node_modules/minimatch` **10.2.6**, through ESTree 8.72.0 / typescript-eslint / eslint-config-next 16.4.2.

[Current full audit](marketing-v7/security-audit-current.json): **16 moderate package entries**, **18 unique affected-package installation paths**, **one underlying advisory URL**, **two actual minimatch installations**. These counts are distinct. The JSON inventories every propagated package, range and path; they are not 16 independent vulnerabilities. [Production audit](marketing-v7/security-audit-production-current.json): **zero findings**.

`npm ls minimatch braces --omit=dev --all` is empty. All 22 available `.next/**/*.nft.json` traces were inspected and none includes minimatch. These include the existing production build traces, not merely dependency dev flags. Source contains no minimatch/lint import or endpoint executing supplied glob expressions. This is bounded artifact/source inspection, not an exhaustive binary or deployment certification.

## Reachability

The [official advisory](https://github.com/advisories/GHSA-g3hv-75wg-m249) flags `<11.0.1`, describes globparts amplification in minimatch 10.2.6 at `optimizationLevel >= 2`, and identifies 11.0.1 as patched.

The installed 10.2.6 implementation defaults to level 1. Its only matching call found in ESTree's distributed JS is `useProgramFromProjectService.js:244`, using `minimatch(filePath, pattern, {dot:true})` for `allowDefaultProject` patterns. The repository ESLint configuration does not enable projectService/allowDefaultProject or optimizationLevel 2. No override to level 2 was found in inspected lint packages. The 3.1.5 implementation has neither this option nor the cited firstPhasePreProcess routine; nonetheless the published broad version range and npm audit still flag it. No claim of upstream withdrawal or complete non-applicability is made.

The website supplies no untrusted HTTP/form/upload glob-input path to this development tooling. Repository contributors and developer/CI-supplied configuration remain a separate untrusted-code boundary; future configuration or dependency changes can alter reachability. No CPU/memory exhaustion demonstration was run.

## Compatible remediation assessment

[Official npm metadata snapshot](marketing-v7/npm-current-metadata.json) was read without installing packages. Current minimatch is 11.0.3, while current ESTree 8.72.1 still requests `^10.2.2`, current ESLint 10.14.0 requests `^10.2.6`, and current React/import/JSX-a11y plugins request `^3.1.2`. These declared ranges do not select 11.0.1 or 11.0.3. A lock-only refresh or straightforward parent upgrade does not establish a complete fix.

Forcing 11 over 3 also crosses an API boundary: installed v3 exports a callable CommonJS function used directly by plugins, while modern releases expose named APIs. A blanket override is not demonstrated compatible. ESLint 10 additionally remains outside the official React/import/JSX-a11y peer ranges. npm's suggested major downgrades are not accepted remediation. No force, override, suppressed audit, lockfile modification or install was performed.

No complete compatible correction is established. A reviewed upstream backport/compatible parent chain, or an explicitly scoped founder risk decision, is required before publication. This report does not authorize either. Reduced observed reachability does not mark the advisory fixed.

M8-SEC-001 remains ESLint 9 EOL only, owner e-sall, expiring **2026-11-01 23:59 America/Toronto**; mandatory reevaluation before merge or expiration. No automatic extension or new exception. Local preview is authorized; push, merge, release and public deployment remain blocked under the unresolved disposition.
