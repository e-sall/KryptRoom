# Control API foundation — M9 PR1

Local operational-metadata foundation, based on dev
`7fde54f86b8df11d162eb317414dc1d2f932b70a`. No production service, authentication,
organization registration, Room creation, invitation, governance mutation, audit
storage, cryptographic execution or frontend connection is implemented here.

## Local containers

From `services/control-api`, with Docker Engine and Compose installed:

```sh
python scripts/local-secrets.py
docker compose config --quiet
docker compose up --build -d api
curl http://127.0.0.1:8001/health/live
curl http://127.0.0.1:8001/health/ready
```

Compose requires native Linux/POSIX storage (including a WSL Linux filesystem,
not a Windows `/mnt/c` checkout). The generator rejects non-private directories,
invalid existing credentials and unsupported permission semantics. Canonical
passwords remain in ignored `.runtime/secrets`, directories `0700` and files
`0600`, owned by the operator. Existing values are never overwritten.

A one-shot `prepare-secrets` container projects those credentials into separate
consumer volumes: directories `0700`, files `0400`, UID/GID 999 for PostgreSQL and
10001 for migrate/API/tests. Each consumer mounts only its own volume read-only;
the API receives only its application credential. No world-readable mode is used.
The preparer runs no API, has no network, a read-only root filesystem, and only
CHOWN/DAC_OVERRIDE capabilities needed to read private operator files and assign
consumer ownership. It exits before PostgreSQL can start. Values or metadata
mismatches in an existing projection fail instead of silently rotating credentials.

The preparer is a local/CI bootstrap helper, not a new business service. Docker
operators are trusted; this is not protection against host root or daemon owners.
Native Windows API development remains separate from this POSIX Compose profile.
The database has no host port. The API is bound to loopback; do not expose it as a
production service. Local database transport is explicitly non-TLS on an internal
Docker network. Typed configuration otherwise defaults to requiring database TLS.
Secrets are mounted separately: the API receives only the read-only role credential,
the migration job only the schema-owner credential. PostgreSQL administration is
restricted to the database container. No real participant data belongs in this DB.

Both official images are pinned by release and immutable OCI index digest in the
Dockerfile/Compose file. Python dependencies, including transitive versions and
hashes, are locked in `uv.lock` and its committed runtime/development exports.
Image maintenance and host security remain operator responsibilities.

For the optional technical OpenAPI 3.1 JSON, set `CONTROL_DOCS_ENABLED=true` in the
operator environment before recreating `api`. `/openapi.json` then describes only
the two health endpoints. No Swagger/CDN or ReDoc page is installed. Normal
business endpoints will use `/api/v1` in later PRs; there are none in PR1.

## Migrations and rollback

The official PostgreSQL entrypoint initializes two local databases and separate
non-superuser roles once, on a fresh volume. It creates `control_api`, grants only
schema usage/table SELECT to the application role, and leaves public-schema CREATE
revoked. Application startup never runs migrations or `create_all`.

The PostgreSQL initializer validates all credentials before any role SQL and stops
on absent, unreadable, empty, malformed or incorrectly owned/permitted files.
The separate `migrate` service applies `alembic upgrade head` before the API starts.
Readiness requires PostgreSQL major 17, the exact Alembic revision
`0001_foundation`, and the technical marker `m9-control-foundation-v1`. Liveness
does not connect to PostgreSQL. An unavailable DB or incompatible/missing schema
returns generic readiness 503. Do not use readiness as an authorization check.

```sh
docker compose run --rm migrate alembic current
docker compose run --rm migrate alembic check
docker compose run --rm migrate alembic upgrade head
```

Run one migration actor at a time. To roll PR1 back locally, stop API consumers,
retain a backup if needed, then explicitly run:

```sh
docker compose stop api
docker compose run --rm migrate alembic downgrade base
```

This removes only the technical marker table. Restoring service requires upgrading
again and restarting `api`. Future business-data migrations need independent
backup/data-retention review; this rollback is not a general data-loss guarantee.
Do not change an already published migration. Credential changes on an existing
volume require an explicit operator rotation; rewriting secret files alone does
not rotate SQL role passwords. `docker compose down` preserves the local volume.
Use `down --volumes` only for a disposable test instance whose contents may be lost.

## Python development and checks

Python 3.12.16 and uv 0.13.7 are the recorded versions. In this directory:

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
```

The pip alternative used in CI installs `requirements-dev.lock` with
`--require-hashes`, then installs this package with `--no-deps --no-build-isolation`.
The build backend is pinned Hatchling. The hash exports must remain exact:

```sh
uv export --frozen --no-header --no-dev --no-emit-project --format requirements-txt --output-file requirements.lock
uv export --frozen --no-header --no-emit-project --format requirements-txt --output-file requirements-dev.lock
```

Full local container acceptance, including the five real PostgreSQL integration
tests, outage, database/API restart and repeated migration:

```sh
uv run python scripts/compose-acceptance.py
```

This script operates only the named local Compose project. It leaves the stack
available for inspection. CI removes its disposable containers/volume afterwards.
Integration tests require explicit `CONTROL_TEST_POSTGRES=1`, `CONTROL_ENVIRONMENT=test`,
a database name ending `_test`, migration-role credentials and a separate
`CONTROL_TEST_APP_PASSWORD_FILE`. Selecting them without these fails, rather than
silently skipping. They downgrade/reset only the disposable PR1 test schema.

## Contracts and boundaries

The seven `modules` files are internal typed ports, not registered business routes.
PR2 will implement OIDC identity and controlled organizational enrollment. No email
domain, browser header or external claim is accepted as membership authority.
The default business authorizer denies every request. Future audit/outbox writers
must share the caller's SQL transaction; PR1 implements neither persistence path.
Governance references are not `StatePolicy`, cryptographic consent or execution
grants. UUIDv4 from the standard library is the initial opaque-ID convention;
UUIDv7 remains an optional later decision. Database timestamps use timezone-aware
UTC values. No historical Core identifier/commitment changes.

Future success envelopes, bounded cursor pagination and safe error envelopes are
defined in `contracts.py`. Health success stays a small probe body. Every HTTP
response gets a fresh server-generated UUID correlation header, `no-store`, and
`nosniff`. Error bodies carry the same ID. Submitted correlation headers grant no
trust. Default request logs contain only a fixed event, generated ID, recognized
method, server route template, status and elapsed time. Bodies, arbitrary paths,
queries, headers, database URLs and exception text are not logged by this service.
Use the provided Uvicorn options: access logging and proxy-header trust disabled.

No Core runtime is imported and no frontend/M8 preview is connected. There is no
`/run`, `/reveal`, `/decrypt`, `/prove` or `/anchor` API. This service has no access
to KryptNode storage, keys, raw data, secret shares or ciphertext payloads.
