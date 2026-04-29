from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import RecurrenceType


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    recurrence: Mapped[RecurrenceType] = mapped_column(
        String(20),
        default=RecurrenceType.monthly,
        nullable=False,
    )
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    group: Mapped["Group"] = relationship("Group", back_populates="templates")
    items: Mapped[list["TemplateItem"]] = relationship(
        "TemplateItem",
        back_populates="template",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    executions: Mapped[list["Execution"]] = relationship(
        "Execution",
        back_populates="template",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Template(id={self.id}, name='{self.name}')>"


class TemplateItem(Base):
    __tablename__ = "template_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    planned_quantity: Mapped[float] = mapped_column(Float, default=1, nullable=False)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    template: Mapped["Template"] = relationship("Template", back_populates="items")
    category: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="template_items",
    )

    def __repr__(self) -> str:
        return f"<TemplateItem(id={self.id}, name='{self.name}')>"