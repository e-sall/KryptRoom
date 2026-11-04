# M9 PR1 — Acceptance results

**Verdict: BLOCKED for publication; local implementation and acceptance complete.**
Recorded **2026-11-03 America/Toronto**, baseline
`7fde54f86b8df11d162eb317414dc1d2f932b70a`. No hosted CI success is claimed.

## Executed

- **20 unit/static tests passed**, including real refused TCP connection, liveness,
  generic readiness/errors, correlation/log leakage sentinels, exact OpenAPI scope,
  missing forbidden endpoints, default-deny authorization, bounded immutable
  pagination, typed/secret configuration and source/CI boundaries.
- **Five PostgreSQL integration tests passed** on native Windows PostgreSQL 17.11
  and official Linux PostgreSQL 17.11 containers. They cover upgrade twice,
  `alembic check`, downgrade/re-upgrade, constrained metadata-only schema, commit/
  rollback, actual runtime-role DDL/DML denial, API/engine reload, wrong revision,
  missing schema contract and real failed password authentication without leakage.
- **Full Docker Compose lifecycle passed**, including a fresh volume, real role/
  schema initialization and migration, readiness 200, DB stop → readiness 503
  while liveness stays 200, DB restart → 200, API restart → 200, migration rerun →
  200, and scanning container logs for all generated passwords without matches.
- **Two fresh hash-verified Windows installations passed**: same 73 installed
  distributions including the project, same versions, `pip check`, 20 unit tests
  each, and all three lock hashes unchanged. Native runtime Python 3.12.16.
- **Linux image validation passed** on Python 3.12.16: lock consistency, Ruff lint
  and format, strict mypy (14 source files), 20 tests, sdist/wheel build,
  `pip check`, runtime and development dependency audits. Runtime/test image builds
  use hash verification and completed with the committed image digests.
- **31 existing CI classifier tests passed** locally, without modifying the
  classifier or invoking cryptographic runtimes. New tests also verify that
  adding a crypto path still selects its existing proof checks.
- Full/runtime **M9 Python audits: zero known vulnerabilities**. The independent
  unchanged legacy root audit still reports three high entries and blocks the
  proposed publication scope; see [security review](SECURITY-REVIEW.md).

The unit and PostgreSQL commands select separate markers. Their deselected counts
are the other group, not skips or excluded assertions. No new skip was introduced.
Fresh role/schema initialization uses the same committed SQL bootstrap on Windows
and Linux. Native process-control isolation required one lifecycle controller;
the definitive container cycle also passed using normal Compose stop/start.

## Reproducible commands

See [service README](../../../services/control-api/README.md) for install and
credentials. From `services/control-api`:

```sh
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run python -m pytest -m 'not postgres'
uv run python -m build --no-isolation
uv run python scripts/check-locks.py
uv run python -m pip_audit -r requirements.lock --require-hashes --disable-pip
uv run python -m pip_audit -r requirements-dev.lock --require-hashes --disable-pip
uv run python scripts/local-secrets.py
docker compose config --quiet
uv run python scripts/compose-acceptance.py
```

Local Linux verification used Ubuntu 24.04 WSL, existing Docker Engine 29.1.3 and
official Compose 5.7.0 (binary SHA-256
`7758048ad38e580f22559603312874fec8bb638d021a9e64182385fc17cc12a2`).
No OS-wide package installation or group change. Containers run Python 3.12.16;
the host's older Python only drives Docker lifecycle commands.

## Evidence and boundaries

- [Machine-readable validation and inventory](evidence/validation.json).
- [Fresh install reproducibility](evidence/reproducibility.json).
- [Source archive privacy regression, before/after](evidence/packaging-regression.json).
- [M9 runtime audit](evidence/audit-runtime.json), [development audit](evidence/audit-dev.json).
- [Native real HTTP lifecycle](evidence/native-http-lifecycle.json).
- [Exact prospective workflow plan](evidence/workflow-plan.json).
- [Local Linux checks](evidence/linux-qa.txt), [fresh Compose acceptance](evidence/compose-acceptance.txt).

Raw credentials, database volume, temporary tools, virtualenvs, distributions,
cache/build trees and nonessential host logs are excluded from Git. Evidence is
scanned for generated credentials before staging.

No M1–M8 runtime regression suite or frontend/browser suite was rerun: those
implementations, dependencies and interfaces are byte-preserved, and no adapter
connects M9 to them. Boundary tests verify this narrow scope; they are not a new
cryptographic validation. No Groth16 or blockchain transaction was executed.
Production deployment, independent audit, disaster recovery, and exact-head GitHub
CI remain outside the executed evidence. Main and dev are unchanged; PR2 not started.
