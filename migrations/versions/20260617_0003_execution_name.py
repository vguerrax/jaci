"""execution name

Revision ID: 20260617_0003
Revises: 20260616_0002
Create Date: 2026-06-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260617_0003"
down_revision: Union[str, None] = "20260616_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("executions", sa.Column("name", sa.String(length=150), nullable=True))


def downgrade() -> None:
    op.drop_column("executions", "name")
