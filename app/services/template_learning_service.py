from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.execution import Execution, ExecutionItem
from app.models.template import TemplateItem


def _normalize_name(value: str | None) -> str:
    return " ".join((value or "").strip().casefold().split())


def _template_item_names(db: Session, template_id: int) -> set[str]:
    return {
        _normalize_name(name)
        for name in db.scalars(
            select(TemplateItem.name).where(TemplateItem.template_id == template_id)
        )
        if name
    }


def get_template_suggestions(db: Session, execution: Execution) -> list[dict]:
    """Detecta sugestões de aprendizado geradas por uma execução finalizada."""
    if not execution.template_id or execution.is_standalone:
        return []

    existing_template_names = _template_item_names(db, execution.template_id)
    items = db.scalars(
        select(ExecutionItem)
        .where(ExecutionItem.execution_id == execution.id)
        .order_by(ExecutionItem.sort_order, ExecutionItem.name)
    ).all()

    suggestions = []
    for item in items:
        item_name = _normalize_name(item.name)
        if item.template_item_id or item_name in existing_template_names:
            continue
        suggestions.append(
            {
                "type": "new_item",
                "template_id": execution.template_id,
                "execution_id": execution.id,
                "execution_item_id": item.id,
                "name": item.name,
                "category_id": item.category_id,
                "planned_quantity": item.planned_quantity,
                "notes": item.notes,
                "explanation": "Item adicionado durante a compra e ausente no template.",
            }
        )
    return suggestions
