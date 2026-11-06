"""Identity, controlled organizations and isolated BFF persistence.

Frozen SQL snapshot; no import of mutable application model definitions.
"""

from pathlib import Path

from alembic import op

revision = "0002_identity_organizations"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    directory = Path(__file__).parent
    for name in ("0002_schema.sql", "0002_security.sql"):
        op.execute((directory / name).read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute("""
        DROP FUNCTION control_api.resolve_identity(uuid,uuid,text,text,text,text);
        DROP FUNCTION control_api.lookup_identity(text,text);
        DROP FUNCTION control_api.lock_current_user();
        DROP TABLE bff_auth.logout_replays, bff_auth.oidc_transactions, bff_auth.sessions;
        DROP TABLE control_api.idempotency_records, control_api.organization_access_events,
            control_api.organization_memberships, control_api.organizations,
            control_api.identity_links, control_api.users CASCADE;
        DROP FUNCTION IF EXISTS control_api.current_actor();
        DROP FUNCTION IF EXISTS control_api.active_role(uuid);
        DROP TYPE control_api.membership_status, control_api.organization_role,
            control_api.verification_status, control_api.organization_status,
            control_api.user_status;
    """)
