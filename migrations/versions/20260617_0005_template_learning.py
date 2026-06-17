"""template learning

Revision ID: 20260617_0005
Revises: 20260617_0004
Create Date: 2026-06-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260617_0005"
down_revision: Union[str, None] = "20260617_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "groups",
        sa.Column(
            "template_learning_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.create_table(
        "template_learning_dismissals",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("execution_id", sa.Integer(), nullable=False),
        sa.Column("suggestion_type", sa.String(length=30), nullable=False),
        sa.Column("execution_item_id", sa.Integer(), nullable=True),
        sa.Column("template_item_id", sa.Integer(), nullable=True),
        sa.Column("value", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["execution_id"], ["executions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["execution_item_id"], ["execution_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["template_item_id"], ["template_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "execution_id",
            "suggestion_type",
            "execution_item_id",
            "template_item_id",
            "value",
            name="uq_template_learning_dismissal",
        ),
    )
    op.create_index(
        "ix_template_learning_dismissals_execution_id",
        "template_learning_dismissals",
        ["execution_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_template_learning_dismissals_execution_id",
        table_name="template_learning_dismissals",
    )
    op.drop_table("template_learning_dismissals")
    op.drop_column("groups", "template_learning_enabled")
