# M9 PR5 — local operational hardening

Base: `c209806ff445e39dbc61d47d601dc9db8a6c9725`. Branch
`codex/m9-pr5-hardening`. Local QA candidate; publication NO-GO.

## Migration and recovery

0005_action_guard is a frozen CREATE OR REPLACE snapshot of the approved guarded
function. PostgreSQL retains its existing owner, SECURITY DEFINER configuration,
search_path and ACL. Fresh installations and databases that already recorded the
old vulnerable 0004 both receive it. No table reset or earlier migration edit.
The test fixture for the old function is SHA-bound to the historical 3fdff1b source.
Tests preserve exact Room/invitation/event rows, including pending/accepted/revoked.
0005 downgrade is intentionally a no-op: it never reinstates the disclosure.

0006_room_history adds transaction-bound Room create/update history and projects
invitation events. Historical collaboration IDs/times are copied exactly; absent
historical Room events are not fabricated. All tables have forced RLS and runtime
logins lack direct history access. Fixed-search-path NOLOGIN-guard functions and
triggers append events; failure rolls back the business operation. Temporary schema
ownership-transfer permission is removed in the same migration transaction.

For a backed-up local database, run the restricted migrator `alembic upgrade head`
before API readiness. Check head `0006_room_history`, application roles and smoke
requests. Transactions serialize business changes under the existing PR2/PR4 rules.
This is a maintenance/transactional migration, not demonstrated zero-downtime DDL.
Downgrade 0006 deletes **new** operational history and restores the previous schema;
old collaboration history, invitations and Rooms remain. Export new history first.
Restore a consistent PostgreSQL backup into an isolated database when recovery of
that history is required; backup/PITR automation is not implemented or certified.

## Operational interface

GET `/api/v1/rooms/{roomId}/history` uses current Room access plus current manager
authority. Owner OWNER/ADMIN sees that Room's history. An accepted partner's
OWNER/ADMIN sees its current invitation events and Room events since acceptance;
it sees no past partner history. Ordinary members/outsiders are denied. Cursor
pagination orders by timestamp and event UUID, with no actor-user ID, request key
or Room metadata body in the public projection. Revocation denies later requests.
Existing states remain DRAFT and headStateId remains null. No crypto authority.

The existing BFF allowlist adds only GET history; opaque sessions, current API
authorization, CSRF and default-deny remain. M8 components expose history on demand
to managers. A demonstrated repeated-selection event could leave forms/inboxes in
Loading without a dependency change; same-value selection is now a no-op, and
unit/real browser regression assertions preserve the original capabilities.
History remounts per Room to avoid retaining another Room's displayed history.

BFF `/health/live` does not depend on other services; `/health/ready` requires
DB, API readiness and the exact live OIDC issuer, with bounded requests and generic
503s. Existing API request logs keep only correlation ID, server route template,
method, status and duration. Events contain business identifiers, not private data.
They are not cryptographic proof, independent audit certification or malicious security.

## Packaging actually executed

Clean native Linux build: `docker build --pull=false --target runtime -t
kr-m9-pr5-web-runtime:local -f apps/web/Dockerfile.identity apps/web`.
The pinned Node 22.23.4 image runs locked strict-peer npm ci and Next build.
The runtime copies standalone/static/public only, runs `node server.js` as UID10001,
read-only/cap-drop ALL, and has no source or node_modules bind mount. Only synthetic
credential/CA mounts and a bounded writable cache are used. No `next start` proof.
The earlier 27 external-file warnings were due to a Windows junction; the clean
build has no such warnings. No outputFileTracingRoot widening or design change.
The runtime input hashes, image ID and actual container image ID are in QA evidence.
The API is also built from its hash-locked Dockerfile and executed read-only as
UID10001 with credential/CA mounts only, no source/migration/test mounts. The final
real browser suite exercises both self-contained images together.
This is a locally executed deployable artifact, not permission or security approval
to deploy. There is no public listener, production secret or real-company fixture.

## Acceptance

- 26 native PostgreSQL tests PASS: fresh/legacy migrations, owner/ACL/data,
  bounded history, RLS, atomic rollback, concurrent revoke/If-Match and readiness.
- 43 affected backend contracts/error/privacy/packaging tests PASS; Ruff/mypy PASS.
- 35 targeted frontend unit tests PASS; ESLint, TypeScript and build PASS.
- Three real Edge Chromium/Keycloak/BFF/FastAPI/PostgreSQL tests PASS on the
  standalone: Rooms creation/conflict/reconnect, A/B collaboration/C isolation,
  scoped history, revocation, all-service restart and persisted data/history,
  API/IdP outages and recovery, liveness/readiness and real session expiration.
- Hosted CI, heavy cryptography, Groth16, chain transactions, WebKit/Firefox,
  real devices, production TLS/cookie deployment, backup restore/PITR and OS image
  vulnerability scanning: NOT RUN. No previous QA is relabelled as this candidate's QA.

See RELEASE-GATES.md. Independent QA04 and separate publication decisions remain.
