"""Persistir sessões de acesso por dispositivo (BL-0019), sem tocar compras."""
from alembic import op
import sqlalchemy as sa

revision = '20261110_0006'
down_revision = '20260617_0005'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('access_sessions',
        sa.Column('id_hash',sa.String(64),primary_key=True),
        sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id'),nullable=False),
        sa.Column('subject',sa.String(64),nullable=False),
        sa.Column('product_id',sa.String(64),nullable=False),
        sa.Column('provider',sa.String(8),nullable=False),
        sa.Column('authenticated_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('last_activity_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('expires_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('access_expires_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('encrypted_tokens',sa.Text(),nullable=False),
        sa.Column('revoked_at',sa.DateTime(timezone=True)),
        sa.Column('reason',sa.String(32)),
        sa.Column('version',sa.Integer(),nullable=False,server_default='1'),
        sa.CheckConstraint('last_activity_at >= authenticated_at',name='ck_access_session_activity'),
        sa.CheckConstraint('expires_at > last_activity_at',name='ck_access_session_expiry'),
        sa.CheckConstraint("provider in ('tupa', 'mock')",name='ck_access_session_provider'))
    op.create_index('ix_access_sessions_user_id','access_sessions',['user_id'])
    op.create_index('ix_access_sessions_expires_at','access_sessions',['expires_at'])


def downgrade():
    connection=op.get_bind()
    count=connection.execute(sa.text('SELECT count(*) FROM access_sessions')).scalar()
    if count:
        raise RuntimeError('Downgrade exige tratamento explícito das sessões; não apagar registros automaticamente.')
    op.drop_table('access_sessions')
