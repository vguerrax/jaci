from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import ExecutionStatus


class Execution(Base):
    __tablename__ = "executions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    template_id: Mapped[int | None] = mapped_column(
        ForeignKey("templates.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    scheduled_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[ExecutionStatus] = mapped_column(
        String(20),
        default=ExecutionStatus.scheduled,
        nullable=False,
        index=True,
    )
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_standalone: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    current_location: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    template: Mapped["Template | None"] = relationship(
        "Template",
        back_populates="executions",
    )
    group: Mapped["Group"] = relationship("Group", back_populates="executions")
    items: Mapped[list["ExecutionItem"]] = relationship(
        "ExecutionItem",
        back_populates="execution",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Execution(id={self.id}, status='{self.status}')>"

    @property
    def display_name(self) -> str:
        if self.name and self.name.strip():
            return self.name.strip()
        return self.template.name if self.template else "Compra Avulsa"


class ExecutionItem(Base):
    __tablename__ = "execution_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    execution_id: Mapped[int] = mapped_column(
        ForeignKey("executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    template_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("template_items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    planned_quantity: Mapped[float] = mapped_column(Float, default=1, nullable=False)
    purchased_quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    notes: Mapped[str] = mapped_column(String(255), nullable=True)
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    execution: Mapped["Execution"] = relationship(
        "Execution",
        back_populates="items",
    )
    category: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="execution_items",
    )
    template_item: Mapped["TemplateItem | None"] = relationship("TemplateItem")

    @property
    def total_price(self) -> float | None:
        """Calcula o valor total do item (qtd * preço unitário)."""
        if self.purchased_quantity is not None and self.unit_price is not None:
            return round(self.purchased_quantity * self.unit_price, 2)
        return None

    def __repr__(self) -> str:
        return f"<ExecutionItem(id={self.id}, name='{self.name}', version={self.version})>"
