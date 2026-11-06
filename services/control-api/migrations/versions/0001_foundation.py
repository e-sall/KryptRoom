"""Foundation marker only: no user, organization, Room, audit or cryptographic data."""

import sqlalchemy as sa
from alembic import op

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    marker = op.create_table(
        "foundation_metadata",
        sa.Column("singleton", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("contract", sa.String(48), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("singleton", name="pk_foundation_metadata"),
        sa.CheckConstraint("singleton = true", name=op.f("ck_foundation_metadata_singleton")),
        sa.CheckConstraint(
            "contract = 'm9-control-foundation-v1'", name=op.f("ck_foundation_metadata_contract")
        ),
        schema="control_api",
    )
    op.bulk_insert(marker, [{"singleton": True, "contract": "m9-control-foundation-v1"}])


def downgrade() -> None:
    # This destroys only the PR1 technical marker, never historical Core artifacts.
    op.drop_table("foundation_metadata", schema="control_api")
