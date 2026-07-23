from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TemplateLearningDismissal(Base):
    __tablename__ = "template_learning_dismissals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    execution_id: Mapped[int] = mapped_column(
        ForeignKey("executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    suggestion_type: Mapped[str] = mapped_column(String(30), nullable=False)
    execution_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("execution_items.id", ondelete="CASCADE"),
        nullable=True,
    )
    template_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("template_items.id", ondelete="CASCADE"),
        nullable=True,
    )
    value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    execution: Mapped["Execution"] = relationship("Execution")

    __table_args__ = (
        UniqueConstraint(
            "execution_id",
            "suggestion_type",
            "execution_item_id",
            "template_item_id",
            "value",
            name="uq_template_learning_dismissal",
        ),
    )
