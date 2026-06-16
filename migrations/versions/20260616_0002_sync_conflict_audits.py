"""sync conflict audits

Revision ID: 20260616_0002
Revises: 20260615_0001
Create Date: 2026-06-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260616_0002"
down_revision: Union[str, None] = "20260615_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sync_conflict_audits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("execution_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("operation_type", sa.String(length=80), nullable=False),
        sa.Column("entity", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.String(length=80), nullable=False),
        sa.Column("reason", sa.String(length=120), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("local_state", sa.JSON(), nullable=False),
        sa.Column("remote_state", sa.JSON(), nullable=True),
        sa.Column("resolution_applied", sa.String(length=80), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["execution_id"], ["executions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sync_conflict_audits_execution_id", "sync_conflict_audits", ["execution_id"], unique=False)
    op.create_index("ix_sync_conflict_audits_group_id", "sync_conflict_audits", ["group_id"], unique=False)
    op.create_index("ix_sync_conflict_audits_user_id", "sync_conflict_audits", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sync_conflict_audits_user_id", table_name="sync_conflict_audits")
    op.drop_index("ix_sync_conflict_audits_group_id", table_name="sync_conflict_audits")
    op.drop_index("ix_sync_conflict_audits_execution_id", table_name="sync_conflict_audits")
    op.drop_table("sync_conflict_audits")
