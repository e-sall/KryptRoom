# KRYPTROOM M8 — V7.2 PUBLICATION & SECURITY EXCEPTION REPORT

Date: 2026-11-01, America/Toronto. Existing PR20 and branch
`feat/m8-responsive-accessibility-final-qa`; parent
`56b9a883977c8899b564e3e97ad6e82b70670a39`. Final published SHA and hosted
results are maintained in the PR body after publication, avoiding a report commit
that invalidates its own recorded HEAD. No merge or deployment is authorized.

## Founder decision and clocks

[M8-SEC-002](M8-SEC-002.md) is a distinct, explicit founder approval for
GHSA-g3hv-75wg-m249 in trusted development/build validation and V7.2 publication
on PR20 only. Recorded approval receipt: **2026-11-01T07:00:41Z / November 1,
02:00:41 EST Toronto**. Hard expiration: **2026-11-04T07:00:41Z / November 4,
02:00:41 EST Toronto**. No automatic renewal, production-service scope, unrelated
vulnerability acceptance, merge or deployment approval.

M8-SEC-001 remains independently limited to ESLint 9 EOL and expires
**2026-11-01 23:59 Toronto / 2026-11-02T04:59Z**. It was active at local
validation/publication preparation. M8-SEC-002 does not extend that earlier gate;
later operations that depend on EOL acceptance require a separate explicit decision.

## Verified source and controls

PR20 was confirmed OPEN, same-owner/non-fork, head matching the local parent.
Dev remained `8e8d8349db565278a866bd82f743f03fd1ee8c35`; main remained
`1715b504e2041127056127ab5236a3248195a234`. The input is the preserved,
founder-directed V7.2 tree plus the approval and validation documentation.
Unknown PR commits/artifacts were not incorporated. Dependency and lockfile pins
are unchanged. No root install or untrusted ZIP/glob input was executed.

Existing CI was read and preserved: read-only contents permission, unpersisted
web checkout credentials, ephemeral hosted runner, pinned Node 22.22.0 and npm
10.9.4 verification, normal frontend npm ci, timeouts, all existing checks and
evidence retention. Root policy jobs retain npm ci --ignore-scripts. The current
web workflow has no separate fail-on-audit step; npm install output/green checks
are not misrepresented as a clean full audit. Audit results are explicitly recorded.

Before branch advancement, remote parent/base and applicable deadlines must be
checked again. CI results apply only to the resulting published SHA. No broad
CI exclusions, weakened security settings, forced dependency, rule suppression
or new skip is introduced. The unchanged classifier must keep heavy crypto jobs
skipped for this frontend/documentation delta while retaining mandatory policy,
contract and reproducibility checks.

## V7.2 behavior and evidence

The preserved [V7.2 report](MARKETING-V72-REPORT.md) and
[gallery](marketing-v72/README.md) cover six founder corrections: compact 6px
Quantum grouping, Why label raised 8px, natural document scrolling with four
accessible click-selected How steps, top Technology label with centered editorial
content, Founder name/label alignment and stronger pointer-local cryptographic
CTA reveal. V7/V7.1 history remains dated evidence; their retired wheel lock is
not current behavior.

Local publication checks: lint, typecheck, **112 unit/component tests**, production
build (**72 static pages**) and **31 classifier tests** passed. The complete local Chromium run passed **181 tests with two inherited exclusions** (183 total, 10.7 minutes), across desktop/tablet/mobile. Hosted CI is recorded separately in PR20.
Local Node 24.12.0/npm 11.6.2 is distinct from CI's pinned clean-install environment;
local results are not claimed as that environment's acceptance. Previous V7.2
targeted browser results remain historical until the new run finishes.

No new M1–M7 cryptographic integration, Groth16 or blockchain action is claimed.
Windows WebKit results from V7.1 are historical, not new V7.2 certification.
No Firefox, device, physical trackpad or full WCAG certification is asserted.

## Current audits and residual risk

[Publication frontend full audit](security-disposition-20261101/publication-audit-full.json):
**16 moderate propagated package findings from one advisory**, two registered
minimatch installations (**3.1.5** and **10.2.6**).
[Production audit](security-disposition-20261101/publication-audit-production.json):
**zero findings**. The embedded Next @vercel/nft tracing implementation remains
identified in the [disposition report](MINIMATCH-SECURITY-DISPOSITION-REPORT.md).
No visitor path has been demonstrated; this is not proof of inexploitability.
No complete compatible fix was established. Advisory visibility is preserved.

A root-level audit, distinct from apps/web, also reports preexisting adm-zip
advisories through @openmined/psi.js → protoc-gen-js 3.21.4 → adm-zip 0.5.10.
This is not covered or accepted by M8-SEC-002, and no root dependency changes
are made. Bounded triage found adm-zip used by protoc-gen-js/post-install.js to
extract a versioned official protobuf-javascript release; root CI policy jobs
already disable lifecycle scripts. No invocation of that generator/ZIP library
was found in application/tests/runtime paths searched, and this publication
does not execute its installer or accept external ZIPs. This is a separate core
dependency follow-up, not a clean root audit claim or proof of non-exploitability.
Do not reuse the frontend exception for root dependency work. The raw root-audit
triage is retained outside Git in the task's preserved scratch evidence.

## Scope and publication boundary

Only frontend presentation/tests, M8 documentation/evidence, CHANGELOG and TODO
are intended for this commit. The four reserved film files, canonical logo,
portrait assets, dependency pins, crypto code/fixtures, CI, main and dev are
unchanged. Prototype 12 remains reserved to chat 05; no new SVG scene or DESIGN
LOCK is inferred. Local Next-generated AGENTS.md and dev type-path changes are
preserved locally and excluded from publication.

The loopback preview remains http://127.0.0.1:3002/ using the existing dependencies.
It is not public deployment. Working-tree/source comparison after publication
must distinguish any generated local-only files from published V7.2 work.

Maximum permitted verdict after current checks: **READY FOR FOUNDER VISUAL REVIEW**.
Remaining gates: founder visual acceptance, separate merge authorization,
reevaluation of both exceptions before further dependent decisions, and compatible
security remediation or newly explicit bounded decisions at the applicable deadlines.
M8 completion, production readiness and M9 are not authorized or asserted.
