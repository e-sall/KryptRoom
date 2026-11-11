# M9 PR4 — local multi-organization collaboration

Base: `b2cf2b5d124d9b29a60a93530cccc6fc367fe616`. Isolated branch
`feat/m9-pr4-collaboration`. Local implementation only; publication NO-GO.

## Behavior and contracts

A Room has one owner organization and at most one pending/accepted partner.
The owner OWNER/ADMIN invites an ACTIVE pre-registered organization by UUID and
can revoke pending/accepted participation. The target OWNER/ADMIN accepts/rejects
a pending invitation or leaves an accepted participation. Active partner members
then read shared Room metadata; only owner OWNER/ADMIN edits it. No ownership
transfer, private-data access, crypto consent or execution is introduced.

- POST `/api/v1/rooms/{roomId}/invitations`: body `organizationId`,
  `targetOrganizationId`; Idempotency-Key required; 201 and version ETag.
- GET `/api/v1/organizations/{organizationId}/room-invitations`: OWNER/ADMIN
  only, bounded `limit`/UUID `cursor`, both sent and received invitations.
- PATCH `/api/v1/organizations/{organizationId}/room-invitations/{invitationId}`:
  body `roomId`, action `accept|reject|leave|revoke`; strong If-Match required.
- GET `/api/v1/rooms/{roomId}/participants`: visible Room's owner and accepted
  partner UUIDs only, no private organization record or membership directory.
- Existing Room list includes accepted shared Rooms. Existing detail read uses
  RLS; metadata update still requires authority in the owning organization.

Invitation UUIDv4 IDs are not bearer credentials. Every request uses existing
real token validation/introspection and current PostgreSQL authority. Pending
invitations never grant Room read access. Unknown/foreign resources use generic
errors; no raw SQL exceptions or target private data are returned.

## SQL, concurrency and lifecycle

Migration 0004 adds forced-RLS invitation/event tables. Runtime logins have no
direct writes to these tables and no RLS bypass. Narrow NOLOGIN-guard functions
use a fixed search_path, check actor authority, lock the Room and recheck live
authority after waits. Organization mutation locks reuse PR2 revocation ordering.
The temporary schema CREATE grant used to transfer function ownership is revoked
within the migration transaction. SQL guards never accept client status/role.

Creation retries bind actor + Room + key + target. Conflicting targets fail.
Transition retries already in the requested terminal/current state return without
new events, even with the original If-Match. Other stale versions fail 412;
invalid transitions or a second pending/accepted partner fail 409. Events append
atomically with mutations and are not readable/rewritable by the app login.
They are application history, not a cryptographic proof or production audit log.

Revocation denies subsequent requests. Operations ordered before a revocation
commit can finish under their existing authority; there is no retroactive recall
of metadata already read. Waiting mutations recheck authority/current invitation.

Upgrade: existing restricted migrator runs `alembic upgrade head`. No prior
migration changes. Downgrade: `alembic downgrade 0003_persistent_rooms` restores
owner-only Room visibility, preserves Room metadata, and **deletes PR4 invitation
and event history**. Back up/export history before a deliberate non-test rollback.
No automatic downgrade or runtime schema ownership is granted.

## UI/BFF

The existing same-origin session BFF gains exact route/method allowlist entries.
It keeps opaque cookies, encrypted server-side OAuth tokens and CSRF checks.
M8 Card/Button/TextField components show pending/accepted/rejected/revoked/left,
loading/empty/error, invitations pagination and explicit owner/read-only roles.
`/app/rooms/invitations` is an organization-manager inbox. Partners open existing
Room details with disabled metadata edits. An invitation targets a known UUID;
there is no public organization directory, email sender or background notification.
No homepage/design or preview changes. `headStateId` remains null throughout.

## Executed evidence

- Native Linux PostgreSQL 17: 8 PR4 cases and 8 affected Rooms regressions PASS.
  Includes direct RLS/grants, member/admin roles, idempotent event counts, malformed
  versions, observed distinct-connection lock waits, revoke vs accept, authority
  revoked while waiting, downgrade/re-upgrade and Alembic metadata drift check.
- Python contracts/packaging: 19 PASS. Ruff and strict mypy PASS.
- Frontend affected unit/component/BFF security tests: 27 PASS. Targeted ESLint,
  TypeScript and webpack build PASS.
- Real installed Edge Chromium: one complete Keycloak PKCE → BFF → FastAPI →
  PostgreSQL test PASS; A/B/C identities, UI invite/accept/reject/leave/revoke,
  cross-org/forged mutation/CSRF denial, read-only partner, reconnect, API restart
  and independent direct SQL persistence assertion. No intercepted/mock responses.

The source and test logs are bound to the final commit in the flat external QA
handoff manifest. Frozen PR2/PR3 suites outside affected regressions were reused,
not claimed as newly run. Hosted CI, Firefox/WebKit, real devices, full identity
regression and heavy cryptography: NOT RUN. No Groth16 or chain transaction.

## Limits and next gate

Inherited eight moderate frontend minimatch/Next-nft findings and ESLint 9 EOL
remain unresolved. Dependency/lockfile bytes and audit controls are unchanged;
PR2 audits/reviews were not rerun, findings are not claimed fixed or newly audited.
No old exception is renewed or reused, and local QA is not hosted publication
approval. Independent QA04 of this delta and separate security/enforcement and
Founder authorization remain mandatory before any publication.

The local build uses existing dependency junctions. Next warns that 27 external
trace files are outside outputFileTracingRoot; this local `next start` acceptance
does not validate a standalone production bundle. No production service, transport
security certification or real-company data is involved.
