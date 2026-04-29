import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.user import User
from app.models.group import Group, group_members
from app.models.category import Category
from app.models.template import Template, TemplateItem
from app.models.execution import Execution, ExecutionStatus
from app.models.enums import RecurrenceType

logger = logging.getLogger("jaci.templates")


def get_templates_by_group(
    db: Session, group_id: int, include_inactive: bool = False
) -> list[Template]:
    """Retorna templates do grupo, opcionalmente incluindo inativos."""
    query = select(Template).where(Template.group_id == group_id)
    if not include_inactive:
        query = query.where(Template.is_active == True)
    query = query.order_by(Template.name)
    return db.execute(query).scalars().all()


def get_template_by_id(
    db: Session, template_id: int, user: User
) -> Optional[Template]:
    """Retorna template se pertencer a um grupo do usuário."""
    return db.scalar(
        select(Template)
        .join(Group, Template.group_id == Group.id)
        .join(group_members, Group.id == group_members.c.group_id)
        .where(
            Template.id == template_id,
            group_members.c.user_id == user.id,
        )
    )


def get_template_items_grouped(db: Session, template_id: int) -> list[dict]:
    """
    Retorna itens do template agrupados por categoria.
    Cada grupo é um dict com 'category' e 'items'.
    """
    items = (
        db.execute(
            select(TemplateItem)
            .where(TemplateItem.template_id == template_id)
            .order_by(TemplateItem.sort_order, TemplateItem.name)
        )
        .scalars()
        .all()
    )

    # Group by category
    grouped = {}
    no_category = []

    for item in items:
        if item.category:
            cat_name = item.category.name
            if cat_name not in grouped:
                grouped[cat_name] = {
                    "category": item.category,
                    "items": [],
                }
            grouped[cat_name]["items"].append(item)
            grouped[cat_name]["items"].sort(key=lambda x: x.name)
        else:
            no_category.append(item)
            no_category.sort(key=lambda x: x.name)

    result = list(grouped.values())
    if no_category:
        result.append({
            "category": None,
            "items": no_category,
        })

    result.sort(key=lambda x: x["category"].name if x["category"] else 'ZZZZZZZZZZZZZZ')

    return result


def create_template(
    db: Session,
    group: Group,
    name: str,
    recurrence: RecurrenceType,
    budget: Optional[float] = None,
) -> Template:
    """Cria um novo template no grupo."""
    template = Template(
        name=name.strip(),
        recurrence=recurrence,
        budget=budget,
        group_id=group.id,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    logger.info(f"Template '{template.name}' criado no grupo '{group.name}'")
    return template


def update_template(
    db: Session,
    template: Template,
    name: str,
    recurrence: RecurrenceType,
    budget: Optional[float] = None,
) -> Template:
    """Atualiza dados básicos do template."""
    template.name = name.strip()
    template.recurrence = recurrence
    if budget is not None and budget != '':
        try:
            template.budget = float(budget)
        except (ValueError, TypeError):
            template.budget = None
    else:
        template.budget = None
    template.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(template)
    logger.info(f"Template '{template.name}' atualizado")
    return template


def toggle_template_active(db: Session, template: Template) -> Template:
    """Alterna o status active do template."""
    template.is_active = not template.is_active
    template.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(template)
    status = "ativado" if template.is_active else "desativado"
    logger.info(f"Template '{template.name}' {status}")
    return template


def count_active_executions(db: Session, template_id: int) -> dict:
    """
    Conta execuções ativas (não finalizadas, não canceladas)
    vinculadas a este template.
    """
    scheduled = db.scalar(
        select(func.count(Execution.id)).where(
            Execution.template_id == template_id,
            Execution.status == ExecutionStatus.scheduled,
        )
    )
    in_progress = db.scalar(
        select(func.count(Execution.id)).where(
            Execution.template_id == template_id,
            Execution.status == ExecutionStatus.in_progress,
        )
    )
    return {
        "scheduled": scheduled or 0,
        "in_progress": in_progress or 0,
        "total": (scheduled or 0) + (in_progress or 0),
    }


def can_delete_template(db: Session, template: Template) -> tuple[bool, str]:
    """
    Verifica se o template pode ser excluído.
    Retorna (pode_excluir, mensagem).
    """
    counts = count_active_executions(db, template.id)
    if counts["total"] > 0:
        return False, (
            f"Não é possível excluir: {counts['total']} execução(ões) "
            f"ativa(s) vinculada(s) a este template."
        )
    return True, ""


def delete_template(db: Session, template: Template) -> None:
    """Exclui template e seus itens (cascade)."""
    name = template.name
    db.delete(template)
    db.commit()
    logger.info(f"Template '{name}' excluído")


def add_item_to_template(
    db: Session,
    template: Template,
    name: str,
    planned_quantity: float,
    category_id: Optional[int] = None,
) -> TemplateItem:
    """Adiciona um item ao template."""
    # Get max sort_order
    max_order = db.scalar(
        select(func.max(TemplateItem.sort_order)).where(
            TemplateItem.template_id == template.id
        )
    )

    item = TemplateItem(
        template_id=template.id,
        name=name.strip(),
        planned_quantity=planned_quantity,
        category_id=category_id,
        sort_order=(max_order or 0) + 1,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    logger.info(f"Item '{item.name}' adicionado ao template '{template.name}'")
    return item


def get_template_item_by_id(
    db: Session, item_id: int, user: User
) -> Optional[TemplateItem]:
    """Retorna item do template se pertencer a grupo do usuário."""
    return db.scalar(
        select(TemplateItem)
        .join(Template, TemplateItem.template_id == Template.id)
        .join(Group, Template.group_id == Group.id)
        .join(group_members, Group.id == group_members.c.group_id)
        .where(
            TemplateItem.id == item_id,
            group_members.c.user_id == user.id,
        )
    )


def update_template_item(
    db: Session,
    item: TemplateItem,
    name: str,
    planned_quantity: float,
    category_id: Optional[int] = None,
) -> TemplateItem:
    """Atualiza um item do template."""
    item.name = name.strip()
    item.planned_quantity = planned_quantity
    item.category_id = category_id
    db.commit()
    db.refresh(item)
    logger.info(f"Item '{item.name}' atualizado")
    return item


def remove_template_item(db: Session, item: TemplateItem) -> None:
    """Remove um item do template."""
    item_name = item.name
    db.delete(item)
    db.commit()
    logger.info(f"Item '{item_name}' removido do template")


def get_categories_for_group(db: Session, group_id: int) -> list[Category]:
    """Retorna categorias disponíveis para o grupo."""
    return (
        db.execute(
            select(Category)
            .where(Category.group_id == group_id)
            .order_by(Category.name)
        )
        .scalars()
        .all()
    )