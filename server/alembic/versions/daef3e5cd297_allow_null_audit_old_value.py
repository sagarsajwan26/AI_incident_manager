"""allow null audit old value

Revision ID: daef3e5cd297
Revises: c699ae301567
Create Date: 2026-08-30 15:43:34.089715

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "daef3e5cd297"
down_revision: Union[str, Sequence[str], None] = "c699ae301567"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "incident_audit_logs",
        "old_value",
        existing_type=sa.Text(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "incident_audit_logs",
        "old_value",
        existing_type=sa.Text(),
        nullable=False,
    )
