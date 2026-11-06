# M9 PR1: establish the metadata-only Control API foundation

Base: `dev` at `7fde54f86b8df11d162eb317414dc1d2f932b70a`.
Head branch: `feat/m9-control-api-foundation` (local, unpublished).

Add an isolated Python 3.12/FastAPI Control API with health/readiness, typed safe
contracts, SQLAlchemy transactions, a versioned metadata-only Alembic schema,
separate PostgreSQL roles, digest-pinned Compose and hash-locked dependencies.
Prepare internal module ports and deny all business authorization by default.
There is no authentication, Room/invitation creation, frontend connection or Core
execution/disclosure API. Existing M1–M8 code, fixtures and workflows are preserved.

Validation: 20 unit/static tests, five real PostgreSQL tests on Windows/Linux,
fresh-volume Compose outage/restart/reload acceptance, two clean installations,
lint/format/mypy/build/lock checks, zero known M9 dependency findings and 31 existing
classifier tests. See the three PR1 reports for raw evidence and exact limitations.

**Publication held:** current legacy routing would additionally run root tooling
with three high pre-existing package entries and M8 frontend jobs. No M8 exception
covers M9. Resolve that scope/treatment explicitly before push/opening this PR.
No exact-head GitHub result, merge approval or deployment authorization is implied.
