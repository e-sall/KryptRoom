# Local persistent Rooms UI/BFF

Isolated branch on approved PR3 `646a8f5`. PR3 code/migrations, dependencies and CI
are unchanged. No publication or hosted execution is authorized.

`/app/rooms`, `/app/rooms/new` and `/app/rooms/{UUID}` now read/create/edit actual
organization Rooms through the existing PR2 BFF session proxy. OWNER/ADMIN affordances
come from /me; backend authorization remains decisive at every request. Only exact
PR3 GET/POST/PATCH paths are added to the allowlist. No delete, invitation, state,
compute or disclosure route is introduced. Synthetic /preview and /demo stay separate.

Use the actual GET ETag with If-Match, never an inferred version. Conflicts preserve
the unsaved edit and require an explicit reload. Idempotency keys survive uncertain
creation retries. Denied/revoked responses clear displayed records. The browser
receives the intended session-bound CSRF value, never OAuth credentials. Same-origin,
HttpOnly sessions, CSRF/origin checks, server-only token storage and API RLS are reused.
Loading, empty, sign-in, read-only, forbidden, conflict, saved and generic error views
use M8 primitives/tokens. No cached preview dataset is used as persisted data.

Validation: 142 frontend unit tests PASS, targeted lint, typecheck and local webpack
production build; real browser path with existing Edge Chromium, Keycloak PKCE,
session BFF, API and PostgreSQL. Real scenario covers creation, reopening after
reconnection, actual ETag conflict, missing CSRF, cross-tenant denial and revocation.
The dedicated opt-in suite preserves the PR2 identity suite selection:
`playwright test --config=playwright.rooms.config.ts`.
Set KR_ROOMS_TEST_PRIVATE (synthetic test-user files), KR_ROOMS_TEST_OPERATOR
(trusted fixture controller path) and KR_ROOMS_BROWSER_CHANNEL=msedge on the local
Windows/WSL controller. TLS trusts only the fixture SPKI via KR_TEST_TLS_SPKI.
Fixture secrets and controller authority are never supplied to browser code.

The external evidence directory M9-ROOMS-UI-LOCAL-20261111 records exact commands,
results and fixture scripts; it excludes private credentials from review packages.
Windows/WSL required temporary loopback byte relays; TLS remained end-to-end.
Cached dependencies were linked, not installed. Local webpack build succeeded with
standalone tracing warnings caused by that external junction: standalone packaging
and a clean install/container build are NOT validated by this run.
The final real-service suite passed in installed Edge Chromium without response
mocks. The approved PR3 commit/backend stay unchanged. Its generated next-env.d.ts
was observed dirty during final checks and deliberately left outside this delta;
the original pre-existing PR2 next-env edit was also preserved byte-for-byte.

Known limits: PR2's eight moderate findings/EOL and enforcement gates remain open;
no exception/CI change is made. Other modules and RoomStates remain unavailable;
Room headStateId stays null. No real-device or Firefox validation. Hosted CI and
deployment are NOT RUN. Backend PR3 QA is reused, not reopened. QA04 should inspect
only this UI/BFF delta, its narrow presentation-I/O test exception and the recorded
real-service scenario before any separately authorized publication.
