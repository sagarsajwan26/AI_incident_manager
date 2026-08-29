"""added the incident model and update the user model

Revision ID: e6c2ed458290
Revises: d119cd8b1008
Create Date: 2026-08-28 15:39:32.377269
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "e6c2ed458290"
down_revision: Union[str, Sequence[str], None] = "d119cd8b1008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    bind = op.get_bind()

    # 1. Create the PostgreSQL enum for UserRole
    user_role_enum = postgresql.ENUM(
        "MEMBER",
        "INVESTIGATOR",
        "ADMIN",
        name="userrole",
    )

    user_role_enum.create(bind, checkfirst=True)

    # 2. Change users.role from VARCHAR to ENUM
    op.alter_column(
        "users",
        "role",
        existing_type=sa.VARCHAR(length=20),
        type_=postgresql.ENUM(
            "MEMBER",
            "INVESTIGATOR",
            "ADMIN",
            name="userrole",
        ),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    bind = op.get_bind()

    # 1. Change users.role back to VARCHAR
    op.alter_column(
        "users",
        "role",
        existing_type=postgresql.ENUM(
            "MEMBER",
            "INVESTIGATOR",
            "ADMIN",
            name="userrole",
        ),
        type_=sa.VARCHAR(length=20),
        existing_nullable=False,
    )

    # 2. Remove the enum type
    user_role_enum = postgresql.ENUM(
        "MEMBER",
        "INVESTIGATOR",
        "ADMIN",
        name="userrole",
    )

    user_role_enum.drop(bind, checkfirst=True)
