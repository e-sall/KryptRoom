"""PR2 metadata only. No Room, cryptographic artifact or participant data tables."""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from kryptroom_control.db import Base

m = Base.metadata


def enum(name: str, *values: str) -> sa.Enum:
    return sa.Enum(*values, name=name, schema="control_api")


user_status = enum("user_status", "ACTIVE", "SUSPENDED")
org_status = enum("organization_status", "PENDING_REVIEW", "ACTIVE", "SUSPENDED", "REJECTED")
verification = enum("verification_status", "UNVERIFIED", "REVIEWED")
role = enum("organization_role", "ORG_OWNER", "ORG_ADMIN", "ORG_MEMBER")
member_status = enum("membership_status", "PENDING", "ACTIVE", "REVOKED")


def identifier() -> sa.Column[UUID]:
    return sa.Column("id", sa.Uuid(), primary_key=True)


def fk(name: str, target: str, *, nullable: bool = False) -> sa.Column[UUID]:
    return sa.Column(name, sa.Uuid(), sa.ForeignKey("control_api." + target), nullable=nullable)


def timestamp(name: str, *, nullable: bool = False) -> sa.Column[datetime]:
    return sa.Column(
        name,
        sa.DateTime(timezone=True),
        nullable=nullable,
        server_default=None if nullable else sa.func.now(),
    )


def version() -> sa.Column[int]:
    return sa.Column("version", sa.BigInteger(), nullable=False, server_default="1")


users = sa.Table(
    "users",
    m,
    identifier(),
    sa.Column("status", user_status, nullable=False, server_default="ACTIVE"),
    sa.Column("display_name", sa.String(120), nullable=False),
    sa.Column("email_snapshot", sa.String(254)),
    timestamp("created_at"),
    timestamp("updated_at"),
    version(),
    sa.CheckConstraint("version > 0", name="version"),
)
identity_links = sa.Table(
    "identity_links",
    m,
    identifier(),
    fk("user_id", "users.id"),
    sa.Column("issuer", sa.String(512), nullable=False),
    sa.Column("subject", sa.String(255), nullable=False),
    timestamp("linked_at"),
    timestamp("last_authenticated_at"),
    sa.UniqueConstraint("issuer", "subject", name="uq_identity_links_issuer_subject"),
)
organizations = sa.Table(
    "organizations",
    m,
    identifier(),
    sa.Column("display_name", sa.String(120), nullable=False),
    sa.Column("status", org_status, nullable=False, server_default="PENDING_REVIEW"),
    sa.Column("verification_status", verification, nullable=False, server_default="UNVERIFIED"),
    fk("requested_by_user_id", "users.id"),
    sa.Column("review_reference", sa.String(120)),
    timestamp("created_at"),
    timestamp("reviewed_at", nullable=True),
    timestamp("updated_at"),
    version(),
    sa.CheckConstraint("version > 0", name="version"),
)
memberships = sa.Table(
    "organization_memberships",
    m,
    identifier(),
    fk("organization_id", "organizations.id"),
    fk("user_id", "users.id"),
    sa.Column("role", role, nullable=False),
    sa.Column("status", member_status, nullable=False),
    timestamp("created_at"),
    timestamp("activated_at", nullable=True),
    timestamp("revoked_at", nullable=True),
    timestamp("updated_at"),
    version(),
    fk("granted_by_user_id", "users.id", nullable=True),
    sa.UniqueConstraint("organization_id", "user_id", name="uq_memberships_organization_user"),
    sa.CheckConstraint("version > 0", name="version"),
)
events = sa.Table(
    "organization_access_events",
    m,
    identifier(),
    fk("organization_id", "organizations.id", nullable=True),
    fk("actor_user_id", "users.id", nullable=True),
    sa.Column("operator_reference", sa.String(120)),
    sa.Column("case_reference", sa.String(120)),
    sa.Column("kind", sa.String(48), nullable=False),
    timestamp("created_at"),
)
idempotency = sa.Table(
    "idempotency_records",
    m,
    fk("user_id", "users.id"),
    sa.Column("key", sa.String(128), nullable=False),
    sa.Column("request_hash", sa.String(64), nullable=False),
    sa.Column("response", JSONB(), nullable=False),
    timestamp("created_at"),
    sa.PrimaryKeyConstraint("user_id", "key", name="pk_idempotency_records"),
)
sessions = sa.Table(
    "sessions",
    m,
    sa.Column("id_hash", sa.String(64), primary_key=True),
    fk("user_id", "users.id"),
    sa.Column("issuer", sa.String(512), nullable=False),
    sa.Column("subject", sa.String(255), nullable=False),
    sa.Column("provider_sid", sa.String(255)),
    sa.Column("encrypted_access_token", sa.Text(), nullable=False),
    sa.Column("encrypted_refresh_token", sa.Text()),
    timestamp("token_expires_at"),
    timestamp("created_at"),
    timestamp("last_seen_at"),
    timestamp("idle_expires_at"),
    timestamp("absolute_expires_at"),
    timestamp("revoked_at", nullable=True),
    sa.Column("encryption_key_id", sa.String(48), nullable=False),
    version(),
    schema="bff_auth",
)
transactions = sa.Table(
    "oidc_transactions",
    m,
    sa.Column("state_hash", sa.String(64), primary_key=True),
    sa.Column("browser_hash", sa.String(64), nullable=False),
    sa.Column("encrypted_payload", sa.Text(), nullable=False),
    timestamp("expires_at"),
    schema="bff_auth",
)
logout_replays = sa.Table(
    "logout_replays",
    m,
    sa.Column("issuer", sa.String(512), primary_key=True),
    sa.Column("jti", sa.String(255), primary_key=True),
    timestamp("expires_at"),
    schema="bff_auth",
)

sa.Index("ix_memberships_user_status", memberships.c.user_id, memberships.c.status)
sa.Index("ix_sessions_provider_sid", sessions.c.issuer, sessions.c.provider_sid)
