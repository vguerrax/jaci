import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.user import User
from app.models.group import Group, group_members
from app.models.category import Category
from app.models.template import Template, TemplateItem
from app.models.execution import Execution, ExecutionItem
from app.models.enums import ExecutionStatus

logger = logging.getLogger("jaci.executions")


def ensure_execution_is_mutable(execution: Execution) -> None:
    """Impede qualquer alteração em uma execução já finalizada."""
    if execution.status == ExecutionStatus.completed:
        raise ValueError("Não é possível alterar execução já finalizada.")


def get_execution_display_name(execution: Execution) -> str:
    """Retorna o nome próprio da execução, preservando fallback legado."""
    return execution.display_name


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
    group = db.scalar(
        select(Group)
        .join(Execution, Execution.group_id == Group.id)
        .where(Execution.id == execution_id)
    )
    items = (
        db.execute(
            select(ExecutionItem)
            .where(
                ExecutionItem.execution_id == execution_id,
                ExecutionItem.is_deleted == False,
            )
            .order_by(ExecutionItem.sort_order, ExecutionItem.name)
        )
        .scalars()
        .all()
    )

    grouped = {}
    no_category = []

    for item in items:
        if item.category:
            if item.category.id not in grouped:
                grouped[item.category.id] = {
                    "category": item.category,
                    "items": [],
                }
            grouped[item.category.id]["items"].append(item)
            grouped[item.category.id]["items"].sort(key=lambda x: x.name)
        else:
            no_category.append(item)
            no_category.sort(key=lambda x: x.name)

    result = list(grouped.values())
    result.sort(key=lambda item: (item["category"].sort_order, item["category"].name))

    if no_category:
        uncategorized_group = {"category": None, "items": no_category}
        if group and group.uncategorized_first:
            result.insert(0, uncategorized_group)
        else:
            result.append(uncategorized_group)
    return result


def get_execution_totals(db: Session, execution_id: int) -> dict:
    """Calcula totais da execução."""
    items = (
        db.execute(
            select(ExecutionItem).where(
                ExecutionItem.execution_id == execution_id,
                ExecutionItem.is_deleted == False,
            )
        )
        .scalars()
        .all()
    )

    total_items = len(items)
    completed_items = sum(1 for item in items if item.is_completed)
    # Soma os mesmos totais em centavos exibidos por item para a conta fechar
    # exatamente com o que o usuário vê na lista.
    total_spent = sum(
        item.total_price or 0
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
        name=template.name,
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
            template_item_id=tpl_item.id,
            name=tpl_item.name,
            category_id=tpl_item.category_id,
            planned_quantity=tpl_item.planned_quantity,
            notes=tpl_item.notes,
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
    name: Optional[str] = None,
) -> Execution:
    """Cria uma execução avulsa sem template."""
    normalized_name = (name or "").strip() or "Compra Avulsa"
    if len(normalized_name) > 150:
        raise ValueError("Nome da execução deve ter no máximo 150 caracteres.")

    execution = Execution(
        template_id=None,
        group_id=group.id,
        name=normalized_name,
        scheduled_date=scheduled_date,
        status=ExecutionStatus.scheduled,
        budget=budget if budget is not None and budget > 0 else None,
        is_standalone=True,
        created_by=created_by.id,
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    logger.info(f"Execução avulsa criada para {scheduled_date.date()}")
    return execution


def update_scheduled_execution(
    db: Session,
    execution: Execution,
    name: str,
    scheduled_date: datetime,
    budget: Optional[float] = None,
) -> Execution:
    """Edita somente dados próprios de uma execução agendada."""
    if execution.status != ExecutionStatus.scheduled:
        raise ValueError("Apenas execuções agendadas podem ser editadas.")

    normalized_name = name.strip()
    if not normalized_name:
        raise ValueError("Nome da execução é obrigatório.")
    if len(normalized_name) > 150:
        raise ValueError("Nome da execução deve ter no máximo 150 caracteres.")
    if budget is not None and budget < 0:
        raise ValueError("Orçamento não pode ser negativo.")
    if (
        execution.template_id is not None
        and normalized_name != get_execution_display_name(execution)
    ):
        raise ValueError("Apenas compras avulsas sem lista podem ter o nome alterado.")

    if execution.template_id is None:
        execution.name = normalized_name
    execution.scheduled_date = scheduled_date
    execution.budget = budget if budget is not None and budget > 0 else None
    db.commit()
    db.refresh(execution)
    logger.info(f"Execução {execution.id} atualizada enquanto agendada")
    return execution


# ─── Execução ───


def start_execution(db: Session, execution: Execution) -> Execution:
    """Inicia a execução (status -> in_progress)."""
    ensure_execution_is_mutable(execution)
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
    notes: Optional[str] = None,
) -> ExecutionItem:
    """Marca item como comprado com quantidade e valor."""
    ensure_execution_is_mutable(item.execution)
    item.purchased_quantity = purchased_quantity
    item.unit_price = unit_price
    item.location = location
    item.notes = notes
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
    ensure_execution_is_mutable(item.execution)
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
    notes: Optional[str] = None,
    unit_price: Optional[float] = None,
) -> ExecutionItem:
    """Adiciona item à execução sem alterar o template associado."""
    ensure_execution_is_mutable(execution)
    if execution.status == ExecutionStatus.cancelled:
        raise ValueError("Não é possível alterar execução cancelada.")

    is_purchased = execution.status == ExecutionStatus.in_progress
    if is_purchased and (unit_price is None or unit_price <= 0):
        raise ValueError("Valor unitário deve ser maior que zero.")

    if category_id is not None:
        category_group_id = db.scalar(
            select(Category.group_id).where(Category.id == category_id)
        )
        if category_group_id != execution.group_id:
            raise ValueError("Categoria não pertence ao grupo da execução.")

    max_order = db.scalar(
        select(func.max(ExecutionItem.sort_order)).where(
            ExecutionItem.execution_id == execution.id
        )
    )
    item = ExecutionItem(
        execution_id=execution.id,
        name=name.strip(),
        planned_quantity=planned_quantity,
        purchased_quantity=planned_quantity if is_purchased else None,
        unit_price=unit_price if is_purchased else None,
        is_completed=is_purchased,
        category_id=category_id,
        notes=notes,
        sort_order=(max_order or 0) + 1,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    logger.info(
        "Item '%s' adicionado à execução como %s",
        item.name,
        "comprado" if item.is_completed else "pendente",
    )
    return item


def remove_item_from_execution(db: Session, item: ExecutionItem) -> None:
    """Remove item não concluído da execução."""
    ensure_execution_is_mutable(item.execution)
    if item.is_completed:
        raise ValueError("Não é possível remover item já concluído.")
    item_name = item.name
    db.delete(item)
    db.commit()
    logger.info(f"Item '{item_name}' removido da execução")
    
    
def update_execution_item(db: Session, item: ExecutionItem, name: str, planned_quantity: float, category_id: int | None, notes: Optional[str] = None) -> ExecutionItem:
    ensure_execution_is_mutable(item.execution)
    if category_id is not None:
        category_group_id = db.scalar(
            select(Category.group_id).where(Category.id == category_id)
        )
        if category_group_id != item.execution.group_id:
            raise ValueError("Categoria não pertence ao grupo da execução.")

    if item.name != name:
        item.name = name
    if item.planned_quantity != planned_quantity:
        item.planned_quantity = planned_quantity
    if item.category_id != category_id:
        item.category_id = category_id
    if item.notes != notes:
        item.notes =  notes
    item.version += 1
    db.commit()
    db.refresh(item)
    return item

# ─── Finalização ───


def get_pending_items(db: Session, execution_id: int) -> list[ExecutionItem]:
    """Retorna itens não concluídos da execução."""
    return (
        db.execute(
            select(ExecutionItem).where(
                ExecutionItem.execution_id == execution_id,
                ExecutionItem.is_completed == False,
                ExecutionItem.is_deleted == False,
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
    ensure_execution_is_mutable(execution)
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
    ensure_execution_is_mutable(original_execution)
    new_execution = Execution(
        template_id=original_execution.template_id,
        group_id=original_execution.group_id,
        name=get_execution_display_name(original_execution),
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
