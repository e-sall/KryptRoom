# PR1 → PR2 database procedure

Migration `0001_foundation.py` and the marker contract
`m9-control-foundation-v1` retain their historical bytes/meaning.
`0002_identity_organizations` adds identity/organization metadata, named types,
constraints/indexes, RLS/functions and separate BFF persistence. Readiness expects
revision 0002 while retaining the PR1 marker.

## Fresh disposable local installation

`local-secrets.py` preserves existing credentials and prepares missing private
sources. `prepare-secrets.py` projects only each consumer's allowed files.
`init-db.sh` validates every required role credential before SQL, creates restricted
roles/schemas, and retains SCRAM-SHA-256. Alembic then runs explicitly as the
separate non-root migrator. Application startup never creates or migrates tables.

## Existing PR1 database

Do not rerun init-db.sh against existing data and do not give CREATEROLE to the
migrator. Back up/inspect the intended local metadata database first.

1. Preserve the existing app/migrator passwords and original foundation marker.
2. Generate only missing operator/BFF/Keycloak private credential sources and
   project them into the PostgreSQL administrator's UID-owned 0400 secret volume.
3. Run `scripts/upgrade-identity-roles.sh` once through the isolated PostgreSQL
   administrator channel. It validates inputs, refuses unexpected/preexisting new
   roles or databases, creates the infrastructure prerequisites and grants no
   role-creation privilege to the migrator/API. It does not rotate old credentials.
4. Run `alembic upgrade head` with the migrator credential, then repeat the same
   command to confirm Alembic's safe no-op semantics. Confirm the original marker
   value/timestamp and expected revision before starting the configured services.

The infrastructure script is deliberately one-shot, not an automatic role repair
or password rotation facility. On partial infrastructure failure, stop and inspect;
do not continue migration/service startup or erase an existing volume.

`scripts/pr1-upgrade-acceptance.py --disposable` tests this against the exact PR1
bootstrap fixture from baseline `d8a5c0aa7ed845c31bd2ff40c1b3491246c6cf83`, with
only its original two roles before upgrade. `tests/fixtures/pr1-baseline.json`
records original bootstrap and migration SHA-256 values. This is M9 metadata
testing; no historical Core fixture or proof is regenerated.

## Rollback

On a disposable test database, `alembic downgrade 0001_foundation` removes PR2
tables/functions/types while retaining the foundation marker. A second upgrade
must reproduce the schema. Runtime credentials cannot perform this DDL.

Downgrading destroys identities, memberships and sessions. Passing a disposable
rollback test does not authorize a destructive downgrade of real pilot metadata.
Production rollback, retention and backup recovery require a separate reviewed plan.
