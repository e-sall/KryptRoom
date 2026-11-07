#!/bin/sh
# One-shot infrastructure prerequisite for an existing PR1 database. Run only as
# the local PostgreSQL administrator, never as the API, migrator or BFF role.
set -eu
fail() { printf '%s\n' 'Identity role upgrade refused; inspect private local prerequisites' >&2; exit 1; }
read_secret() {
    path=/run/secrets/$1
    [ -f "$path" ] && [ ! -L "$path" ] && [ -r "$path" ] || fail
    [ "$(stat -c %a "$path")" = 400 ] || fail
    [ "$(stat -c %u "$path")" = "$(id -u)" ] || fail
    size=$(stat -c %s "$path") || fail
    [ "$size" -ge 24 ] && [ "$size" -le 128 ] || fail
    value=$(cat "$path") || fail
    [ "${#value}" -eq "$size" ] || fail
    case "$value" in *[!A-Za-z0-9_-]*|'') fail ;; esac
    printf '%s' "$value"
}
# Validate every credential before any mutation. Do not enable shell tracing.
MIGRATOR_PASSWORD=$(read_secret migrator_password) || exit 1
APP_PASSWORD=$(read_secret app_password) || exit 1
OPERATOR_PASSWORD=$(read_secret operator_password) || exit 1
BFF_PASSWORD=$(read_secret bff_password) || exit 1
KEYCLOAK_PASSWORD=$(read_secret keycloak_password) || exit 1
export MIGRATOR_PASSWORD APP_PASSWORD OPERATOR_PASSWORD BFF_PASSWORD KEYCLOAK_PASSWORD
psql -v ON_ERROR_STOP=1 --username postgres --dbname kryptroom <<'SQL'
\getenv operator_password OPERATOR_PASSWORD
\getenv bff_password BFF_PASSWORD
\getenv keycloak_password KEYCLOAK_PASSWORD
BEGIN;
DO $$
BEGIN
  IF current_user <> 'postgres' OR NOT EXISTS (
      SELECT 1 FROM control_api.foundation_metadata WHERE contract='m9-control-foundation-v1') THEN
    RAISE EXCEPTION 'Expected existing PR1 foundation';
  END IF;
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname IN
      ('kryptroom_auth_guard','kryptroom_operator','kryptroom_bff','kryptroom_keycloak')) THEN
    RAISE EXCEPTION 'Identity roles already exist; do not rotate or overwrite implicitly';
  END IF;
  IF EXISTS (SELECT 1 FROM pg_database WHERE datname='keycloak') THEN
    RAISE EXCEPTION 'Unexpected existing identity database';
  END IF;
  IF (SELECT count(*) FROM pg_roles WHERE rolname IN ('kryptroom_app','kryptroom_migrator')
      AND rolcanlogin AND NOT rolsuper AND NOT rolcreatedb AND NOT rolcreaterole
      AND NOT rolbypassrls) <> 2 THEN
    RAISE EXCEPTION 'Unexpected PR1 runtime/migrator role privileges';
  END IF;
END $$;
SET password_encryption='scram-sha-256';
CREATE ROLE kryptroom_auth_guard NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE BYPASSRLS;
SELECT format('CREATE ROLE kryptroom_operator LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS PASSWORD %L', :'operator_password') \gexec
SELECT format('CREATE ROLE kryptroom_bff LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS PASSWORD %L', :'bff_password') \gexec
SELECT format('CREATE ROLE kryptroom_keycloak LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS PASSWORD %L', :'keycloak_password') \gexec
GRANT kryptroom_auth_guard TO kryptroom_migrator;
GRANT CONNECT ON DATABASE kryptroom TO kryptroom_operator, kryptroom_bff;
CREATE SCHEMA bff_auth AUTHORIZATION kryptroom_migrator;
GRANT USAGE ON SCHEMA control_api TO kryptroom_auth_guard;
COMMIT;
-- CREATE DATABASE cannot run inside a transaction. If it fails, do not migrate
-- or start services: inspect/complete this explicit infrastructure step first.
CREATE DATABASE keycloak OWNER kryptroom_keycloak;
REVOKE ALL ON DATABASE keycloak FROM PUBLIC;
GRANT CONNECT ON DATABASE kryptroom_test TO kryptroom_operator, kryptroom_bff;
\connect kryptroom_test
CREATE SCHEMA bff_auth AUTHORIZATION kryptroom_migrator;
GRANT USAGE ON SCHEMA control_api TO kryptroom_auth_guard;
SQL
unset MIGRATOR_PASSWORD APP_PASSWORD OPERATOR_PASSWORD BFF_PASSWORD KEYCLOAK_PASSWORD value
printf '%s\n' 'PR1 identity-role prerequisite completed; Alembic migration remains explicit'
