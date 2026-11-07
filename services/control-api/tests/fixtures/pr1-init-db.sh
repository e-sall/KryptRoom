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
export MIGRATOR_PASSWORD APP_PASSWORD
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
\getenv migrator_password MIGRATOR_PASSWORD
\getenv app_password APP_PASSWORD
SET password_encryption = 'scram-sha-256';
SELECT format('CREATE ROLE kryptroom_migrator LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L', :'migrator_password') \gexec
SELECT format('CREATE ROLE kryptroom_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L', :'app_password') \gexec
REVOKE ALL ON DATABASE kryptroom FROM PUBLIC;
GRANT CONNECT ON DATABASE kryptroom TO kryptroom_migrator, kryptroom_app;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA control_api AUTHORIZATION kryptroom_migrator;
GRANT USAGE ON SCHEMA control_api TO kryptroom_app;
ALTER DEFAULT PRIVILEGES FOR ROLE kryptroom_migrator IN SCHEMA control_api GRANT SELECT ON TABLES TO kryptroom_app;
CREATE DATABASE kryptroom_test;
REVOKE ALL ON DATABASE kryptroom_test FROM PUBLIC;
GRANT CONNECT ON DATABASE kryptroom_test TO kryptroom_migrator, kryptroom_app;
\connect kryptroom_test
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA control_api AUTHORIZATION kryptroom_migrator;
GRANT USAGE ON SCHEMA control_api TO kryptroom_app;
ALTER DEFAULT PRIVILEGES FOR ROLE kryptroom_migrator IN SCHEMA control_api GRANT SELECT ON TABLES TO kryptroom_app;
SQL
unset MIGRATOR_PASSWORD APP_PASSWORD value
