"""Business history metadata, never cryptographic evidence."""

import sqlalchemy as sa

from kryptroom_control.db import Base

room_history = sa.Table(
    "room_operational_events",
    Base.metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("room_id", sa.Uuid(), sa.ForeignKey("control_api.rooms.id"), nullable=False),
    sa.Column(
        "actor_org", sa.Uuid(), sa.ForeignKey("control_api.organizations.id"), nullable=False
    ),
    sa.Column("actor_user_id", sa.Uuid(), sa.ForeignKey("control_api.users.id"), nullable=False),
    sa.Column("invitation_id", sa.Uuid(), sa.ForeignKey("control_api.room_invitations.id")),
    sa.Column("kind", sa.Text(), nullable=False),
    sa.Column(
        "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    ),
)
sa.Index(
    "room_operational_page", room_history.c.room_id, room_history.c.created_at, room_history.c.id
)
