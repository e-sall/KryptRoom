# M9-PR2-SEC-002 — targeted QA local validation decision

Status: APPROVED UNDER CONDITIONS. Owner: Founder e-sall.
Explicit approval received and recorded `2026-11-07T02:51:16Z`.
Automatic expiration `2026-11-08T02:51:16Z` (November 7, 21:51:16 America/Toronto).
Maximum 24 hours; no automatic renewal. This is a new decision, independent of
M9-PR2-SEC-001 and all earlier M8/M9 dispositions. None is reused or extended.

Scope: trusted, non-public local frontend validation of QA-PR2-01/02/03 only:
lint, types, build, units and real loopback Keycloak/BFF acceptance. It covers
ESLint 9 EOL and the eight existing moderate minimatch/Next-nft findings already
documented. They remain unresolved; approval is not remediation or a security
certification. Fresh complete/production audits remain visible.

Controls: reviewed local code and build/glob configuration; no untrusted source
or artifacts; no real organization data, identity or production secrets; synthetic
loopback fixture; all OIDC/CSRF/RLS/tenant/role/session controls and tests retained.
No forced dependencies, incompatible override, suppressed audit or skipped assertion.
Stop affected execution at expiration, a new high/critical finding or a material
change in exposure/controls. No new vulnerability is accepted by this decision.

No hosted CI, push, PR opening, merge, main change, deployment or production is
covered. Future hosted CI disposition requires a separate explicit Founder decision.

Evidence: official npm metadata and strict isolated resolution at
`2026-11-07T02:49:49Z` still reject the supported ESLint 10.14.0 chain with the
official Next 16.4.5 lint configuration (import/React/a11y peer support through 9).
The repository dependency manifests/lock are unchanged. Upstream minimatch 11.0.5
does not establish compatibility for the installed consumers or the embedded nft
copy. The fresh full audit reports eight moderate and zero high/critical findings;
production and root audits report zero. Raw evidence accompanies the delta package.

Founder response: “J’approuve cette nouvelle disposition locale limitée à 24 h”,
reply to `call_f52de811dbab41e3b095ee2c78df0efa`. The proposed controls and exclusions
were checked against this response before dependent frontend execution.
