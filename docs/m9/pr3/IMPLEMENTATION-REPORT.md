# M9-PR3 — Persistent Rooms, local only

Base: `75eb1ed5303851e7d9077f60665bf1032d56a6c6`, stacked on approved local PR2.
Branch: `feat/m9-pr3-persistent-rooms`, isolated managed worktree. Original PR2
branch and its next-env.d.ts edit are preserved. No publication or PR4 work.

## API and invariants

POST `/api/v1/organizations/{organizationId}/rooms`: required Idempotency-Key,
bounded displayName/description, active OWNER/ADMIN only. Transactionally writes
Room, creation snapshot and metadata event. Same actor/org/key and normalized
payload replays the original 201 snapshot; conflicting payload returns 409.
Current authority is checked before replay; records have no automatic expiry.

GET that collection provides bounded keyset pagination to active organization
members. GET `/api/v1/rooms/{roomId}` reads only an authorized Room. PATCH that
resource requires OWNER/ADMIN, nonempty non-null display metadata and strong
version If-Match: missing header 428, stale/malformed value 412. Foreign resources
return 404; insufficient own-tenant role returns 403. PR2 data/correlation_id,
no-store and ETag conventions are preserved.

Rooms are DRAFT metadata owned by the founding organization, not active two-party
collaborations. Invitations, second organization and Room-specific membership are
PR4 work. No activation/delete/frontend/governance/cryptographic API is added.
`headStateId` remains NULL by SQL CHECK, with no application write grant or input
field. No RoomState is fabricated or initialized.

Existing OIDC signature/issuer/audience/introspection and PostgreSQL identity/
membership authority are reused unchanged. Migration 0003 enables and forces RLS
and explicit grants in the same transaction. No actor, foreign tenant, pending or
revoked membership, or suspended organization grants access. Operator/BFF cannot
directly read Rooms. App cannot delete or reassign Rooms or set head state.
The API-established transaction actor remains trusted as in PR2; this does not
claim security against compromise of that SQL role.

Mutations acquire the existing organization lock, recheck authority, then lock/
re-read the Room before version checking. This serializes different Room writes
within one organization, intentionally acceptable for the bounded pilot.
Migrations 0001/0002 and PR2 RLS remain byte-identical. Downgrade 0003 drops only
the new tables and loses their data: use only for disposable fixtures or with an
approved backup/migration plan. Readiness now requires revision 0003.

## Executed validation

- 51 pytest cases PASS on Python 3.12.16/native Linux: wire/foundation/identity
  contract regressions, packaging privacy, 5 PostgreSQL foundation cases and
  8 Room PostgreSQL cases. Real PostgreSQL17/restricted roles, no SQLite mock.
- Deterministic distinct-connection tests observe pg_blocking_pids: concurrent
  If-Match conflict and revocation before mutation resumes. Also concurrent
  idempotent creation, OWNER/ADMIN/member rules, raw SQL RLS/grants, pending/
  suspended/revoked denial, pagination, rollback/repeated upgrade/schema drift.
- Real Keycloak 26.8.2 Authorization Code + PKCE S256 over verified local TLS:
  actual HTTP creation/read/update, cross-organization denial, inactive access
  token refused by actual introspection. No tokens reach a browser.
- Restart the API, then fresh controller process and real login: same persisted
  Room/version reloads with headStateId null. PostgreSQL volume is retained.
- API UID10001:10001; runtime logs checked against synthetic credentials/JWT
  patterns without matches. The separate trusted fixture controller reads its
  synthetic credentials; its privileges are not API or browser privileges.
- Ruff, strict mypy and source/wheel packaging checked on the final source delta.
  No new dependency, lockfile, workflow, classifier, crypto fixture or M1-M8 change.
  No PR2 audit/review cycle, Groth16 or heavy cryptographic integration repeated.

Docker CLI was available under WSL but Compose was absent. Tests reused cached
PR2 Python images with current source mounted read-only, and original pinned
PostgreSQL/Keycloak configurations, in a dedicated native Linux fixture. No
install, frontend service or image build ran; fresh image-build validation is not
claimed. WSL stopped the first stack between commands; grouping startup/tests in
one Linux lifetime fixed this infrastructure failure. Early failing driver traces
could include synthetic credentials; exported diagnostics are redacted and the
disposable fixture is retired after acceptance.

## Reproduce and targeted review

Unit: select test_rooms.py, test_identity_contracts.py, test_foundation.py and
test_packaging.py. PostgreSQL: select test_postgres.py and test_rooms_postgres.py
with the existing CONTROL_TEST_POSTGRES and separate-role password-file fixture;
missing configuration fails rather than silently skips.
Run tests/rooms_http_acceptance.py in the trusted native Linux synthetic fixture
(loopback 5435/8001/8444), restart API, then its --reload mode in a fresh process.
Exact local fixture commands, sanitized outputs, source/image IDs and Git delta
are in the compact external M9-PR3-LOCAL-20261111 evidence directory.

Hosted CI, public deployment and browser/BFF Room integration are NOT RUN / not
authorized. Existing PR2 publication gates remain NO-GO. **READY FOR LOCAL QA**:
04 should review RLS/grants, authority after waits, idempotency/ETag behavior and
the actual IdP/API restart chain. This is not a hosted or production certification.

Static parent limitation: test_identity_delivery.py still asserts the former
inline `npm audit --json --audit-level=moderate` recipe, which the approved parent
gate replaces with a helper. That unrelated full-suite delivery check was not
executed, weakened or patched here. Its recipe/assertion alignment needs a separate
PR2 publication follow-up; the 51 focused PR3 cases do not certify that full suite.
