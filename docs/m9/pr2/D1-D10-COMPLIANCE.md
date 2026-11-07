# D1–D10 implementation mapping

Reference: complete Architect export, original SHA-256
`17a076581b6e3b8c7ffba1c687f86f4ce22cb36138feb456698764f46d3932a8`.
The export restores the full contract; the earlier truncated summary is not used
as a substitute for sections 8–21.

- **D1 — Modular monolith.** `services/control-api/src/kryptroom_control` extends
  PR1 FastAPI/SQLAlchemy/Alembic; `identity_schema.py`, `identity_api.py`,
  `organization_service.py` and `operator.py` separate responsibilities. No broker
  or additional application microservice is added.
- **D2 — External OIDC.** `oidc.py`, `scripts/keycloak`, `apps/web/src/server/auth`
  and `compose.identity.yml` provide actual Keycloak code/PKCE/introspection/logout.
  Production IdP selection is still open.
- **D3 — Organization tenancy.** `organizations` and `organization_memberships`,
  scoped queries and transaction-local RLS implement organization isolation.
  The two-organization Room contract belongs to PR3; no Room is fabricated here.
- **D4 — Double policy approval.** Not implemented early. PR2 organization approval
  is controlled enrollment, not bilateral policy or cryptographic approval.
- **D5 — No cryptographic initialization.** API inventory has identity/organization
  metadata and health only. RoomState initialization remains outside M9-PR2.
- **D6 — Controlled enrollment.** Normal registration is PENDING_REVIEW. A separate
  restricted operator credential activates the nominated owner atomically and
  enrolls additional known internal identities. Invitation flows remain PR4.
- **D7 — Server authorization.** PR1 BusinessAuthorizer contract/DenyAll remain;
  the configured real service uses current database state, role/context checks,
  locks, versions, default denial and additional RLS. Client roles are not authority.
- **D8 — Audit boundary.** Bounded access events share mutation transactions and
  lack application UPDATE/DELETE grants. No generalized PR6 outbox or crypto proof
  is claimed.
- **D9 — Preview isolation.** New `/auth` and `/bff` server routes do not connect
  `features/marketing`, synthetic catalog/preview components or `/demo` to execution.
  `tests/auth-boundary.test.ts` and the retained M8 assertions check this separation.
- **D10 — Incremental delivery.** Dedicated local branch from the required baseline,
  phase commits, exact-source tests/audits and portable review evidence. No push,
  PR opening, merge, main change, deployment or PR3 implementation is authorized.

Founder additions are retained: controlled pilot registration; absolute separation
between business governance and cryptographic authority; no automatic acceptance
of new high/critical dependency debt. PR2 requires new independent review.
