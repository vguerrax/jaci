from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Table, Column, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Tabela associativa Usuário <-> Grupo (M:N)
group_members = Table(
    "group_members",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
    Column("joined_at", DateTime(timezone=True), server_default=func.now()),
)


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    uncategorized_first: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="owned_groups",
        foreign_keys=[owner_id],
        lazy="selectin",
    )
    members: Mapped[list["User"]] = relationship(
        "User",
        secondary=group_members,
        back_populates="groups",
        lazy="selectin",
    )
    categories: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="group",
        lazy="selectin",
        order_by="Category.sort_order, Category.name",
    )
    templates: Mapped[list["Template"]] = relationship(
        "Template",
        back_populates="group",
        lazy="selectin",
    )
    executions: Mapped[list["Execution"]] = relationship(
        "Execution",
        back_populates="group",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Group(id={self.id}, name='{self.name}')>"
