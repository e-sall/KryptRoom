# M9-PR2 targeted QA remediation

Reviewed starting HEAD: `8da2b45cdaa7492f6df742c73865f9c2aa851693`.
PR1 baseline: `d8a5c0aa7ed845c31bd2ff40c1b3491246c6cf83`.
Branch: `feat/m9-identity-organizations`. The five original commits remain intact.
The new commit, exact delta and source hashes are recorded in the portable delta
package. No publication, hosted run, merge, deployment or PR3 work is authorized.

Architect01 approved the starting HEAD. QA04 requested the three bounded changes
below. Neither prior verdict automatically certifies this modified candidate.
New targeted 04 revalidation and 01 attestation are required on the frozen new SHA.

## QA-PR2-01 — requester visibility after revocation

The only application/security implementation change is the `org_select` predicate
in unpublished migration `0002_security.sql`: requester-based visibility now
requires `status IN ('PENDING_REVIEW','REJECTED')`. Active organization visibility
requires a current active role. No other grants, helpers, schema constraints,
HTTP contracts, BFF logic or authorization code is changed.

Real PostgreSQL regression creates Alice's A through the request/approval flow,
promotes a second owner, revokes Alice and executes a direct SELECT as
`kryptroom_app` under Alice's transaction context. A is absent; Alice's actual
pending/rejected requests remain visible; another user's request is absent.
The service list/read paths also deny A. The expanded real BFF/API scenario
separately promotes Dora, revokes applicant Alice and confirms HTTP 404, no
accessible organization and no active membership for Alice.

The HTTP layer already required current membership; the original finding was
an overbroad SQL defense predicate, not a demonstrated HTTP bypass.
The correction narrows SQL to the approved contract rather than creating a new one.

Migration 0001 is unchanged. PR2 is unpublished: fresh fixtures and a real PR1
upgrade use corrected 0002. Alembic does not silently reapply an already installed
0002. Any older disposable PR2 fixture must be explicitly recreated; retained
identity data must never be reset implicitly. No production migration is claimed.

## QA-PR2-02 — observed transactional overlap

The tests now use two distinct PostgreSQL backend PIDs, an explicit initial
authorization, connection-local SQL instrumentation/Event/Queue coordination and
`pg_blocking_pids` to prove the intended lock wait before allowing the first
transaction to mutate and commit. Bounded polling waits for database evidence;
an elapsed delay alone cannot pass either test. No wheel/timer-style or implicit
thread scheduling assumption is used as proof.

- Dora's initially authorized metadata update blocks behind Alice's organization
  lock. Alice revokes Dora and commits. The resumed update returns 404; the
  organization name and version remain unchanged.
- Two initially authorized owner-removal operations overlap on the same lock.
  Removing Charlie commits first. Alice's second connection then attempts to
  remove the remaining owner and returns 409 `last_owner`; one active owner remains.

Existing application locking and post-lock authorization satisfy these tests.
`organization_service.py`, operator behavior and lock ordering are unchanged.
The helper's eight-second statement timeout is test-only; no runtime setting changes.

## QA-PR2-03 — real BFF/API mutations and provider revocation

The original four Chromium cases are preserved and the business case is expanded:

- Alice promotes Charlie through BFF/API, reads back the new role/version, and
  later demotes him through the same authorized path.
- Bob cannot change Charlie's role, revoke him or rename A. Alice cannot rename B,
  change B's membership role or revoke B's owner: six actual writes return 404.
- Authorized reads compare both complete organization objects and paginated
  membership objects before/after those attempts; no forbidden change persists.
- Self-promotion, CSRF negatives, owner protection, committed revocation, refresh,
  expiry, service restarts, IdP outage, local/signed logout and OIDC tampering remain.
- The trusted controller decrypts Bob's real access token into its own memory,
  verifies live introspection `active=true` and calls FastAPI `/api/v1/me` directly:
  200. After real provider logout, the **same still-unexpired token** has live
  `active=false` and direct FastAPI returns 401 `authentication_failed`.
  This client has no BFF cookie; the browser never receives the token.

The controller uses the already pinned `httpx2` dependency. The unsigned claim
read in its probe is solely a test freshness guard, never authentication. The
unchanged API independently verifies signature/claims and performs live introspection.
No token, private key or credential value is printed or placed in the package.

## Executed validation and exact-source binding

Authoritative immutable source tree:
`aefb28665754b8fc3d704c6e1fe47c69c8516034`.
Native Linux run: `2026-11-07T02:57:48.457199Z`–`03:00:51.397948Z`, exit 0.
Later changes are documentation only; the delta package verifies each tested code
blob against the final commit, without assuming old evidence covers changed code.

- 95 Python unit/contract/privacy cases and **17 real PostgreSQL cases passed**.
- Ruff check/format, mypy (20 source files), hash-lock exports, pip check and
  Python distribution build passed.
- Fresh PostgreSQL 17 migration, deterministic negative/concurrency cases and
  separate original-PR1 database upgrade/repeated migration passed; marker preserved.
- **4 real Chromium Keycloak/BFF/API cases passed in 39.3 seconds**, including all
  prior scenarios and the new assertions. They are four expanded cases, not a
  claim of additional standalone cases or a full rerun of every historical browser suite.
- Native lifecycle restart/outage checks and actual token privacy scans passed:
  **14 encrypted synthetic tokens**, complete available logs and **35 client files**.
- Frontend lint and TypeScript passed at 02:56–02:57 UTC. Docker production build
  completed using the verified cache; runtime frontend inputs and dependencies
  are unchanged. The 131 frontend unit and 118 M8 browser successes (2 historical
  exclusions) from the reviewed candidate are reused only for unchanged sources.
- 50 classifier tests passed. Targeted delta: web+M9; complete PR2: Core+web+M9.
  Classifier/workflow sources are unchanged; no required check or manual event is removed.
- Root complete/production and Python runtime/development audits at 02:59 UTC:
  zero findings. Frontend complete: **8 moderate, zero high/critical**; production:
  zero. The full frontend audit exits 1 and its findings stay visible.

Two earlier attempts are not claimed successful: a new test tried to read
append-only access events with the intentionally restricted operator role; its
oracle now compares permitted organization fields without expanding SQL grants.
The first complete attempt then stopped on an incorrect `httpx` controller import;
it was corrected to existing `httpx2`, with no new dependency. Both failures and
their provenance remain local; successful final evidence is separately identified.

## Frontend risk and publication boundary

No compatible complete fix is confirmed. Official metadata plus strict isolated
resolution still reject ESLint 10.14.0 / eslint-config-next 16.4.5 because current
import/React/a11y peers stop at ESLint 9. An integrity-verified official Next 16.4.5
archive contains the **byte-identical embedded nft file** as installed Next 16.4.2
(SHA-256 `e436d398b2263fb87a2d8ee3d9dab8db2544c684ba9bc1c0d4ab4e67acbab207`).
Updating that patch alone therefore does not fix the embedded path. Minimatch
11.0.5 lies outside affected declared ranges; no major override or force install
is applied. See the [advisory](https://github.com/advisories/GHSA-g3hv-75wg-m249),
[ESLint policy](https://eslint.org/version-support/) and raw official npm evidence.

Founder approved new **M9-PR2-SEC-002** solely for these local frontend validations,
recorded `2026-11-07T02:51:16Z`, expiring `2026-11-08T02:51:16Z` (Nov 7, 21:51:16
America/Toronto). No previous exception is reused. See the separate decision file.
No hosted CI/push/PR/merge/production scope is accepted. Findings remain unresolved;
absence of a demonstrated visitor-controlled glob path is not inexploitability.

## Scope, review and next gate

The homepage patch, generated preexisting next-env file, historical branches,
M8 design/runtime sources and Core code/fixtures remain unchanged. No cryptographic
suite, Groth16, chain transaction, main change or deployment occurred.

Build verdict: **M9-PR2 READY FOR TARGETED RE-REVIEW**. The portable delta supports
04 closure of all three findings and a targeted 01 attestation on the new exact SHA.
Independent responses must identify their inspected SHA and distinguish their own
re-tests from inspected Build evidence. They are recorded externally after the
commit is frozen, avoiding a further source change after approval.

Publication remains a separate gate: obtain both targeted verdicts, resolve hosted
frontend risk through compatible remediation or a distinct reviewed Founder
disposition, then request explicit push/PR authorization. No publication is made here.
