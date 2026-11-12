"""Sessão do navegador, sem senha nem token em claro."""
from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AccessSession(Base):
    __tablename__ = 'access_sessions'
    id_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    subject: Mapped[str] = mapped_column(String(64), nullable=False)
    product_id: Mapped[str] = mapped_column(String(64), nullable=False)
    provider: Mapped[str] = mapped_column(String(8), nullable=False)
    authenticated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    access_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    encrypted_tokens: Mapped[str] = mapped_column(Text, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reason: Mapped[str | None] = mapped_column(String(32))
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    __table_args__ = (
        Index('ix_access_sessions_user_id', 'user_id'),
        Index('ix_access_sessions_expires_at', 'expires_at'),
        CheckConstraint('last_activity_at >= authenticated_at', name='ck_access_session_activity'),
        CheckConstraint('expires_at > last_activity_at', name='ck_access_session_expiry'),
        CheckConstraint("provider in ('tupa', 'mock')", name='ck_access_session_provider'),
    )
