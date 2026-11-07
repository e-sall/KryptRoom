# PR2 contract and privilege inventory

## API

All business routes are under `/api/v1`, with a verified Bearer access token,
current active internal user and database-scoped authorization. OpenAPI 3.1
declares typed success/error envelopes, HTTP Bearer, bounded pagination and
strict write models. Health routes remain independent of the IdP.

- `POST /auth/complete`: resolve `(issuer, subject)` idempotently; never enroll
  a user into an organization from token/email/domain/group claims.
- `GET /me`: own identity, active accessible organizations and own memberships.
- `GET /me/registrations`: only the caller's registration requests, paginated.
- `GET /organizations`: active accessible organizations, paginated.
- `POST /organizations`: Idempotency-Key required; creates pending registration
  and pending nominated owner atomically, returning 202 rather than active access.
- `GET /organizations/{organizationId}`: read an active authorized organization.
- `PATCH /organizations/{organizationId}`: non-security display name only;
  owner/admin plus strong If-Match required.
- `GET /organizations/{organizationId}/members`: owner/admin only, paginated.
- `PATCH /organizations/{organizationId}/members/{membershipId}`: owner only;
  exact version and last-effective-owner rules apply.
- `DELETE /organizations/{organizationId}/members/{membershipId}`: revoke,
  subject to role hierarchy, exact version and last-effective-owner rules.

There is no HTTP approval/provisioning API, unrestricted POST members, Room,
RoomState, run, reveal, decrypt, prove or anchor endpoint. The separate operator
CLI requires its own restricted SQL credential, attribution and case reference.

The BFF exposes `GET /auth/login`, `GET /auth/callback`, `POST /auth/logout`,
`POST /auth/backchannel-logout` and an explicit method/path-allowlisted
`/bff/api/v1/[...path]` proxy. Authorization headers supplied by the browser do
not choose its upstream identity. Signed backchannel notification is separate
from browser cookie/CSRF authentication. No M8 preview component calls these APIs.

## Role permissions

Every allowance requires active User, Organization and Membership at the time
of the protected transaction. Unknown actions default to denial.

- OWNER, ADMIN, MEMBER: read own organization and own membership.
- OWNER, ADMIN: list members and edit non-security organization metadata.
- OWNER: change roles, revoke admins/owners; never remove the last effective owner.
- OWNER, ADMIN: revoke ordinary members. An admin cannot modify another admin,
  an owner, its own role or any role through a crafted request.
- All business roles: denied organization approval, cross-organization grants
  and cryptographic operations. Room creation remains unimplemented.

Cross-tenant/unknown resources return 404; insufficient role within an accessible
organization returns 403. Missing mutation precondition returns 428; stale version
returns 412. Registration idempotency conflicts return 409.

## SQL and migration

Schema revision: `0002_identity_organizations`, following unchanged
`0001_foundation`. Business tables: users, identity_links, organizations,
organization_memberships, organization_access_events and idempotency_records.
BFF tables: sessions, oidc_transactions and logout_replays in `bff_auth`.

- `kryptroom_app`: nonowner/NOBYPASSRLS; scoped business grants, bounded helper
  EXECUTE, no BFF schema access, no direct operator approval-column update.
- `kryptroom_bff`: nonowner/NOBYPASSRLS; BFF table access only, no business role
  changes or organization-membership lookup authority.
- `kryptroom_operator`: nonowner/NOBYPASSRLS; reviewed enrollment/status columns,
  controlled membership provisioning and append-only attributed access events.
- `kryptroom_auth_guard`: NOLOGIN, selected business-table privileges and
  fixed-search-path SECURITY DEFINER helpers only. Its temporary schema CREATE
  grant is revoked. Runtime roles cannot assume it.
- `kryptroom_migrator`: trusted schema owner/DDL role; never an application credential.
- `kryptroom_keycloak`: separate Keycloak database credential.

Exact grants/policies/functions are reviewable in `0002_security.sql`; exact
tables/constraints/FKs/indexes in `0002_schema.sql` and `identity_schema.py`.
SQL defense does not protect against a database administrator or stolen migrator
credential. Access events are transactional application evidence, not proofs.

## Identity configuration and sessions

The fixture trusts only `https://127.0.0.1:8444/realms/kryptroom-dev`, API audience
`kryptroom-control-api`, permitted BFF `kryptroom-web-bff` and RS256. Each protected
API call also performs live introspection. Unknown key refresh is bounded.
The full fixed development realm template and digest are supplied for review.

Session defaults: opaque 256-bit browser handle; HMAC lookup; AES-256-GCM tokens
with purpose/key/session-bound AAD; separate encryption/HMAC keys; five-minute
single-use OIDC transaction; 30-minute idle and eight-hour absolute expiration.
Refresh serializes on the session row. Production-profile cookie policy is
Secure/HttpOnly/SameSite=Lax/Path=/ with `__Host-` naming and no Domain. The
loopback HTTP acceptance profile uses an explicitly different development name.
No external production TLS deployment is asserted by the local fixture.
