from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tupa_user_id: Mapped[str | None] = mapped_column(
        String(36), unique=True, index=True, nullable=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    is_profile_complete: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary="group_members",
        back_populates="members",
        lazy="selectin",
    )
    owned_groups: Mapped[list["Group"]] = relationship(
        "Group",
        back_populates="owner",
        foreign_keys="Group.owner_id",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"
