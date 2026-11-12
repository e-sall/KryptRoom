"""Catch up databases that already ran the pre-fix 0004 snapshot."""

from pathlib import Path

from alembic import op

revision = "0005_action_guard"
down_revision = "0004_collaboration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(Path(__file__).with_suffix(".sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    # 0004's fixed contract is compatible; never restore the NULL-action disclosure.
    pass
