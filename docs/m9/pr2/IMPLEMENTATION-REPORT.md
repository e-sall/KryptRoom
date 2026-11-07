# M9-PR2 implementation report

## Scope and baseline

Baseline: `d8a5c0aa7ed845c31bd2ff40c1b3491246c6cf83`.
Branch: `feat/m9-identity-organizations`. This report describes a local candidate;
the final commit inventory and exact source hashes accompany the review package.
No push, PR opening, merge, main promotion, deployment, Groth16 or blockchain
operation is part of this implementation.

## A — External identity

`oidc.py` uses PyJWT with fixed RS256, exact issuer/API audience/permitted BFF,
required access-token type, bounded clock skew, signature verification, bounded
discovery/JWKS and one unknown-key refresh. Every protected call also performs
live provider introspection. A verified identity contains no organization authority.
The local/CI provider is Keycloak 26.8.2, digest
`sha256:3879c623248408de29a5303178b5816c77e8dfef3890c361f8c0bbeaa979ba3b`.
Realm imports render only explicitly declared synthetic placeholders; they do not
enable general Keycloak system-variable expansion.

## B–D — Persistence, controlled registration and authorization

`identity_schema.py` defines users, identity links, organizations and memberships,
plus bounded security/idempotency records and the separate `bff_auth` schema.
UUIDv7 comes from the pinned `uuid6` library. Migration 0002 preserves migration
0001 and its foundation marker. Identity races serialize on the exact issuer/subject
pair. Email and names remain presentation metadata, never enrollment evidence.

Registration atomically creates a pending organization, pending nominated owner,
idempotency record and event. `Operator`/`operator_cli` require the separate
`kryptroom_operator` credential, case and attribution; no approval HTTP endpoint
exists. Owner activation and organization approval commit together.

The API independently validates authentication, locks the active user for the
request transaction, establishes a transaction-local internal user context and
queries current active membership. Unknown/cross-tenant resources return 404;
accessible but insufficient roles return 403. Creation requires Idempotency-Key;
mutations require an exact strong If-Match version. Strict request models reject
caller-supplied approval/status/ownership fields.

RLS is additional protection. API/BFF/operator logins are non-owner, non-superuser,
NOBYPASSRLS roles. A separate **NOLOGIN** guard owns narrowly scoped fixed-search-path
helpers to avoid recursive policies. Its temporary schema CREATE grant is revoked
after migration; migration credentials are never given to the API.

## E–F — BFF, sessions and revocation

`apps/web/src/server/auth` and the explicit `/auth` and `/bff/api/v1` route handlers
use openid-client, jose and node-postgres. Browser sessions contain only a random
256-bit opaque handle. PostgreSQL stores its keyed HMAC digest. Access/refresh
tokens are AES-256-GCM envelopes, bound to key ID, purpose and session lookup,
with separately provisioned encryption and HMAC keys.

Production-profile cookies use `__Host-kr_sid`, Secure, HttpOnly, SameSite=Lax,
Path=/ and no Domain. The explicit loopback HTTP fixture uses `kr_dev_sid`;
it is not evidence of a production HTTPS BFF deployment. OIDC transactions are
browser-bound, encrypted, five-minute and consumed once before code exchange.

Mutations require session, bound CSRF token, exact Origin, compatible Fetch
Metadata, JSON content type and an explicit method/path allowlist. Browser
Authorization/identity/Host headers cannot choose the upstream or principal.
Authenticated responses are private/no-store and retain correlation identifiers.
Next incoming URL logging is disabled to avoid recording callback codes.

Session limits are idle 30 minutes, absolute eight hours and provider access-token
target five minutes. Refresh serializes on the session row; invalid refresh or
authenticated-envelope failure revokes the session. Signed provider logout checks
issuer, audience, RS256, event, issued-at age and replay ID before persisting revocation.

Membership mutations serialize on the organization row and re-evaluate authority
after locking. Effective-owner counting excludes suspended users. Suspending the
last effective owner also suspends the organization atomically; reactivation without
an effective owner is refused. Recovery of such an ownerless suspended pilot is
an explicit operator maintenance/review matter, not an automatic grant.

## G — Delivery and boundaries

The real fixture uses PostgreSQL 17.11, Keycloak, FastAPI and the Next standalone
image on native Linux. Its browser is UID 10001, read-only, without Docker socket,
host CLI, SQL/operator credential or server token key. A separate trusted controller
performs only fixed pilot provisioning/lifecycle actions. Its bounded metadata
channel refuses symlinks and preexisting acknowledgements.

M8 production/preview components, SVGs, animations, `/demo`, portrait and design
tokens are unchanged. Two old global no-I/O tests now distinguish exactly eight
new server entrypoints; new negative import/allowlist tests preserve the M8 boundary.
Existing Core code, contracts, fixtures and historical proof/anchor evidence are
unchanged. No Core cryptographic validation is relabeled as newly executed here.

Validation results, reuse boundaries and remaining gates are recorded separately
in [ACCEPTANCE-RESULTS.md](ACCEPTANCE-RESULTS.md) and the portable source manifest.
