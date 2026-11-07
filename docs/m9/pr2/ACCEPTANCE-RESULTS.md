# M9-PR2 acceptance results — local review candidate

Baseline: `d8a5c0aa7ed845c31bd2ff40c1b3491246c6cf83`.
Branch: `feat/m9-identity-organizations`. Exact final commits, cumulative diff,
Git-blob hashes and evidence manifests accompany the portable review package.
No hosted CI or independent PR2 approval is implied by these local results.

## Authoritative immutable-source execution

Native Linux tree: `5ee4cd67e89961544e041a9ce7959cfc308fc841`.
Started `2026-11-07T01:40:53.842221Z`, finished `2026-11-07T01:45:38.328075Z`;
exit 0. It contains the final application, migration and acceptance logic.
Subsequent changes are documentation and acceptance-image support for unchanged
M8 browser assertions; runtime-source identity is checked in the package.

- Clean Python 3.12.16 hash-locked installation, pip check, uv lock and both
  requirements exports: passed. Ruff check/format and mypy (20 source files): passed.
- Python: **95 unit/contract/privacy tests**, **15 real PostgreSQL tests** passed.
- Python wheel and source distribution: built successfully.
- Fresh PostgreSQL 17.11: migration, constrained runtime roles, SCRAM, native
  secret ownership, missing/unreadable/empty/bad-permission negatives: passed.
- Database outage: ready 503, live 200; database/API restart and repeated
  migration: passed. Complete available container logs had no credential match.
- A separate real database initialized with the **exact original PR1 bootstrap**
  and two original roles upgraded to 0002 without changing its foundation marker.
  Repeated Alembic upgrade passed; no role-creation privilege was added to runtime.
- Real Keycloak + PostgreSQL + FastAPI + Next BFF: **4 Chromium cases passed**
  in 48.7 seconds, without mocks as the sole acceptance evidence.
- Real state, nonce and PKCE tampering each refused session creation.
- Two organizations, same-email distinct subjects, pending registration, separate
  operator approval, current role checks, cross-tenant denial and revocation passed.
- Concurrent last-owner removal, suspended-owner handling, RLS/default-deny and
  BFF SQL separation passed in PostgreSQL.
- Six concurrent requests caused exactly one refresh; invalid refresh, idle and
  absolute expiration denied access. Committed revocation remained effective.
- PostgreSQL/API/BFF/IdP restart retained authorized state; IdP outage failed
  protected requests closed. Signed logout revoked the database session before
  any subsequent API introspection could conceal a missing backchannel action.
- Controller channel symlink/exclusive-ack negatives passed. Browser UID 10001,
  read-only, no Docker socket, SQL/operator credential or server token key.
- Privacy scanner checked **12 encrypted synthetic tokens**, actual credentials
  against container logs, and **35 served client files**: no match; values unprinted.

## Frontend and boundary regressions

- Lint, TypeScript and **131 unit/component tests in 14 files** passed locally.
- Production Next standalone build and strict npm installation passed in Linux.
  The same dependency/build source was reused from its verified Docker cache;
  adding test-only image files did not change the production build inputs.
- M8 browser tree: `9508cb917aa03c55861e1a88124506671ad6649a`,
  `2026-11-07T02:05:39Z`–`02:08:41Z`, exit 0.
- **118 Chromium cases passed; 2 existing exclusions**, across desktop/tablet/mobile.
  Suites: foundation, home, rooms, graph, operations, provenance, Signal integration
  and walkthrough. Assertions were not weakened and no new skips were introduced.
- M8 feature/components/assets, How, Signal, `/demo` and the separate local
  homepage patch are unchanged. The generated preexisting next-env file remains
  outside these commits. No new WebKit, Firefox or real-device result is claimed.

## Static delivery and audits

**50 CI classification tests** passed, including Core/M8/M9/mixed/unknown/workflow
negatives. All 14 workflow YAML files parsed; Actionlint passed for the new recipe.
The complete proposed diff classifies Core+web+M9 conservatively because it changes
the classifier/new recipe. No Core check or manual event is suppressed.

Fresh audits `2026-11-07T01:42:37Z`–`01:42:47Z`:

- Root npm complete / production: **0 / 0 findings**.
- Python runtime / development: **0 / 0 known vulnerability findings**.
- Frontend complete: **8 moderate, 0 high, 0 critical**; production: **0**.
  Complete frontend audit exits 1 as expected; its finding is not suppressed.

The local-only Founder disposition expires `2026-11-07T06:45:07Z`
(November 7, 01:45:07 America/Toronto). All reported dependent operations completed
before expiration. ESLint 9 EOL and minimatch/Next-nft remain unresolved.

## Publication and review gates

Local implementation verdict: **M9-PR2 READY FOR INDEPENDENT REVIEW**.
This is not completion of the hosted exact-head acceptance gate in specification
section 20. Independent 01/04 PR2 review and distinct publication approval remain.

Static prediction for a future PR to dev: 11 workflows / 22 jobs selected. Existing
Core regressions remain applicable; the Groth16 acceptance path filter is not
selected and live anchoring remains manual. No workflow was dispatched here.
The identity job's strict moderate-audit gate would currently fail before its
build. The independent M8 workflow would also build; local approval covers neither.
Resolve this hosted security exposure before authorizing any push.

No Core cryptographic suite, Groth16, blockchain transaction, merge, deployment
or PR3 implementation was executed. Earlier failed attempts remain local, but
only the immutable successful evidence above supports this candidate's claims.
