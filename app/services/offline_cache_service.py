from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.execution import Execution, ExecutionItem
from app.models.template import Template, TemplateItem
from app.models.user import User


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _enum_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def build_offline_snapshot(db: Session, user: User) -> dict[str, Any]:
    """Monta dados essenciais somente leitura para consulta offline."""
    group_ids = [group.id for group in user.groups]
    if not group_ids:
        return {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "groups": [],
            "categories": [],
            "templates": [],
            "template_items": [],
            "executions": [],
            "execution_items": [],
        }

    categories = db.scalars(
        select(Category)
        .where(Category.group_id.in_(group_ids))
        .order_by(Category.group_id, Category.sort_order, Category.name)
    ).all()
    templates = db.scalars(
        select(Template)
        .where(Template.group_id.in_(group_ids))
        .order_by(Template.group_id, Template.is_active.desc(), Template.name)
    ).all()
    template_ids = [template.id for template in templates]
    template_items = (
        db.scalars(
            select(TemplateItem)
            .where(TemplateItem.template_id.in_(template_ids))
            .order_by(TemplateItem.template_id, TemplateItem.sort_order, TemplateItem.name)
        ).all()
        if template_ids
        else []
    )
    executions = db.scalars(
        select(Execution)
        .where(Execution.group_id.in_(group_ids))
        .order_by(
            Execution.finished_at.desc().nullslast(),
            Execution.scheduled_date.desc(),
            Execution.id.desc(),
        )
        .limit(20)
    ).all()
    execution_ids = [execution.id for execution in executions]
    execution_items = (
        db.scalars(
            select(ExecutionItem)
            .where(ExecutionItem.execution_id.in_(execution_ids))
            .order_by(ExecutionItem.execution_id, ExecutionItem.sort_order, ExecutionItem.name)
        ).all()
        if execution_ids
        else []
    )

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "groups": [
            {
                "id": group.id,
                "name": group.name,
                "owner_id": group.owner_id,
                "uncategorized_first": group.uncategorized_first,
                "created_at": _iso(group.created_at),
            }
            for group in sorted(user.groups, key=lambda group: group.name)
        ],
        "categories": [
            {
                "id": category.id,
                "group_id": category.group_id,
                "name": category.name,
                "color": category.color,
                "sort_order": category.sort_order,
            }
            for category in categories
        ],
        "templates": [
            {
                "id": template.id,
                "group_id": template.group_id,
                "name": template.name,
                "recurrence": _enum_value(template.recurrence),
                "budget": template.budget,
                "is_active": template.is_active,
                "updated_at": _iso(template.updated_at),
            }
            for template in templates
        ],
        "template_items": [
            {
                "id": item.id,
                "template_id": item.template_id,
                "category_id": item.category_id,
                "name": item.name,
                "planned_quantity": item.planned_quantity,
                "notes": item.notes,
                "sort_order": item.sort_order,
            }
            for item in template_items
        ],
        "executions": [
            {
                "id": execution.id,
                "group_id": execution.group_id,
                "template_id": execution.template_id,
                "status": _enum_value(execution.status),
                "scheduled_date": _iso(execution.scheduled_date),
                "finished_at": _iso(execution.finished_at),
                "budget": execution.budget,
                "is_standalone": execution.is_standalone,
            }
            for execution in executions
        ],
        "execution_items": [
            {
                "id": item.id,
                "execution_id": item.execution_id,
                "category_id": item.category_id,
                "name": item.name,
                "planned_quantity": item.planned_quantity,
                "purchased_quantity": item.purchased_quantity,
                "unit_price": item.unit_price,
                "location": item.location,
                "is_completed": item.is_completed,
                "notes": item.notes,
                "version": item.version,
                "sort_order": item.sort_order,
            }
            for item in execution_items
        ],
    }
