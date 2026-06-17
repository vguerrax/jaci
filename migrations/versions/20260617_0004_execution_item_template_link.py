"""execution item template link

Revision ID: 20260617_0004
Revises: 20260617_0003
Create Date: 2026-06-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260617_0004"
down_revision: Union[str, None] = "20260617_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("execution_items") as batch_op:
        batch_op.add_column(sa.Column("template_item_id", sa.Integer(), nullable=True))
        batch_op.create_index(
            "ix_execution_items_template_item_id",
            ["template_item_id"],
            unique=False,
        )
        batch_op.create_foreign_key(
            "fk_execution_items_template_item_id_template_items",
            "template_items",
            ["template_item_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("execution_items") as batch_op:
        batch_op.drop_constraint(
            "fk_execution_items_template_item_id_template_items",
            type_="foreignkey",
        )
        batch_op.drop_index("ix_execution_items_template_item_id")
        batch_op.drop_column("template_item_id")
