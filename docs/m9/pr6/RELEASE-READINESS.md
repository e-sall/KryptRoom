# M9 PR6 — local release gate remediation

Base: approved PR5 `51e885cd181120df90a342883467387a4e18b8c2`.
Branch: `codex/m9-pr6-release-gates`. Publication is NOT authorized.

## Local changes and validation

- Official digest-pinned Node 22.23.5 security patch and npm 10.9.10; strict clean
  peer installation. No application dependency/lockfile or ESLint rule change.
- Unused npm/corepack physically removed from standalone BFF; pip removed from
  served API after installing hash-locked dependencies. Test stages retain their
  installers. No scan exclusion. Debian apt/libapt security patch 2.6.2.
- History-losing Alembic downgrade refused online/offline before DDL. Existing
  0001–0006 migration files unchanged. Only trusted Config opt-in AND test
  environment AND *_test database permits an intentional disposable reset.
  No production override or new application endpoint.
- Real PostgreSQL 17 logical restore: private 0600 archive, new destination,
  unchanged source, all table fingerprints, schema version, function definitions,
  owners/ACLs, RLS policies/flags and database grants compared. Existing target
  never overwritten. Not PITR or production disaster recovery.
- Additive release workflow: explicit classification, separate backend/security,
  frontend operations dependent on successful gates, aggregate refusing failures,
  cancellations, skipped requirements and missing scope. Full action/scanner pins,
  contents:read, no secrets. Archive/config digest/source binding is measured
  UNSIGNED provenance, not an independent attestation or SLSA claim.

Tests: 104 backend unit/security, 39 actual PostgreSQL, 153 frontend unit/component,
three real Edge/Chromium acceptance cases with Keycloak/PostgreSQL/source-free
API/BFF (Rooms save/reopen, collaboration/revocation, restarts, dependency outages,
readiness recovery and real persisted session expiry). Lint, types, production
build, Ruff, formatting, strict mypy and locked Python audits pass. CI/gate tests:
69; actual final decision shell: nine positive/negative executions. Actionlint
and YAML pass; external shellcheck/pyflakes integrations NOT RUN (unavailable).
Two Python distributions compared with fixed SOURCE_DATE_EPOCH; exact hashes and
commands in the handoff. Bit-identical independent Docker rebuild is NOT RUN.

Broad suites found stale delivery assertions expecting the pre-V2 inline audit
and omitting PR5's exact server readiness route. Tests now check the actual strict
gate and exact existing route; adjacent/future paths stay rejected. No general
server exemption. Test-only Docker inputs include the lockfile, canonical Signal
reference mount and writable test caches. Marketing assets/assertions unchanged.

## Explicit gates

- Local QA handoff: GO after exact-source evidence verification.
- Publication/hosted execution/merge/production: NO-GO.
- Eight moderate npm findings and ESLint 9 EOL remain OPEN (SECURITY.md).
- Final runtime scans FAIL: API 98 HIGH/CRITICAL occurrences, BFF 35.
- Hosted workflow and full Compose orchestration NOT RUN. Native Linux bare
  Docker equivalents were used locally; WSL Compose is unavailable.
- PostgreSQL/Keycloak image scans are required by prepared CI but NOT RUN locally.
- Independent review/check enforcement absent; classic protection UNKNOWN/403.
- Unchanged classifier yields core=true, web=true, m9=true for this workflow/helper
  delta. Existing Core/proof workflows remain applicable, potentially Groth16.
  Explicit routing/approval resolution is required BEFORE any push. No exemption
  or required cryptographic check is silently removed. No heavy run occurred.
- Production secrets/rotation, DB verify-full TLS, secure external IdP/BFF,
  encrypted off-host backups, WAL/PITR and measured RPO/RTO require infrastructure.

Prefer reviewed forward migrations and schema-compatible application rollback.
Reverting PR6 must not authorize destructive 0006 downgrade. No raw participant
data, real business credentials, new RoomState or cryptographic operation used.
Next action: QA04 reviews only this delta and its flat evidence; separate Founder
authorization is required for remote governance, publication and hosted execution.
