"""Upgrade a real disposable PR1 PostgreSQL database, preserving its original marker."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

SERVICE = Path(__file__).resolve().parents[1]
NAME = "kr-m9-pr2-pr1-upgrade"
PG_IMAGE = (
    "postgres:17.11-bookworm@sha256:"
    "839fbb5a4942a7758dd93e18b42ea5649807491a0545b5eeeb8f0b8bb11857a5"
)
LABEL = "kryptroom.m9.pr2.fixture=pr1-upgrade"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--disposable", action="store_true", required=True)
    parser.parse_args()
    if os.name != "posix" or os.geteuid() != 0:
        raise RuntimeError("Native fixture controller required")
    docker = shutil.which("docker")
    if docker is None:
        raise RuntimeError("Docker required")

    def call(*args: str, data: bytes | None = None, check: bool = True) -> str:
        result = subprocess.run(  # noqa: S603 — fixed trusted local executable/actions, no shell
            [docker, *args], input=data, capture_output=True, check=False, timeout=180
        )  # noqa: S603 — fixed trusted local calls
        if check and result.returncode:
            raise RuntimeError("Disposable PR1 upgrade command failed; no credential displayed")
        return result.stdout.decode().strip()

    fixture = SERVICE / "tests/fixtures/pr1-init-db.sh"
    provenance = json.loads((fixture.parent / "pr1-baseline.json").read_text())
    if hashlib.sha256(fixture.read_bytes()).hexdigest() != provenance["init_db_sha256"]:
        raise ValueError("Original PR1 bootstrap fixture changed")
    migration = SERVICE / "migrations/versions/0001_foundation.py"
    if hashlib.sha256(migration.read_bytes()).hexdigest() != provenance["migration_0001_sha256"]:
        raise ValueError("Historical PR1 migration changed")
    runtime = SERVICE / ".runtime/pr1-upgrade"
    runtime.mkdir(mode=0o700)
    projected = runtime / "pg-secrets"
    projected.mkdir(mode=0o700)
    for source in (SERVICE / ".runtime/secrets").iterdir():
        if source.name not in {
            "postgres_password",
            "migrator_password",
            "app_password",
            "operator_password",
            "bff_password",
            "keycloak_password",
        }:
            continue
        path = projected / source.name
        path.write_bytes(source.read_bytes())
        path.chmod(0o400)
        os.chown(path, 999, 999)
    os.chown(projected, 999, 999)
    migrate = runtime / "migrate"
    migrate.mkdir(mode=0o700)
    path = migrate / "migrator_password"
    path.write_bytes((projected / "migrator_password").read_bytes())
    path.chmod(0o400)
    os.chown(path, 10001, 10001)
    os.chown(migrate, 10001, 10001)
    # Existing resources under this unique name are never silently overwritten.
    if call("ps", "-aq", "--filter", "name=^/" + NAME + "$", check=False):
        raise RuntimeError("Disposable upgrade container already exists")
    if call("volume", "ls", "-q", "--filter", "name=^" + NAME + "-data$") or call(
        "network", "ls", "-q", "--filter", "name=^" + NAME + "$"
    ):
        raise RuntimeError("Existing upgrade resources require explicit inspection")
    created_network = created_volume = False
    try:
        call("network", "create", "--internal", "--label", LABEL, NAME)
        created_network = True
        call("volume", "create", "--label", LABEL, NAME + "-data")
        created_volume = True
        call(
            "run",
            "-d",
            "--name",
            NAME,
            "--label",
            LABEL,
            "--network",
            NAME,
            "-e",
            "POSTGRES_DB=kryptroom",
            "-e",
            "POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password",
            "-e",
            "POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256 --auth-local=trust",
            "--mount",
            f"type=volume,source={NAME}-data,target=/var/lib/postgresql/data",
            "--mount",
            f"type=bind,source={projected},target=/run/secrets,readonly",
            "--mount",
            f"type=bind,source={fixture},target=/docker-entrypoint-initdb.d/10-pr1.sh,readonly",
            PG_IMAGE,
            "postgres",
            "-c",
            "log_statement=none",
            "-c",
            "log_min_error_statement=panic",
            "-c",
            "log_parameter_max_length_on_error=0",
        )
        for _ in range(100):
            result = call(
                "exec",
                NAME,
                "pg_isready",
                "-h",
                "127.0.0.1",
                "-U",
                "postgres",
                "-d",
                "kryptroom",
                check=False,
            )
            if "accepting connections" in result:
                break
            time.sleep(0.2)
        else:
            raise RuntimeError("Original PR1 PostgreSQL bootstrap did not become ready")
        call("build", "--target", "runtime", "-t", NAME + "-migrate", str(SERVICE))

        def migrate_to(revision: str) -> None:
            call(
                "run",
                "--rm",
                "--network",
                NAME,
                "--read-only",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges:true",
                "--mount",
                f"type=bind,source={migrate},target=/run/secrets,readonly",
                "-e",
                "CONTROL_DATABASE_HOST=" + NAME,
                "-e",
                "CONTROL_DATABASE_NAME=kryptroom",
                "-e",
                "CONTROL_DATABASE_USER=kryptroom_migrator",
                "-e",
                "CONTROL_DATABASE_PASSWORD_FILE=/run/secrets/migrator_password",
                "-e",
                "CONTROL_DATABASE_SSLMODE=disable",
                NAME + "-migrate",
                "alembic",
                "upgrade",
                revision,
            )

        def query(sql: str) -> str:
            return call(
                "exec",
                "-u",
                "postgres",
                NAME,
                "psql",
                "-At",
                "-U",
                "postgres",
                "-d",
                "kryptroom",
                "-c",
                sql,
            )

        migrate_to("0001_foundation")
        before = query("SELECT row_to_json(m)::text FROM control_api.foundation_metadata m")
        if query("SELECT count(*) FROM pg_roles WHERE rolname LIKE 'kryptroom_%'") != "2":
            raise RuntimeError("Expected exactly the original two PR1 roles")
        call(
            "exec",
            "-i",
            "-u",
            "postgres",
            NAME,
            "sh",
            "-s",
            data=(SERVICE / "scripts/upgrade-identity-roles.sh").read_bytes(),
        )
        migrate_to("head")
        migrate_to("head")
        if before != query("SELECT row_to_json(m)::text FROM control_api.foundation_metadata m"):
            raise RuntimeError("PR1 foundation marker changed during upgrade")
        if (
            query("SELECT version_num FROM control_api.alembic_version")
            != "0002_identity_organizations"
        ):
            raise RuntimeError("Wrong upgrade revision")
        print(
            json.dumps(
                {
                    "original_pr1_bootstrap": provenance["init_db_sha256"],
                    "original_pr1_roles": 2,
                    "upgrade": "passed",
                    "marker_byte_value_preserved": True,
                    "repeat_alembic_upgrade": "passed",
                    "runtime_role_creation_privilege_added": False,
                }
            )
        )
    finally:
        call("rm", "-f", NAME, check=False)
        if created_volume:
            call("volume", "rm", NAME + "-data", check=False)
        if created_network:
            call("network", "rm", NAME, check=False)


if __name__ == "__main__":
    main()
