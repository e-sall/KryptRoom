# KRYPTROOM M8 — PRE-PR7 SECURITY REEVALUATION REPORT

Reviewed 2026-10-25, America/Toronto. Initial Phase 0 verdict:
**RENEWAL REQUIRES FOUNDER APPROVAL**. No PR7 implementation began under that
verdict. Subsequent explicit founder decision: **APPROVED — LIMITED EXCEPTION
RENEWAL; GO FOR PR7 BUILD**. The gate is now conditionally satisfied, not resolved.

## Decision and boundary

The founder approved only the remaining **ESLint 9 EOL** risk in development
tooling. Owner: **e-sall**, repository maintainer / founder. Frontend maintainer
collects evidence and escalates; it cannot extend the exception.

Expiration: **November 1, 2026, 23:59 America/Toronto** (November 2, 04:59 UTC).
Reevaluate **before PR7 merge or expiration**, whichever comes first. New material
risk requires stopping and reporting. Any extension needs new explicit founder
approval. No runtime/production dependencies, crypto components or new advisory
are covered. No production service deployment is authorized.

This decision is recorded in the [canonical exception](../pr1/SECURITY-EXCEPTION.md)
above the preserved historical PR1 record. No retrospective rewrite of earlier
acceptance or proof evidence. The prior Phase 0 proposal remains a historical
local report; this is the repository's current disposition.

## Updated evidence

- [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm)
  was withdrawn on October 23, 2026 as not practically exploitable. **Close the
  GHSA portion**, not as a package patch. braces remains 3.0.3.
- [ESLint support](https://eslint.org/version-support/): 9.x EOL since August 6,
  2026; installed 9.39.5 is unsupported, 10.x is the current supported line.
- Full and production audits with pinned **npm 10.9.4**: zero findings.
  [Full JSON](audit-all.json), [production JSON](audit-production.json).
- `npm ls braces --all`: eslint-config-next 16.4.2 → @next/eslint-plugin-next
  16.4.2 → fast-glob 3.3.1 → micromatch 4.0.8 → braces 3.0.3, development only.
  `npm ls braces --omit=dev --all`: empty (exit 1 denotes no matching package).
- Separate clean production install from the exact manifest/lock with
  `npm@10.9.4 ci --omit=dev --ignore-scripts`: 26 packages added, zero findings,
  neither braces nor ESLint installed. Ignore-scripts is for inspection only;
  ordinary CI/install scripts and checks are unchanged.
- Production build: 68 pages. Phase 0 inspection of 22 `.nft.json` files,
  3,834 file references, **zero lint-chain package references**. Existing browser
  regression repeats this exclusion on the PR7 build. Traces do not establish
  an exhaustive supply-chain audit.
- No lint import, external pattern service, business API, server action, upload,
  browser network/storage sink or path from a form/query to ESLint was found.
  Installed Next lint plugin calls fast-glob for configured `settings.next.rootDir`;
  the app sets no rootDir and uses a fixed repository working directory.

## Compatibility check (not a forced upgrade)

Official npm metadata observed October 25: ESLint 10.13.0, eslint-config-next
16.4.3 and @next/eslint-plugin-next 16.4.3 are current. Config's >=9 peer does
not prove the transitive chain compatible. eslint-plugin-react 7.37.5 supports
through ^9.7; eslint-plugin-jsx-a11y 6.10.2 and eslint-plugin-import 2.32.0 exclude
10. Hooks 7.1.1 and typescript-eslint 8.72.0 do accept 10. Node 22.22 used in CI
satisfies ESLint 10's engine requirement.

An isolated private manifest with exactly ESLint 10.13.0 and eslint-config-next
16.4.3, resolved with `npm@10.9.4 install --package-lock-only --ignore-scripts
--strict-peer-deps`, exits **1 / ERESOLVE**. The reported conflict is
eslint-plugin-import 2.32.0 via eslint-import-resolver-typescript 3.10.1. This is
a dependency-resolution test, not an execution of every ESLint 10 rule.
Upstream [React #3977](https://github.com/jsx-eslint/eslint-plugin-react/issues/3977)
and [JSX a11y #1075](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/issues/1075)
remain open at review. No compatible drop-in official chain was established;
this does not prove that no alternative could ever be reviewed.

No force, legacy peer bypass, downgrade, audit suppression, package change or
rule removal. A separately reviewed supported configuration must demonstrate
rule parity before adoption.

## Compensating controls, residual risk and exit

Web CI retains Ubuntu 24.04 hosted ephemeral runners, 15-minute timeout,
contents:read, persist-credentials:false, no pull_request_target, no application
secrets/deployment credentials, exact pins and ordinary clean installation.
The application and lock remain isolated from core runtimes. All source boundary,
production trace, privacy, contract and scope tests remain active.

Untrusted repository contributions can still propose hostile code/configuration
executed during development or CI. No web-user runtime exposure was demonstrated;
that is not a guarantee of safe arbitrary PR execution. EOL leaves unknown/future
tool defects and no upstream fixes. Zero npm findings does not restore support.

Exit requires a reviewed supported lint configuration, clean compatible install,
both audits, lint, typecheck, build, complete unit/browser checks, production
exclusion and required CI passing. Until then, a bounded daily read-only watch
checks official versions, peers and advisories through expiration, notifying
actionable changes/deadline only. It cannot change dependencies, renew approval,
merge, deploy or execute cryptography. Mandatory pre-merge reevaluation is not
replaced by the watch. PR7 remains unmerged pending independent review.
