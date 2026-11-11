"""PR3 business metadata; never a RoomState or participant dataset."""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from kryptroom_control.db import Base

rooms = sa.Table(
    "rooms",
    Base.metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "organization_id", sa.Uuid(), sa.ForeignKey("control_api.organizations.id"), nullable=False
    ),
    sa.Column(
        "created_by_user_id", sa.Uuid(), sa.ForeignKey("control_api.users.id"), nullable=False
    ),
    sa.Column("display_name", sa.String(120), nullable=False),
    sa.Column("description", sa.String(1000), nullable=False, server_default=""),
    sa.Column("status", sa.String(16), nullable=False, server_default="DRAFT"),
    sa.Column("head_state_id", sa.Uuid(), nullable=True),
    sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    sa.Column(
        "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    ),
    sa.Column(
        "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    ),
    sa.CheckConstraint("length(btrim(display_name)) BETWEEN 1 AND 120", name="display_name"),
    sa.CheckConstraint("status='DRAFT'", name="draft_only"),
    sa.CheckConstraint("head_state_id IS NULL", name="no_room_state"),
    sa.CheckConstraint("version>0", name="positive_version"),
)
sa.Index("rooms_organization_page", rooms.c.organization_id, rooms.c.id)

room_requests = sa.Table(
    "room_creation_requests",
    Base.metadata,
    sa.Column("user_id", sa.Uuid(), sa.ForeignKey("control_api.users.id"), primary_key=True),
    sa.Column(
        "organization_id",
        sa.Uuid(),
        sa.ForeignKey("control_api.organizations.id"),
        primary_key=True,
    ),
    sa.Column("key", sa.String(128), primary_key=True),
    sa.Column("request_hash", sa.String(64), nullable=False),
    sa.Column("response", JSONB(), nullable=False),
)
