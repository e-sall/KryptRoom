# M9-PR2 security review — implementation evidence, not independent approval

Independent PR2 reviews by 01 and 04 remain required. PR1 approval is not reused
as approval of these new authentication/session/authorization surfaces.

## Enforced boundaries

- External authentication is an exact issuer/subject pair, not an email/domain/group.
- The Control API validates signed access tokens and live introspection independently
  of the BFF, and reads current PostgreSQL user/organization/membership state.
- Business roles confer no execution, decryption, reveal, proof or anchoring right.
- Registration grants no active authority. Normal users cannot invoke operator approval.
- Organization changes use scoped SQL, RLS, user/organization locking and strong versions.
- BFF SQL credentials cannot read memberships; API credentials cannot read BFF tokens.
- Browser storage has no access/refresh token. Server token envelopes use mature AES-GCM;
  their keys are separate from the database and from the keyed session digest key.
- Callback state/nonce/PKCE, cookie rotation, CSRF, logout, expiry and refresh are tested
  with real Keycloak/PostgreSQL/Next paths as well as focused unit negatives.
- Runtime logs expose allowlisted route/status/correlation metadata, not credentials.
  The acceptance scanner compares actual decrypted synthetic token values against
  complete container logs and served client artifacts without printing those values.

## Privilege model

The API, migrator and BFF use UID 10001. PostgreSQL/Keycloak retain their official
separate users. Private source credentials are 0600; projections are 0400 inside
0700 UID-owned consumer directories. The offline preparer may assign ownership;
it is not an API execution identity.

The API, BFF and operator database roles are distinct non-superuser/NOBYPASSRLS
logins. The NOLOGIN RLS guard has selected table privileges and fixed-search-path
functions, not a general query interface. The trusted migrator owns schema/DDL
and can transfer helper ownership; its higher privileges are not runtime authority.
Database administrators and a compromised migration credential are outside the
application-level RLS guarantee. Events are append-only to application roles,
not cryptographically immutable against a database administrator.

The browser acceptance container has no Docker/host CLI/SQL/operator/key access.
An initial proposal to mount Docker into it was rejected by automatic approval
review and was not executed. The implemented controller/browser split avoids that
grant. Metadata reads use O_NOFOLLOW/fstat; acknowledgements use O_EXCL/O_NOFOLLOW.

## Dependency disposition

The raw audit reports and exact manifests/locks are in the portable package.
Python runtime/development and root npm findings are reported from fresh audits.
Frontend findings remain visible: eight moderate dependency findings derived from
one minimatch advisory, plus ESLint 9 EOL. They are **not fixed** by this PR2 work.
Production npm audit reports zero findings; this is not proof that every embedded
or served component is vulnerability-free. The known Next/nft copy/build paths
remain in the disposition. No visitor-controlled glob route has been demonstrated;
that absence is not a proof of inexploitability.

The [official advisory](https://github.com/advisories/GHSA-g3hv-75wg-m249) and
[ESLint support policy](https://eslint.org/version-support/) support this residual
tooling assessment. The strict ESLint 10 / official Next/React/import/a11y chain
probe failed peer resolution; no force install, incompatible override, audit fix
or audit suppression was used. Existing package versions were preserved when
adding BFF dependencies. Linux optional-dependency lock metadata was repaired
and strictly installed/audited in an isolated probe.

`M9-PR2-SEC-001` is the new explicit Founder disposition, solely for trusted,
non-public **local frontend validation**, recorded `2026-11-06T06:45:07Z`, expiring
`2026-11-07T06:45:07Z` (Toronto Nov 7, 01:45:07). It covers neither M9 runtime
dependencies nor any new vulnerability, hosted CI, push, PR, merge or deployment.
No old M8/M9 exception is renewed or reused. Stop affected work on expiration,
high/critical findings or a material change of exposure.

## CI and publication boundary

The new identity workflow is additive and preserves an explicit non-applicability
result. Its frontend audit gate is strict at moderate severity: the present eight
findings would block it **before building**. The local-only disposition does not
bypass that gate. Hosted execution requires a compatible correction or a separate
explicitly approved, bounded CI disposition and corresponding reviewed control.
No hosted success is claimed before separate publication authorization.

The existing M8 workflow remains independent and would also run lint/build/browser
checks for this shared frontend delta. The identity workflow's strict gate cannot
stop a different workflow. Consequently **no publication or hosted execution is
authorized by the local disposition**, even if one workflow would fail early.
That exposure must be resolved explicitly before the Founder authorizes a push.

BFF/shared frontend dependency changes select both frontend and M9 consumers.
Core/shared-security/unknown/workflow changes remain conservative. The classifier
and new recipe themselves therefore remain Core-relevant; no required check is
removed or silently exempted. Existing proof/chain workflows are unchanged, and
their current path/event rules do not select Groth16 or live anchoring for this diff.

## Remaining limits

This is a local/CI operational foundation, not a production multi-company service.
Production IdP, legal organization verification, KMS/key rotation, retention,
incident operations and deployment hardening remain separate decisions. No full
container-OS vulnerability certification, Firefox/real-device certification or
penetration-test claim is made. Keycloak provider-side revocation propagation
outside the observed local scenario is not claimed instantaneous. No M1–M7
computation, cryptographic authorization or production rollout is introduced.
