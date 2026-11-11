import sqlalchemy as sa

from kryptroom_control.db import Base

invitations = sa.Table(
    "room_invitations",
    Base.metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("room_id", sa.Uuid(), sa.ForeignKey("control_api.rooms.id"), nullable=False),
    sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("control_api.organizations.id"), nullable=False),
    sa.Column(
        "target_id", sa.Uuid(), sa.ForeignKey("control_api.organizations.id"), nullable=False
    ),
    sa.Column("actor_id", sa.Uuid(), sa.ForeignKey("control_api.users.id"), nullable=False),
    sa.Column("request_key", sa.String(128), nullable=False),
    sa.Column("status", sa.Text(), nullable=False),
    sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    sa.UniqueConstraint("room_id", "actor_id", "request_key", name="room_request_unique"),
)
sa.Index(
    "room_one_partner",
    invitations.c.room_id,
    unique=True,
    postgresql_where=sa.text("status IN ('PENDING','ACCEPTED')"),
)
events = sa.Table(
    "room_collaboration_events",
    Base.metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "invitation_id", sa.Uuid(), sa.ForeignKey("control_api.room_invitations.id"), nullable=False
    ),
    sa.Column("actor_id", sa.Uuid(), sa.ForeignKey("control_api.users.id"), nullable=False),
    sa.Column("actor_org", sa.Uuid(), nullable=False),
    sa.Column("kind", sa.Text(), nullable=False),
    sa.Column(
        "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    ),
)
