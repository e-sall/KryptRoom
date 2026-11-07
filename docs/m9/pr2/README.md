# M9-PR2 — Identity & Organizations

Local implementation candidate, based on `dev` at
`d8a5c0aa7ed845c31bd2ff40c1b3491246c6cf83`. Publication, independent PR2 sign-off,
hosted CI, merge and deployment remain separate gates.

The complete 21-section Architect specification was read in order. Its original
export SHA-256 is `17a076581b6e3b8c7ffba1c687f86f4ce22cb36138feb456698764f46d3932a8`;
the four supplied chunks concatenate byte-for-byte to that export. The portable
review package contains this reference and its verification inventory.

Implemented surfaces:

- Real confidential OIDC Authorization Code + PKCE S256 against pinned Keycloak.
- Internal identities keyed exclusively by exact `(issuer, subject)`.
- Controlled organization requests, separate operator approval and enrollment.
- Current PostgreSQL RBAC, transaction-local RLS and serialized role/revocation changes.
- Server-only Next.js BFF, opaque cookies and encrypted PostgreSQL token storage.
- Signed backchannel logout, session expiration, concurrent refresh and fail-closed IdP handling.

There is no Room, RoomState initialization, invitation service, crypto execution,
reveal, proof or anchoring API. M8 previews remain disconnected synthetic views.

See [implementation](IMPLEMENTATION-REPORT.md), [security](SECURITY-REVIEW.md),
[acceptance](ACCEPTANCE-RESULTS.md), [architecture compliance](D1-D10-COMPLIANCE.md)
and [migration procedure](MIGRATIONS.md).

## Local reproduction

Use a disposable native Linux checkout, not a DrvFS directory. Docker Engine and
Compose supporting `!reset` are required. The fixture controller needs permission
to project UID-owned secret files and manage its own disposable containers.
Runtime API, migrator, BFF and browser processes remain UID 10001; Keycloak uses
its official UID 1000 and PostgreSQL its official UID 999.

After installing the hash-locked Python 3.12 toolchain, from `services/control-api`:

```sh
python scripts/local-secrets.py
python scripts/compose-acceptance.py
# Remove this disposable foundation fixture before reusing its loopback port.
docker compose --profile test down --volumes --remove-orphans
sudo "$(command -v python)" scripts/pr1-upgrade-acceptance.py --disposable
sudo "$(command -v python)" scripts/identity-stack-acceptance.py --disposable
```

The identity fixture binds PostgreSQL 5435, API 8001, Keycloak HTTPS 8444 and BFF
3004 exclusively to loopback. It is not a production Compose configuration.
The final command removes only its named disposable stack and database volume.
Never point these acceptance commands at a database containing real identities.

For an interactive **local** fixture, provision credentials with the scripts,
then use `docker compose -p kr-m9-pr2-real -f compose.identity.yml up -d api keycloak bff`.
Provisioning requires `docker compose -f compose.identity.yml run --rm identity-prepare`
after building its image. Browser access to the self-issued test certificate
needs explicit local trust. Tests pin only that fixture's public key; general TLS
verification is not disabled. The certificate expires after two days. Rotation is
an explicit operator action, not an automatic overwrite.

The frontend tooling disposition is local-only and expires at
`2026-11-07T06:45:07Z`. Recheck [its exact scope](SECURITY-DISPOSITION.md) before
frontend validations. It authorizes no hosted CI, publication, merge or deployment.
