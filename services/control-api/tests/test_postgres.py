import logging
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError

from kryptroom_control.app import create_app
from kryptroom_control.config import Settings
from kryptroom_control.db import SCHEMA_REVISION, Database

pytestmark = pytest.mark.postgres


@pytest.fixture(scope="module")
def migrated(postgres_settings: Settings) -> Iterator[Database]:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    db = Database(postgres_settings)
    command.downgrade(config, "base")
    with TestClient(create_app(postgres_settings)) as client:
        assert client.get("/health/live").status_code == 200
        assert client.get("/health/ready").status_code == 503
    command.upgrade(config, "head")
    command.upgrade(config, "head")
    command.check(config)
    assert db.ready()
    yield db
    db.close()


def test_schema_version_constraints_and_metadata_only(migrated: Database) -> None:
    with migrated.transaction() as session:
        assert (
            session.scalar(text("SELECT version_num FROM control_api.alembic_version"))
            == SCHEMA_REVISION
        )
        assert session.scalars(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='control_api' ORDER BY table_name"
            )
        ).all() == ["alembic_version", "foundation_metadata"]
        count = session.scalar(text("SELECT count(*) FROM control_api.foundation_metadata"))
        assert count == 1
        constraints = session.scalars(
            text(
                "SELECT conname FROM pg_constraint "
                "WHERE conrelid='control_api.foundation_metadata'::regclass"
            )
        ).all()
        assert set(constraints) == {
            "pk_foundation_metadata",
            "ck_foundation_metadata_singleton",
            "ck_foundation_metadata_contract",
        }
        assert session.scalar(text("SHOW timezone")) in {"UTC", "Etc/UTC"}
    with pytest.raises(IntegrityError), migrated.transaction() as session:
        session.execute(
            text(
                "INSERT INTO control_api.foundation_metadata(singleton,contract) "
                "VALUES(false,'bad')"
            )
        )


def test_transaction_commit_and_rollback(migrated: Database) -> None:
    with migrated.transaction() as session:
        session.execute(text("CREATE TABLE control_api.transaction_probe (id integer PRIMARY KEY)"))
        session.execute(text("INSERT INTO control_api.transaction_probe VALUES(1)"))
    try:
        with pytest.raises(RuntimeError), migrated.transaction() as session:
            session.execute(text("INSERT INTO control_api.transaction_probe VALUES(2)"))
            raise RuntimeError("abort synthetic transaction")
        with migrated.transaction() as session:
            assert session.scalars(text("SELECT id FROM control_api.transaction_probe")).all() == [
                1
            ]
    finally:
        with migrated.transaction() as session:
            session.execute(text("DROP TABLE control_api.transaction_probe"))


def test_runtime_role_readiness_and_least_privilege(
    migrated: Database,
    postgres_settings: Settings,
    app_password: SecretStr,
) -> None:
    settings = postgres_settings.model_copy(
        update={
            "database_user": "kryptroom_app",
            "database_password": app_password,
            "database_password_file": None,
        }
    )
    db = Database(settings)
    try:
        assert db.ready()
        with db.transaction() as session:
            assert (
                session.scalar(text("SELECT rolsuper FROM pg_roles WHERE rolname=current_user"))
                is False
            )
        for statement in [
            "CREATE TABLE control_api.unauthorized(id integer)",
            "DELETE FROM control_api.foundation_metadata",
        ]:
            with pytest.raises(DBAPIError), db.transaction() as session:
                session.execute(text(statement))
        # A new app/engine reloads the persisted schema; no create_all/auto migration.
        for _ in range(2):
            with TestClient(create_app(settings)) as client:
                assert client.get("/health/ready").status_code == 200
                assert client.get("/health/live").status_code == 200
    finally:
        db.close()


def test_missing_and_wrong_revision_fail_closed(migrated: Database) -> None:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    with migrated.transaction() as session:
        session.execute(text("UPDATE control_api.alembic_version SET version_num='unknown'"))
    try:
        assert not migrated.ready()
    finally:
        with migrated.transaction() as session:
            session.execute(
                text("UPDATE control_api.alembic_version SET version_num=:version"),
                {"version": SCHEMA_REVISION},
            )
    command.downgrade(config, "base")
    try:
        assert not migrated.ready()
    finally:
        command.upgrade(config, "head")
    assert migrated.ready()


def test_authentication_failure_redacts_real_driver_errors(
    migrated: Database,
    postgres_settings: Settings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    sentinel = "wrong-database-credential-0123456789"  # noqa: S105 — deliberate leakage sentinel
    settings = postgres_settings.model_copy(
        update={
            "database_user": "kryptroom_app",
            "database_password": SecretStr(sentinel),
            "database_password_file": None,
        }
    )
    with TestClient(create_app(settings)) as client, caplog.at_level(logging.INFO):
        response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "not_ready"
    assert sentinel not in response.text
    assert sentinel not in caplog.text
