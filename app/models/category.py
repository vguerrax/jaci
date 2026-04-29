from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Categorias padrão criadas no primeiro acesso do grupo
DEFAULT_CATEGORIES = [
    {"name": "Mantimentos", "color": "#D9B382"},
    {"name": "Limpeza", "color": "#A7C7B1"},
    {"name": "Hortifruti", "color": "#8DB89A"},
    {"name": "Açougue", "color": "#E6B89C"},
    {"name": "Laticínios", "color": "#F5F0E8"},
    {"name": "Bebidas", "color": "#9B6A4A"},
    {"name": "Higiene Pessoal", "color": "#D9C4B0"},
    {"name": "Padaria", "color": "#D9B382"},
]


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)  # #RRGGBB
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    group: Mapped["Group"] = relationship("Group", back_populates="categories")
    template_items: Mapped[list["TemplateItem"]] = relationship(
        "TemplateItem",
        back_populates="category",
        lazy="selectin",
    )
    execution_items: Mapped[list["ExecutionItem"]] = relationship(
        "ExecutionItem",
        back_populates="category",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}')>"