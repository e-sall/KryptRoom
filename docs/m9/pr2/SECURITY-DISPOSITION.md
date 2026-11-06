# M9-PR2-SEC-001 — explicit Founder decision

Status: APPROVED UNDER CONDITIONS. Owner: e-sall.
Recorded: 2026-11-06T06:45:07.000Z. Automatic expiration: 2026-11-07T06:45:07.000Z.
Timezone for Founder decisions: America/Toronto. Maximum duration24hours;
no automatic renewal. Independent of all previous M8/M9 dispositions.

Scope: local, non-public PR2 frontend validations only, covering ESLint9 EOL and
the eight existing moderate minimatch/Next-nft findings already documented under
GHSA-g3hv-75wg-m249. These findings remain unresolved; this is risk acceptance,
not remediation or a claim of complete security.

Founder explicitly requires trusted development code/inputs, no real company data
or production secrets, visible audits and unchanged security controls. Stop on
high/critical findings, materially changed exposure, or expiration. The exception
cannot bypass OIDC, CSRF, BFF, tenant isolation, required checks or any tests.

No hosted CI, push, PR opening, merge, deployment or production service is covered.
No new vulnerability is accepted. The proposal was checked against these exact
limits; all restrictions are retained. Any later extension needs explicit Founder
authorization. Local runner must verify this deadline before dependent operations.
