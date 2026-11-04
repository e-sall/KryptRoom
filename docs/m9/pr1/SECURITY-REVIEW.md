# M9 PR1 — Security review

Date: **2026-11-03 America/Toronto**. Owner: repository maintainer / e-sall.
This is an implementation review, not an independent audit or production approval.

## Dependency disposition

M9 has an isolated Python dependency graph: no root npm or frontend dependency is
needed by its runtime, tests or image builds. Direct versions are exact; transitives
and distributions are hash-locked. Exports are checked against `uv.lock`.

Fresh `pip-audit 2.10.1` checks on fully hashed runtime/development exports found
**zero known vulnerabilities** in both, on Windows and in Linux. Windows inventory:
23 runtime entries, 72 development-inclusive entries. Linux respects its own
platform markers. No ignore list, forced override, advisory suppression or M8
exception is used. `--disable-pip` avoids re-resolving the complete hash-locked
transitive exports; it does not disable vulnerability queries. Raw JSON evidence
is committed under `evidence/`; Linux CLI outcomes are recorded in validation.

These are Python-package advisory checks, not a complete audit of OS packages,
bundled libpq/OpenSSL binaries, the Docker host, or future production infrastructure.
Image/host CVE inventory and a deployment-specific assessment remain required
before production; no claim of production-ready security is made. Official images
are pinned by immutable digest, not assumed vulnerability-free.

Distribution inspection also found an initial source-build privacy defect: local
test credentials under `.runtime` were included by the default source archive.
The archive remained ignored/local and was never committed, uploaded or published.
It was rebuilt with an explicit source allowlist and private/cache exclusions.
A synthetic regression reproduces the inclusion with the prior manifest and proves
its absence with the final manifest, even without Git ignore rules. Final wheel
and sdist inventories exclude secrets, virtualenvs, caches and stale egg metadata.
Disposable test database volumes are removed after validation. No exception is
used for this defect; it is corrected before the commit.

The legacy baseline root audit independently still reports **three high affected
package entries**: `@openmined/psi.js`, `protoc-gen-js`, `adm-zip`. This is pre-existing
and unchanged, not three new M9 vulnerabilities. The separately prepared M8 fix is
not imported and its risk decisions are not inherited. A feature push would select
M2's root install; a dev PR also selects existing M8 lint/build. **Publication is
BLOCKED pending a specific treatment/routing decision.** No finding is accepted
by this report, and no security exception is created, renewed or broadened.

## Implemented controls and actual negative checks

- Only unauthenticated technical health routes. No identity/session, business
  mutation, secret ingestion, crypto execution or disclosure path.
- Organization enrollment configuration only accepts `controlled`. It is a
  foundation invariant, not an implemented registration flow.
- Business authorization denies by default. Internal references and governance
  metadata do not authorize Core operations. No imports of Core/SecretFlow/OpenFHE/
  blockchain modules are allowed by the source-boundary regression.
- SQL URL constructed from typed operator configuration, password kept in
  `SecretStr` or a mounted secret file; no `.env` autoload, committed password or
  secret-bearing OpenAPI setting. Startup configuration errors are generic.
- Distinct migration/runtime/admin credentials. Runtime role is non-superuser,
  SELECT-only and cannot create tables/delete the marker. Migrations own the
  dedicated schema, not the server. Statements/connect/pool wait are bounded.
- Only technical version/contract/timestamp data is persisted. DB is unavailable
  to the host network; the API receives only its own credential. No KryptNode
  storage, shared data, keys, CSVs, model weights or ciphertext payloads are mounted.
- API is non-root, read-only, drops capabilities and disallows privilege escalation.
  Local API publication binds `127.0.0.1:8001`; internal DB transport explicitly
  disables TLS for local-only use. API ingress bridge allows ordinary egress;
  this is not a production network policy or a universal egress-denial guarantee.
- Structured request log fields are allowlisted; arbitrary path, query, headers,
  body, request-supplied correlation IDs and exception text are omitted.
- Real driver authentication failure returns generic 503 without its supplied
  password in response/logs. Unhandled exceptions/validation inputs are redacted;
  malformed request correlation headers are replaced with server UUIDs.
- Logs from the actual Compose lifecycle are scanned against all three generated
  credentials, with no matches. Health/readiness remain independent during outage.

## Limitations and stop conditions

No OIDC validation, tenant isolation over business tables, CSRF/session protection,
rate limiting, HTTP deployment TLS, RLS, audit/outbox persistence, tamper-proof audit,
KMS, backup service, production secret rotation or node orchestration is implemented.
There are no business endpoints that could rely on these absent capabilities.
Application-log checks are bounded to the tested paths; arbitrary future code and
external infrastructure log pipelines are not certified.

Native startup probes and Docker WSL tests are local validation; hosted exact-head
checks have not run. A new high/critical finding, external exposure, changed trust
input, dependency drift, new endpoint or missing boundary requires fresh review.
Do not use M8-SEC-001/002 for M9. Do not publish into the current legacy CI surface
until its risks and scope are explicitly resolved. No merge/deployment is approved.
