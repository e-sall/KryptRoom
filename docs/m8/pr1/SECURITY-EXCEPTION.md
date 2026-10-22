# M8-SEC-001 — Temporary PR1 lint-tooling exception

Reviewed: **2026-10-22**. Scope: `apps/web` only, PR #14. Owner: repository
maintainer (`e-sall`), with the frontend maintainer responsible for reevaluation.
This record is the bounded temporary exception requested in final review, not
an upstream fix or an independently signed security approval. Maintainer approval
of the PR must include acceptance of this record. No automatic merge is enabled.

**Expiry / mandatory reevaluation: before M8 PR7 starts, or 2026-11-21,
whichever occurs first.** Reevaluation is also required before any deployment
that includes development tools, any service integration that accepts patterns,
or a change to the dependency chain below. No automatic extension. Track closure
in `TODO.md`; resolve or explicitly renew with new evidence before the deadline.

## Verified dependency and compatibility evidence

- `npm ls braces --all`: only `eslint-config-next@16.4.2` →
  `@next/eslint-plugin-next@16.4.2` → `fast-glob@3.3.1` → `micromatch@4.0.8` →
  `braces@3.0.3`. All entries are development-only in the committed lock.
- `npm ls braces --omit=dev --all`: empty. A separate clean
  `npm@10.9.4 ci --omit=dev --ignore-scripts` install also contains neither braces
  nor ESLint. Ignoring scripts here is solely an inspection precaution, not the
  build/CI installation method. The application CI still uses normal `npm ci`.
- `npm audit --omit=dev --json`: zero findings. Full audit: five high findings
  propagated from **one** advisory, not five independent vulnerabilities.
- [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm)
  affects braces <=3.0.3; no patched version is listed. Registry latest is 3.0.3.
  Deeply nested brace patterns can exhaust the Node call stack (availability).
- [ESLint support policy](https://eslint.org/version-support/) confirms v9 EOL
  since 2026-08-06. Installed 9.39.5 is the last 9.x patch; registry current is
  10.13.0. This is a maintenance risk, not a newly demonstrated runtime exploit.
- Registry current `eslint-config-next` remains 16.4.2. Its peer accepts >=9,
  but current `eslint-plugin-react@7.37.5` declares only through `^9.7`.
  A supported drop-in ESLint 10 upgrade is therefore not established for the
  current official config. No `--force`, peer-dependency bypass, framework
  downgrade or audit suppression is applied. Package and lock remain unchanged.

## Reachability and compensating controls

The vulnerable package is **not reachable from application users** in this PR1
architecture. Source inspection found no lint imports, pattern execution service,
API routes, server actions or upload endpoints. The browser's example text field
has no submission or network sink. Runtime Next file traces are checked by the
browser suite for the absence of the excepted dependency chain.

The installed Next lint plugin's `dist/utils/get-root-dirs.js` sends
`settings.next.rootDir` to `fast-glob.globSync`. This app's ESLint config does not
set that property; the plugin uses the fixed working directory. `npm run lint`
runs `eslint .` on repository files, never an HTTP/form/query value.

**Repository contributions are a distinct untrusted-input boundary.** An external
PR author could modify lint configuration/source and cause a CI or developer-tool
denial of service; this is not equivalent to web-user reachability. The exception
does not promise safety when executing arbitrary third-party code locally.

Controls already in place:

- Hosted ephemeral Ubuntu runner, 15-minute job timeout, read-only repository
  token, no application secrets or deployment credentials passed to the web job.
- Checkout `persist-credentials: false`; no privileged `pull_request_target`
  execution, self-hosted runner or deployment step in the web workflow.
- Exact dependency/manager pins; ordinary clean CI installation and unchanged
  audit visibility. Development tools must not be installed in a production
  deployment; use a clean `--omit=dev` runtime tree or verified build artifact.
- Regression checks enforce the dependency-chain dev classification, absence
  from production file traces and the disconnected application I/O boundary.

Residual risk: crafted repository inputs can stop lint/consume CI minutes;
ESLint 9 receives no upstream fixes, so undiscovered/future issues may remain.
These controls limit exposure but do not remove the advisory or restore support.
This exception covers only this advisory and this ESLint lifecycle gap, not
future advisories, production dependencies, cryptographic code or other tooling.

## Exit criteria

At the deadline (or earlier on an upstream release), recheck registry versions,
peer compatibility and both audits. Upgrade to a patched compatible dependency
chain and supported ESLint, or adopt a separately reviewed lint configuration
without the vulnerable chain. Run clean installation, lint, unit tests, build,
typecheck, browser validation and all required PR checks. If no fix exists,
maintainer review must explicitly renew a bounded exception; PR7 cannot silently
inherit this one. No Groth16 rerun, chain transaction or M1–M7 change is needed.
