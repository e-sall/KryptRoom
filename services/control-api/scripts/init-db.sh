#!/bin/sh
set -eu
# Official postgres entrypoint runs this only for a fresh volume. Never enable shell tracing.
export MIGRATOR_PASSWORD="$(cat /run/secrets/migrator_password)"
export APP_PASSWORD="$(cat /run/secrets/app_password)"
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
unset MIGRATOR_PASSWORD APP_PASSWORD
