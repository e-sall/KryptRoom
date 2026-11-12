from io import StringIO
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from kryptroom_control.migration_safety import protect_history


def config():
    return Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))


@pytest.mark.parametrize("target", ["base", "0004_collaboration", "0005_action_guard"])
def test_history_downgrade_refused_by_default(settings, target):
    with pytest.raises(RuntimeError, match="History-losing downgrade blocked"):
        protect_history(settings, config(), ("0006_room_history",), target)


def test_only_explicit_disposable_test_reset_is_allowed(settings):
    c = config()
    c.attributes["allow_disposable_history_loss"] = True
    for environment, database in [("local", "kryptroom_test"), ("test", "kryptroom")]:
        with pytest.raises(RuntimeError):
            protect_history(
                settings.model_copy(update={"environment": environment, "database_name": database}),
                c,
                ("0006_room_history",),
                "base",
            )
    protect_history(
        settings.model_copy(update={"environment": "test", "database_name": "kryptroom_test"}),
        c,
        ("0006_room_history",),
        "base",
    )
    protect_history(settings, config(), ("0004_collaboration",), "head")


def test_offline_sql_does_not_emit_destructive_statements(monkeypatch):
    monkeypatch.setenv("CONTROL_DATABASE_PASSWORD", "synthetic-migration-policy-password")
    monkeypatch.setenv("CONTROL_ENVIRONMENT", "local")
    c = config()
    c.output_buffer = StringIO()
    with pytest.raises(RuntimeError, match="History-losing downgrade blocked"):
        command.downgrade(c, "0006_room_history:0005_action_guard", sql=True)
    assert "DROP " not in c.output_buffer.getvalue()
