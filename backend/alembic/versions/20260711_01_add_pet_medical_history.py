"""Add has_medical_history to pets."""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260711_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pets",
        sa.Column("has_medical_history", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("pets", "has_medical_history")
