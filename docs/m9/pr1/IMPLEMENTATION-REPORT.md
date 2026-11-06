# M9 PR1 — Control API Foundation

Review date: **2026-11-03 America/Toronto**. Local branch:
`feat/m9-control-api-foundation`. Verified remote/local dev baseline:
`7fde54f86b8df11d162eb317414dc1d2f932b70a`.

**Implementation prepared for independent review locally. Publication: BLOCKED by
the legacy CI/security scope described below. No push, PR, merge or deployment.**

## Architecture and implemented scope

The founder supplied the missing D1–D10 section directly after the chat retrieval
tool truncated the architecture report at 20,000 characters. The restored decisions
and this mission are authoritative: modular monolith; external OIDC/Keycloak in
PR2; Organization tenancy; two organizations per future Room; bilateral governance;
no RoomState initialization until M10; pre-registered invitation targets; contextual
server authorization with default denial; future transactional audit/outbox;
isolated M8 previews; eight incremental PRs with no main merge in M9. Organization
enrollment is controlled for the pilot. Business approval is never crypto authority.

Implemented Python 3.12.16, FastAPI 0.162.0, Pydantic 2.14.2/settings 2.16.2,
SQLAlchemy 2.1.7, Alembic 1.20.1, psycopg 3.3.7 and PostgreSQL 17.11.
The synchronous database API runs in synchronous FastAPI endpoints. No event-loop
blocking DB call, global session, automatic migration or business service is added.

- `/health/live`: process health, independent of the database.
- `/health/ready`: PostgreSQL major 17, exact migration head and technical marker.
  Missing/unavailable/incompatible schema and connection/authentication failures
  return generic 503, while liveness remains 200.
- OpenAPI 3.1 describes exactly those two GET operations. JSON serving is operator
  opt-in; interactive documentation/CDN pages are absent.
- Shared immutable wire models, bounded cursor pagination, opaque UUID IDs,
  response/error conventions and generated correlation IDs are prepared.
- Request logs allow only server-defined metadata. No query, arbitrary URL path,
  header, body, database credential or exception text is logged by the service.
- Separate schema-owner and SELECT-only runtime roles; bounded connections,
  SQL statement/connect timeouts, explicit commit/rollback and disposal.
- Alembic revision `0001_foundation` stores only a constrained technical singleton
  and timezone-aware timestamp; no sensitive, identity, business or crypto rows.
- Typed ports for Identity, Organizations, Rooms, Invitations, Authorization,
  Governance and Audit. Only the default-deny authorizer has concrete behavior.
  There are no fake business implementations or crypto adapters.
- Official digest-pinned Python/PostgreSQL images, hash-locked Python packages,
  dedicated local Compose, non-root/read-only API, distinct mounted credentials,
  database internal network and API-only loopback ingress.

The [service guide](../../../services/control-api/README.md) documents exact setup,
configuration, migration, rollback, credential rotation boundaries and test commands.

## Execution and corrections found during validation

See [acceptance results](ACCEPTANCE-RESULTS.md) and [security review](SECURITY-REVIEW.md).
Windows Python/PostgreSQL were isolated under the parent workspace, not installed
system-wide. A pre-existing Ubuntu WSL Docker daemon was then used with the
official Compose 5.7.0 plugin downloaded into the workspace and hash-verified.
No system packages, group memberships or Docker daemon configuration were changed.

Real execution exposed and fixed the following issues before the local commit:

1. Setuptools editable building failed on the restricted Windows temporary path
   containing braces. Pinned Hatchling builds successfully on Windows/Linux.
2. Unit settings inherited integration credentials from the caller environment.
   The unit fixture now isolates its environment and restores it after each test.
3. Readiness queried the marker after detecting a wrong/absent migration revision.
   It now rejects that revision before querying the marker. Missing-table errors
   remain safely handled at the endpoint.
4. Docker accepted a port binding on an exclusively internal network but emitted
   `NetworkSettings.Ports={"8000/tcp":null}`. Internal health was 200 while host
   access failed. Only the API now also joins a bridge; the published address is
   still loopback, and the database/migrator/test network remains internal.
5. The minimal test image exposed an overly deep repository-parent lookup during
   collection. The lookup is now valid in both layouts. Pytest cache goes to tmpfs;
   transient startup connection resets are retried within the bounded probe loop.
6. The default source archive included ignored local runtime files. Explicit sdist
   allowlisting, wheel/source exclusions, component ignore rules and a regression
   now prevent this. No affected archive was published. Component Git attributes
   also preserve LF for reproducible Windows/Linux shell-script checkouts.

No assertion was weakened, no test was skipped, and no audit finding was suppressed.
Marker selection divides the 20 unit/static tests and five PostgreSQL tests; all
25 execute across the two groups. No Core execution was substituted or mocked.

## CI publication scope — not authorized by an M8 exception

New workflow: `.github/workflows/control-api-foundation.yml`, read-only GitHub
permissions, immutable action SHAs, Python 3.12.16, 20-minute bound, M9 paths only,
dev PR / dedicated feature push / dev push, with manual dispatch retained.
It runs locked install, consistency, lint/format/types, tests, unsuppressed audits,
build, real Compose/PostgreSQL lifecycle and disposable-container cleanup.

The existing classifier remains **core=true** for M9. No legacy trigger, condition,
proof recipe, fixture exemption or required test was altered. Exact scope analysis:

- Feature push: **M9 foundation + Private join**. Private join installs the existing
  root npm dependencies and runs real M2 because M9 is conservatively core.
- PR to dev: **nine workflows** — M9, M2, M2.5, M3, M4, M5 native, M6, M7 native,
  and M8 frontend. M8 frontend is selected by the new workflow/global-doc paths.
- Dev push after a future merge: those nine plus PSI, **ten workflows**.
- **Groth16 acceptance is not selected** by the exact M9 paths. The M7 live workflow
  remains manual-only. Mixed crypto changes still select proof/Core checks.

The baseline root audit still reports **three high package entries**. Its adm-zip
remediation belongs to the separate M8 promotion task and is deliberately not
copied here. M8 frontend still has its separately documented ESLint/minimatch
disposition. No M8 exception is used to authorize these jobs for M9.

Therefore publication is held: obtain a separate treatment of legacy tooling and/or
a narrowly reviewed routing decision that preserves mandatory regressions before
any push/PR. There is no exact-head hosted CI result yet. This is not a request to
disable crypto checks, reuse old proof results or accept security risks implicitly.

## Inventory and preservation

All implementation files are under `services/control-api`: project/three locks,
runtime/config/DB/wire/logging code, seven module ports, Alembic scaffolding and
one revision, Dockerfile/Compose, local tooling, README and automated tests.
One new M9 workflow and `docs/m9/pr1` are added. `CHANGELOG.md`, `TODO.md` and
`docs/DECISIONS.md` receive M9-only additions; prior entries remain intact.
The exact file inventory is in [evidence/validation.json](evidence/validation.json).

No M1–M8 implementation, frontend asset, cryptographic fixture, dependency manifest
outside M9, security exception, existing workflow or `ci_scope.py` changed. M8
promotion candidate/workspace are preserved. No `/run`, `/reveal`, `/decrypt`,
`/prove`, `/anchor`, login, Room or invitation endpoint exists. No M9 PR2 work,
Groth16, transaction, main change, tag, merge or public deployment occurred.

## PR2 recommendations, not implementation

Implement real external OIDC verification and controlled organizational enrollment,
with issuer/subject resolution and database-checked memberships. Decide production
IdP before deployment. Add authorization before exposing any business resource;
do not trust tenant headers/email domains. Add reviewed data migrations and
explicit DML grants for the new tables. Future audit/outbox must share transactions.
Keep all business and cryptographic authorization boundaries separate.
