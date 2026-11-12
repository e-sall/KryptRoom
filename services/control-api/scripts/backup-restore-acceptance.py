"""Logical restore rehearsal for an explicitly disposable local/CI test fixture only.

This is not PITR, a production backup agent, or permission to downgrade history.
Only fingerprints/counts leave the controller; the archive stays inside PostgreSQL.
"""

import argparse
import hashlib
import json
import re
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--disposable", action="store_true", required=True)
    parser.add_argument("--container", required=True)
    parser.add_argument("--port", type=int, default=5432)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        raise ValueError("Invalid fixture port")
    if not re.fullmatch(r"kr-m9-(?:pr6-local|release-backend)-[a-zA-Z0-9_-]+", args.container):
        raise ValueError("Only the dedicated disposable release fixture is allowed")
    source = "kryptroom_test"
    restored = "kryptroom_release_restore_test"

    def run(*command: str) -> str:
        # Fixed executable and validated fixture identifier; never invoke a host shell.
        result = subprocess.run(  # noqa: S603
            ["docker", "exec", "--user", "postgres", args.container, *command],  # noqa: S607
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode:
            raise RuntimeError("Disposable restore operation failed; database output withheld")
        return result.stdout.strip()

    def sql(database: str, statement: str) -> str:
        return run(
            "psql",
            "-XAt",
            "-v",
            "ON_ERROR_STOP=1",
            "-p",
            str(args.port),
            "-d",
            database,
            "-c",
            statement,
        )

    def snapshot(database: str) -> dict[str, object]:
        tables = sql(
            database,
            "SELECT quote_ident(schemaname)||'.'||quote_ident(tablename) FROM pg_tables "
            "WHERE schemaname IN ('control_api','bff_auth') ORDER BY 1",
        ).splitlines()
        data = {}
        for table in tables:
            rows = sql(
                database,
                # Catalog identifiers are quoted by PostgreSQL, never user input.
                f"SELECT row_to_json(t)::text FROM {table} t ORDER BY row_to_json(t)::text",  # noqa: S608
            )
            data[table] = {
                "rows": len(rows.splitlines()),
                "sha256": hashlib.sha256(rows.encode()).hexdigest(),
            }
        security = sql(
            database,
            "SELECT json_build_array(n.nspname,c.relname,pg_get_userbyid(c.relowner),"
            "c.relrowsecurity,c.relforcerowsecurity,c.relacl)::text FROM pg_class c "
            "JOIN pg_namespace n ON n.oid=c.relnamespace "
            "WHERE n.nspname IN ('control_api','bff_auth') ORDER BY 1",
        )
        functions = sql(
            database,
            "SELECT json_build_array(n.nspname,p.proname,"
            "pg_get_function_identity_arguments(p.oid),pg_get_userbyid(p.proowner),"
            "p.prosecdef,p.proacl,pg_get_functiondef(p.oid))::text FROM pg_proc p "
            "JOIN pg_namespace n ON n.oid=p.pronamespace "
            "WHERE n.nspname IN ('control_api','bff_auth') ORDER BY 1",
        )
        policies = sql(
            database,
            "SELECT row_to_json(p)::text FROM pg_policies p "
            "WHERE schemaname IN ('control_api','bff_auth') ORDER BY 1",
        )
        return {
            "tables": data,
            "security_sha256": hashlib.sha256(security.encode()).hexdigest(),
            "functions_sha256": hashlib.sha256(functions.encode()).hexdigest(),
            "policies_sha256": hashlib.sha256(policies.encode()).hexdigest(),
        }

    def database_acl(database: str) -> list[list[object]]:
        # Both names are fixed constants above; never accept an arbitrary database.
        if database not in {source, restored}:
            raise ValueError("Unexpected fixture database")
        rows = sql(
            "postgres",
            "SELECT json_build_array(d.datname,CASE WHEN a.grantee=0 THEN 'PUBLIC' "
            "ELSE pg_get_userbyid(a.grantee) END,a.privilege_type,a.is_grantable)::text "
            "FROM pg_database d CROSS JOIN LATERAL "
            "aclexplode(COALESCE(d.datacl,acldefault('d',d.datdba))) a "
            "WHERE d.datname IN ('kryptroom_test','kryptroom_release_restore_test') ORDER BY 1",
        )
        decoded = [json.loads(row) for row in rows.splitlines()]
        return [row[1:] for row in decoded if row[0] == database]

    if not sql(source, "SHOW server_version").startswith("17."):
        raise RuntimeError("PostgreSQL 17 is required")
    if (
        sql(
            "postgres",
            "SELECT count(*) FROM pg_database WHERE datname='kryptroom_release_restore_test'",
        )
        != "0"
    ):
        raise RuntimeError("Restore destination already exists; refusing to overwrite")
    before = snapshot(source)
    source_acl = database_acl(source)
    if not before["tables"].get("control_api.room_operational_events", {}).get("rows", 0):
        raise RuntimeError("Rehearsal requires actual synthetic history")
    created = False
    archive = run("mktemp", "--suffix=.dump")
    if not re.fullmatch(r"/tmp/tmp\.[a-zA-Z0-9]+\.dump", archive):  # noqa: S108 — validates mktemp output
        raise RuntimeError("Unexpected private archive path")
    try:
        # mktemp creates an exclusive private file, never a predictable shell path.
        run("pg_dump", "-p", str(args.port), "-Fc", "-f", archive, source)
        if run("stat", "-c", "%a", archive) != "600":
            raise RuntimeError("Backup permissions are not private")
        run("createdb", "-p", str(args.port), restored)
        created = True
        sql(restored, f"REVOKE ALL ON DATABASE {restored} FROM PUBLIC")
        # pg_dump without --create does not restore database-level privileges.
        for role, privilege, grantable in source_acl:
            if role not in {
                "postgres",
                "kryptroom_app",
                "kryptroom_migrator",
                "kryptroom_operator",
                "kryptroom_bff",
                "kryptroom_auth_guard",
            }:
                raise RuntimeError("Unexpected fixture database grantee")
            if privilege not in {"CONNECT", "CREATE", "TEMPORARY"} or type(grantable) is not bool:
                raise RuntimeError("Unexpected database privilege")
            grant_option = " WITH GRANT OPTION" if grantable else ""
            sql(restored, f"GRANT {privilege} ON DATABASE {restored} TO {role}{grant_option}")  # noqa: S608 — fixed allowlists
        run(
            "pg_restore",
            "-p",
            str(args.port),
            "--exit-on-error",
            "--single-transaction",
            "-d",
            restored,
            archive,
        )
        after = snapshot(restored)
        if before != after or before != snapshot(source) or database_acl(restored) != source_acl:
            raise RuntimeError("Restored data, grants, RLS or source integrity differs")
        print(
            json.dumps(
                {
                    "logical_restore": "PASS",
                    "archive_mode": "0600",
                    "postgres_major": 17,
                    "data_and_security": after,
                    "database_acl_equal": True,
                    "pitr": "NOT RUN",
                    "production_backup": "NOT RUN",
                },
                sort_keys=True,
            )
        )
    finally:
        run("rm", "-f", archive)
        if created:
            run("dropdb", "-p", str(args.port), restored)


if __name__ == "__main__":
    main()
