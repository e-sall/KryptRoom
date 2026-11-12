# M9 PR5 — publication gates remain closed

## Current dependency evidence

Fresh npm 10.9.4 full frontend audit reports **8 moderate, 0 high/critical**, exit 1;
production audit: zero, exit 0. Root full/production: zero. Python locked runtime/development:
zero known findings. These are scoped dependency audits, not demonstrated security.
All repository dependency/lockfile bytes remain unchanged.

[GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249)
affects minimatch >=7 and <11.0.1; the metadata points to one advisory through
multiple packages, not eight independent vulnerabilities. The official latest
minimatch 11.0.8 cannot be forced into ^10 parent contracts. Next's embedded nft
build-tool copy must be assessed separately from npm production counts. The
canonical compiled nft file is absent in the tested standalone; that one-path
negative probe is not a general proof of absence or visitor inexploitability.

[ESLint's support policy](https://eslint.org/version-support/) marks 9 EOL;
10.14.0 is current. Current React 7.37.5, import 2.32.0 and JSX-a11y 6.10.2
official peer ranges exclude 10. An isolated strict resolution of Next/config
16.4.6 + ESLint10 fails ERESOLVE. A compatible patch-only Next/config16.4.6
resolution succeeds but still audits at eight moderates, so no dependency change
was imported. Audit fixAvailable recommends a major config downgrade to 15.5.29;
that is not a safe established fix for this stack. No force, override or downgrade.

No old M8/M9 exception is renewed, broadened or reused. The existing gate rejects
the actual audit exit and also rejects unresolved counts if an exit code is forged
to zero. Its source/workflows/classifier and blocking audits remain unchanged.
No administrator record or empty audit is fabricated. A compatible supported fix,
or a separately approved security design/disposition with independent review, is
needed before publication. No such approval is granted by local test success.

## GitHub enforcement: observed and unknown

Read-only GitHub responses are in the handoff. The repository ruleset collection
shows one active ruleset, 26999669, on main/dev: PRs required, deletion and force
push prohibited, no bypass actors. It specifies zero required approvals and no
required status checks, code-owner review or last-push approval. Classic branch
protection reads for main/dev return 403 to the integration: **UNKNOWN**, not absent.
An administrator must inspect Settings → Branches and Rules → Rulesets for both
branches and export effective settings before a publication decision. No setting
was modified and no hosted workflow was executed.

Minimal separately authorized plan: require current-SHA successful applicable
contexts (including `foundation`, frontend `test`, and
`m9-identity-organizations` once published); bind to the expected GitHub Actions
application/source. Keep explicit scope results and all current Core checks.
Confirm exact observed names on the actual hosted SHA before configuring them.
Do not replace cryptographic controls with an absent workflow or silent skip.

Protect `.github/**`, manifests/lockfiles, auth/BFF, migrations and security records
through a real independent trusted reviewer, code-owner requirement, stale-review
dismissal and last-push approval. Do not create a fictitious CODEOWNER. With e-sall
as sole identified maintainer, independent review remains a governance blocker.
CODEOWNERS/required checks alone do not prevent a PR from changing its own local
helper or publishing a lookalike job under the same Actions app. Use a protected
required workflow from a trusted source if available, or an independent validator
whose signing/check authority and reviewed code cannot be changed by that PR.

The existing review record binds source SHA, ancestor baseline, event, repository,
lock/audit/nft hashes, image, support/fix assertions, expiry <=24h and revocation.
It is not independently authenticated merely because it is an admin variable.
Creation/modification authority, immutable record provenance, prompt revocation and
trusted validation before untrusted execution remain to establish. Merge-time
protection cannot retrospectively make an already unsafe CI build safe. Keep PR
inputs trusted, jobs least-privileged and production secrets inaccessible.

## Provenance and next decisions

Local image IDs and build-input SHA-256s are measured provenance, **not signed SLSA
attestations** or third-party certification. Signing, hosted source verification,
SBOM/OS scanning and production exposure are separate future gates. Stacked PR2–PR5
commits and their reviews must be reconciled through an explicitly authorized
publication sequence; do not force-update dev/main or import the blocked M8 promotion.

Next executable action: targeted independent QA04 of this exact local PR5 delta.
Then Founder must decide compatible security remediation/risk governance,
independent enforcement and publication scope before any push or hosted CI.
Merge and deployment require further distinct authorizations. Current result:
READY FOR LOCAL QA; publication, merge and deployment NO-GO.
