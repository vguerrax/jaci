import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.user import User
from app.models.group import Group, group_members
from app.models.template import Template, TemplateItem
from app.models.execution import Execution, ExecutionItem
from app.models.enums import ExecutionStatus

logger = logging.getLogger("jaci.executions")


# ─── Queries ───


def get_executions_for_group(
    db: Session,
    group_id: int,
    status: Optional[ExecutionStatus] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> list[Execution]:
    """Retorna execuções do grupo, com filtros opcionais."""
    query = select(Execution).where(Execution.group_id == group_id)
    if status:
        query = query.where(Execution.status == status)
    if date_from:
        query = query.where(Execution.scheduled_date >= date_from)
    if date_to:
        query = query.where(Execution.scheduled_date <= date_to)

    query = query.order_by(Execution.scheduled_date.desc())
    return db.execute(query).scalars().all()


def get_execution_by_id(
    db: Session, execution_id: int, user: User
) -> Optional[Execution]:
    """Retorna execução se pertencer a grupo do usuário."""
    return db.scalar(
        select(Execution)
        .join(Group, Execution.group_id == Group.id)
        .join(group_members, Group.id == group_members.c.group_id)
        .where(
            Execution.id == execution_id,
            group_members.c.user_id == user.id,
        )
    )


def get_execution_items_grouped(db: Session, execution_id: int) -> list[dict]:
    """Retorna itens da execução agrupados por categoria."""
    items = (
        db.execute(
            select(ExecutionItem)
            .where(ExecutionItem.execution_id == execution_id)
            .order_by(ExecutionItem.sort_order, ExecutionItem.name)
        )
        .scalars()
        .all()
    )

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
        else:
            no_category.append(item)

    result = list(grouped.values())
    if no_category:
        result.append({"category": None, "items": no_category})

    return result


def get_execution_totals(db: Session, execution_id: int) -> dict:
    """Calcula totais da execução."""
    items = (
        db.execute(
            select(ExecutionItem).where(ExecutionItem.execution_id == execution_id)
        )
        .scalars()
        .all()
    )

    total_items = len(items)
    completed_items = sum(1 for item in items if item.is_completed)
    total_spent = sum(
        (item.purchased_quantity or 0) * (item.unit_price or 0)
        for item in items
        if item.is_completed
    )

    return {
        "total_items": total_items,
        "completed_items": completed_items,
        "remaining_items": total_items - completed_items,
        "total_spent": round(total_spent, 2),
    }


# ─── Criação ───


def create_execution_from_template(
    db: Session,
    template: Template,
    scheduled_date: datetime,
    created_by: User,
    budget: Optional[float] = None,
    is_standalone: bool = False,
) -> Execution:
    """Cria uma execução a partir de um template, copiando seus itens."""
    execution = Execution(
        template_id=template.id,
        group_id=template.group_id,
        scheduled_date=scheduled_date,
        status=ExecutionStatus.scheduled,
        budget=budget if budget is not None and budget > 0 else template.budget,
        is_standalone=is_standalone,
        created_by=created_by.id,
    )
    db.add(execution)
    db.flush()

    # Copia itens do template
    for tpl_item in template.items:
        exec_item = ExecutionItem(
            execution_id=execution.id,
            name=tpl_item.name,
            category_id=tpl_item.category_id,
            planned_quantity=tpl_item.planned_quantity,
            sort_order=tpl_item.sort_order,
        )
        db.add(exec_item)

    db.commit()
    db.refresh(execution)
    logger.info(
        f"Execução criada do template '{template.name}' "
        f"para {scheduled_date.date()}"
    )
    return execution


def create_execution_standalone(
    db: Session,
    group: Group,
    scheduled_date: datetime,
    created_by: User,
    budget: Optional[float] = None,
) -> Execution:
    """Cria uma execução avulsa sem template."""
    execution = Execution(
        template_id=None,
        group_id=group.id,
        scheduled_date=scheduled_date,
        status=ExecutionStatus.scheduled,
        budget=budget if budget > 0 else None,
        is_standalone=True,
        created_by=created_by.id,
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    logger.info(f"Execução avulsa criada para {scheduled_date.date()}")
    return execution


# ─── Execução ───


def start_execution(db: Session, execution: Execution) -> Execution:
    """Inicia a execução (status -> in_progress)."""
    execution.status = ExecutionStatus.in_progress
    db.commit()
    db.refresh(execution)
    logger.info(f"Execução {execution.id} iniciada")
    return execution


def complete_item(
    db: Session,
    item: ExecutionItem,
    purchased_quantity: float,
    unit_price: float,
    location: Optional[str] = None,
) -> ExecutionItem:
    """Marca item como comprado com quantidade e valor."""
    item.purchased_quantity = purchased_quantity
    item.unit_price = unit_price
    item.location = location
    item.is_completed = True
    item.version += 1

    if location:
        execution = item.execution
        execution.current_location = location
        db.add(execution)

    db.commit()
    db.refresh(item)
    logger.info(f"Item '{item.name}' concluído: {purchased_quantity}x R${unit_price}")
    return item


def incomplete_item(
    db: Session,
    item: ExecutionItem,
) -> ExecutionItem:
    """Marca item como não comprado"""
    item.purchased_quantity = None
    item.unit_price = None
    item.location = None
    item.is_completed = False
    item.version += 1
    db.commit()
    db.refresh(item)
    logger.info(f"Item '{item.name}' devolvido.")
    return item


def add_item_to_execution(
    db: Session,
    execution: Execution,
    name: str,
    planned_quantity: float = 1,
    category_id: Optional[int] = None,
) -> ExecutionItem:
    """Adiciona item durante a execução (não afeta o template)."""
    max_order = db.scalar(
        select(func.max(ExecutionItem.sort_order)).where(
            ExecutionItem.execution_id == execution.id
        )
    )
    item = ExecutionItem(
        execution_id=execution.id,
        name=name.strip(),
        planned_quantity=planned_quantity,
        category_id=category_id,
        sort_order=(max_order or 0) + 1,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    logger.info(f"Item '{item.name}' adicionado durante execução")
    return item


def remove_item_from_execution(db: Session, item: ExecutionItem) -> None:
    """Remove item não concluído da execução."""
    if item.is_completed:
        raise ValueError("Não é possível remover item já concluído.")
    item_name = item.name
    db.delete(item)
    db.commit()
    logger.info(f"Item '{item_name}' removido da execução")


# ─── Finalização ───


def get_pending_items(db: Session, execution_id: int) -> list[ExecutionItem]:
    """Retorna itens não concluídos da execução."""
    return (
        db.execute(
            select(ExecutionItem).where(
                ExecutionItem.execution_id == execution_id,
                ExecutionItem.is_completed == False,
            )
        )
        .scalars()
        .all()
    )


def finalize_execution(
    db: Session,
    execution: Execution,
    discard_pending: bool = True,
) -> Execution:
    """
    Finaliza a execução.
    Se discard_pending=True, remove itens não concluídos.
    Se discard_pending=False, quem chama deve tratar os pendentes antes.
    """
    if discard_pending:
        pending = get_pending_items(db, execution.id)
        for item in pending:
            item.is_deleted = True
            db.commit()

    execution.status = ExecutionStatus.completed
    execution.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(execution)

    totals = get_execution_totals(db, execution.id)
    logger.info(
        f"Execução {execution.id} finalizada. " f"Total: R${totals['total_spent']}"
    )
    return execution


def cancel_execution(db: Session, execution: Execution) -> Execution:
    """Cancela a execução."""
    if execution.status == ExecutionStatus.completed:
        raise ValueError("Não é possível cancelar execução já finalizada.")

    execution.status = ExecutionStatus.cancelled
    db.commit()
    db.refresh(execution)
    logger.info(f"Execução {execution.id} cancelada")
    return execution


def create_execution_from_pending(
    db: Session,
    original_execution: Execution,
    pending_items: list[ExecutionItem],
    new_date: datetime,
) -> Execution:
    """
    Cria nova execução avulsa com os itens pendentes.
    Os itens são removidos da execução original.
    """
    new_execution = Execution(
        template_id=original_execution.template_id,
        group_id=original_execution.group_id,
        scheduled_date=new_date,
        status=ExecutionStatus.scheduled,
        budget=original_execution.budget,
        is_standalone=True,
        created_by=original_execution.created_by,
    )
    db.add(new_execution)
    db.flush()

    for item in pending_items:
        new_item = ExecutionItem(
            execution_id=new_execution.id,
            name=item.name,
            category_id=item.category_id,
            planned_quantity=item.planned_quantity,
            sort_order=item.sort_order,
        )
        db.add(new_item)
        item.is_deleted = True
        db.commit()

    db.commit()
    db.refresh(new_execution)
    logger.info(
        f"Nova execução criada com {len(pending_items)} pendentes "
        f"para {new_date.date()}"
    )
    return new_execution


# ─── Orçamento ───


def check_budget_alerts(total_spent: float, budget: float) -> list[dict]:
    """
    Verifica alertas de orçamento.
    Retorna lista de alertas (nível, mensagem).
    """
    if budget <= 0:
        return []

    percent = (total_spent / budget) * 100
    alerts = []

    if percent >= 100:
        over = total_spent - budget
        alerts.append(
            {
                "level": "danger",
                "message": f"💸 Orçamento estourado em R$ {over:.2f}!",
                "percent": percent,
            }
        )
    elif percent >= 95:
        remaining = budget - total_spent
        alerts.append(
            {
                "level": "warning",
                "message": f"🔴 Alerta: você está a R$ {remaining:.2f} de estourar o orçamento!",
                "percent": percent,
            }
        )
    elif percent >= 80:
        alerts.append(
            {
                "level": "info",
                "message": f"⚠️ Atenção: você atingiu {percent:.0f}% do orçamento (R$ {total_spent:.2f} de R$ {budget:.2f})",
                "percent": percent,
            }
        )

    return alerts


#
def generate_next_execution(db: Session, execution: Execution, user: User):
    from app.services.agenda_service import (
        generate_next_execution,
        calculate_next_date,
    )

    # Calcula a próxima data baseada na recorrência
    next_date = calculate_next_date(
        execution.scheduled_date, execution.template.recurrence
    )

    # Verifica se já existe execução agendada para essa data
    existing = db.scalar(
        select(func.count(Execution.id)).where(
            Execution.template_id == execution.template_id,
            Execution.scheduled_date == next_date,
            Execution.status.in_(
                [
                    ExecutionStatus.scheduled,
                    ExecutionStatus.in_progress,
                ]
            ),
        )
    )

    if not existing or existing == 0:
        # Cria nova execução para o próximo ciclo
        from app.services.execution_service import create_execution_from_template

        new_execution = create_execution_from_template(
            db,
            execution.template,
            next_date,
            user,  # O usuário que finalizou é o "criador" da próxima
            execution.template.budget,
            is_avulsa=False,
        )
        logger.info(
            f"Próximo ciclo gerado: template '{execution.template.name}' "
            f"para {next_date.strftime('%d/%m/%Y')}"
        )
