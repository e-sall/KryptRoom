# M8-SEC-001 — Current decision and historical PR1 record

## Founder renewal — 2026-10-25 (current)

Marketing V4 reevaluation, 2026-10-29: scope, owner and expiration unchanged.
Official npm peer metadata still excludes ESLint 10 in React 7.37.5, JSX-a11y
6.10.2 and import 2.32.0. Current full and production audits return zero;
production dependency/trace checks exclude braces and lint tooling. The GHSA
withdrawal remains in force. See [V4 evidence](../pr7/MARKETING-V4-REPORT.md#security).
This is evidence collection, not a renewal, merge approval or production approval.


PR20 final-review reevaluation on 2026-10-26: unchanged scope and expiration;
withdrawal reconfirmed, full/production audits zero, strict isolated ESLint 10
compatibility probe still fails. See the [current follow-up evidence](../pr7/REVIEW-FIX-REPORT.md#security-reevaluation).
This evidence update does not renew or broaden the founder's decision.

**APPROVED — LIMITED EXCEPTION RENEWAL.** The founder explicitly authorized
PR7 implementation after the pre-PR7 security reevaluation. This supersedes the
original deadline below; the original record is preserved as dated evidence.

- Scope: **ESLint 9 end-of-support risk only**, development tooling in `apps/web`.
- Owner: repository maintainer / founder **e-sall**; frontend maintainer performs
  compatibility checks and reports to the founder. No delegated renewal authority.
- Expiration: **2026-11-01 at 23:59 America/Toronto** (2026-11-02 04:59 UTC).
- Mandatory reevaluation: **before PR7 merge or expiration, whichever is first**.
  Any later extension requires a new explicit founder approval.
- GHSA-vfj7-8cjw-p6xm portion: **CLOSED — upstream withdrawal on 2026-10-23**,
  not a package patch or evidence that ESLint is supported. The
  [official advisory](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm)
  states that the issue is not practically exploitable. Current full and production
  audits report zero findings. See [reevaluation evidence](../pr7/PRE-PR7-SECURITY-REEVALUATION-REPORT.md).
- ESLint 9 remains EOL. The direct supported ESLint 10 / official Next config
  probe fails strict peer resolution; no forced dependencies or audit suppression.
- Preserve existing CI security controls, read-only permissions, isolation,
  dependency pins, audits, tests and production trace checks. No runtime,
  production, cryptographic or future vulnerability is covered by this renewal.
- No production service deployment is authorized. No new material risk may be
  accepted implicitly: stop and report it.

Exit: install a supported compatible lint chain under a separately reviewed
change, then pass clean install, both audits, lint, typecheck, build, unit/browser
tests, production exclusion checks and required CI. Until then, monitor official
release/peer metadata; a bounded daily read-only Codex watch has been scheduled
through the expiration date, notifying only actionable changes or deadline action.
The watch cannot renew the exception or authorize a merge. Check manually before
merge even if no notification has arrived. Zero audit findings do not remove EOL risk.

## Historical PR1 decision — superseded, not current approval

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

PR2 follow-up (2026-10-22): the same app and unchanged dependency lock now contain
isolated synthetic Rooms/setup forms. They introduce no network, lint invocation,
upload, execution or storage sink. Existing dependency classification, production
trace checks and application I/O guards remain active. This does not extend the
exception's scope or expiry; before PR7 / 2026-11-21 remains the deadline.

## Exit criteria

At the deadline (or earlier on an upstream release), recheck registry versions,
peer compatibility and both audits. Upgrade to a patched compatible dependency
chain and supported ESLint, or adopt a separately reviewed lint configuration
without the vulnerable chain. Run clean installation, lint, unit tests, build,
typecheck, browser validation and all required PR checks. If no fix exists,
maintainer review must explicitly renew a bounded exception; PR7 cannot silently
inherit this one. No Groth16 rerun, chain transaction or M1–M7 change is needed.
