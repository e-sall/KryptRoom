"""Persistent draft Room metadata, with tenant policies installed atomically."""

from pathlib import Path

from alembic import op

revision = "0003_persistent_rooms"
down_revision = "0002_identity_organizations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(Path(__file__).with_name("0003_rooms.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute("DROP TABLE control_api.room_creation_requests, control_api.rooms")
