"""Bounded two-organization metadata collaboration."""

from pathlib import Path

from alembic import op

revision = "0004_collaboration"
down_revision = "0003_persistent_rooms"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(Path(__file__).with_name("0004_collaboration.sql").read_text())


def downgrade() -> None:
    op.execute("""
    DROP POLICY room_read ON control_api.rooms;
    CREATE POLICY room_read ON control_api.rooms FOR SELECT TO kryptroom_app
      USING (control_api.active_role(organization_id) IS NOT NULL);
    DROP FUNCTION control_api.room_collaboration(uuid,uuid,uuid,text,integer,uuid,text);
    DROP FUNCTION control_api.room_participants(uuid);
    DROP FUNCTION control_api.shared_room_ids(uuid);
    DROP FUNCTION control_api.room_access(uuid);
    DROP TABLE control_api.room_collaboration_events,control_api.room_invitations;
    REVOKE UPDATE(id) ON control_api.rooms FROM kryptroom_auth_guard;
    """)
