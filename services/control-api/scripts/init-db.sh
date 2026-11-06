#!/bin/sh
set -eu
# Runs as postgres, only on a fresh volume. Never enable shell tracing.
fail_secret() {
    printf '%s\n' 'PostgreSQL bootstrap refused an invalid credential' >&2
    exit 1
}
read_secret() {
    path=$1
    [ -f "$path" ] && [ ! -L "$path" ] && [ -r "$path" ] || fail_secret
    [ "$(stat -c %a "$path")" = 400 ] || fail_secret
    [ "$(stat -c %u "$path")" = "$(id -u)" ] || fail_secret
    size=$(stat -c %s "$path") || fail_secret
    [ "$size" -ge 24 ] && [ "$size" -le 128 ] || fail_secret
    value=$(cat "$path") || fail_secret
    [ "${#value}" -eq "$size" ] || fail_secret
    case "$value" in *[!A-Za-z0-9_-]*|'') fail_secret ;; esac
    printf '%s' "$value"
}
# Validate all credentials before the first SQL statement. Assignment failures
# propagate; combining command substitution with `export` would mask them.
MIGRATOR_PASSWORD=$(read_secret /run/secrets/migrator_password) || exit 1
APP_PASSWORD=$(read_secret /run/secrets/app_password) || exit 1
OPERATOR_PASSWORD=$(read_secret /run/secrets/operator_password) || exit 1
BFF_PASSWORD=$(read_secret /run/secrets/bff_password) || exit 1
KEYCLOAK_PASSWORD=$(read_secret /run/secrets/keycloak_password) || exit 1
export MIGRATOR_PASSWORD APP_PASSWORD OPERATOR_PASSWORD BFF_PASSWORD KEYCLOAK_PASSWORD
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
\getenv migrator_password MIGRATOR_PASSWORD
\getenv app_password APP_PASSWORD
\getenv operator_password OPERATOR_PASSWORD
\getenv bff_password BFF_PASSWORD
\getenv keycloak_password KEYCLOAK_PASSWORD
SET password_encryption = 'scram-sha-256';
SELECT format('CREATE ROLE kryptroom_migrator LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L', :'migrator_password') \gexec
SELECT format('CREATE ROLE kryptroom_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L', :'app_password') \gexec
-- PR2 helpers have no login. Runtime credentials cannot SET ROLE to these roles.
CREATE ROLE kryptroom_auth_guard NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE BYPASSRLS;
SELECT format('CREATE ROLE kryptroom_operator LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS PASSWORD %L', :'operator_password') \gexec
SELECT format('CREATE ROLE kryptroom_bff LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS PASSWORD %L', :'bff_password') \gexec
SELECT format('CREATE ROLE kryptroom_keycloak LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS PASSWORD %L', :'keycloak_password') \gexec
CREATE DATABASE keycloak OWNER kryptroom_keycloak;
REVOKE ALL ON DATABASE keycloak FROM PUBLIC;
GRANT kryptroom_auth_guard TO kryptroom_migrator;
REVOKE ALL ON DATABASE kryptroom FROM PUBLIC;
GRANT CONNECT ON DATABASE kryptroom TO kryptroom_migrator, kryptroom_app, kryptroom_operator, kryptroom_bff;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA control_api AUTHORIZATION kryptroom_migrator;
CREATE SCHEMA bff_auth AUTHORIZATION kryptroom_migrator;
GRANT USAGE, CREATE ON SCHEMA control_api TO kryptroom_auth_guard;
GRANT USAGE ON SCHEMA control_api TO kryptroom_app;
ALTER DEFAULT PRIVILEGES FOR ROLE kryptroom_migrator IN SCHEMA control_api GRANT SELECT ON TABLES TO kryptroom_app;
CREATE DATABASE kryptroom_test;
REVOKE ALL ON DATABASE kryptroom_test FROM PUBLIC;
GRANT CONNECT ON DATABASE kryptroom_test TO kryptroom_migrator, kryptroom_app, kryptroom_operator, kryptroom_bff;
\connect kryptroom_test
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA control_api AUTHORIZATION kryptroom_migrator;
CREATE SCHEMA bff_auth AUTHORIZATION kryptroom_migrator;
GRANT USAGE, CREATE ON SCHEMA control_api TO kryptroom_auth_guard;
GRANT USAGE ON SCHEMA control_api TO kryptroom_app;
ALTER DEFAULT PRIVILEGES FOR ROLE kryptroom_migrator IN SCHEMA control_api GRANT SELECT ON TABLES TO kryptroom_app;
SQL
unset MIGRATOR_PASSWORD APP_PASSWORD OPERATOR_PASSWORD BFF_PASSWORD KEYCLOAK_PASSWORD value
