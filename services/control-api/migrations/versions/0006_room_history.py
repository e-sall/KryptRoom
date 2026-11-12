"""Narrow business history, separate from cryptographic evidence."""

from pathlib import Path

from alembic import op

revision = "0006_room_history"
down_revision = "0005_action_guard"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(Path(__file__).with_suffix(".sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute("""
        DROP TRIGGER room_history_append ON control_api.rooms;
        DROP TRIGGER collaboration_history_append ON control_api.room_collaboration_events;
        DROP FUNCTION control_api.append_room_history();
        DROP FUNCTION control_api.room_history(uuid,uuid,integer);
        DROP TABLE control_api.room_operational_events;
    """)
