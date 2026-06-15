import logging
from datetime import datetime, timezone, timedelta, date
from calendar import monthrange, month_name
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.user import User
from app.models.execution import Execution
from app.models.enums import ExecutionStatus, RecurrenceType

logger = logging.getLogger("jaci.agenda")

# Mapeamento de nomes de meses em português
MONTH_NAMES_PT = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


def get_executions_for_month(
    db: Session,
    group_id: int,
    year: int,
    month: int,
) -> list[Execution]:
    """Retorna todas as execuções de um mês para o grupo."""
    first_day = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        last_day = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        last_day = datetime(year, month + 1, 1, tzinfo=timezone.utc)

    return (
        db.execute(
            select(Execution)
            .where(
                Execution.group_id == group_id,
                Execution.scheduled_date >= first_day,
                Execution.scheduled_date < last_day,
            )
            .order_by(Execution.scheduled_date)
        )
        .scalars()
        .all()
    )


def get_executions_for_date(
    db: Session,
    group_id: int,
    date: datetime,
) -> list[Execution]:
    """Retorna execuções de uma data específica."""
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    return (
        db.execute(
            select(Execution)
            .where(
                Execution.group_id == group_id,
                Execution.scheduled_date >= start,
                Execution.scheduled_date < end,
            )
            .order_by(Execution.scheduled_date)
        )
        .scalars()
        .all()
    )


def build_calendar_data(
    db: Session,
    group_id: int,
    year: int,
    month: int,
    today: date
) -> dict:
    """
    Constrói os dados para o calendário mensal.
    Retorna semanas com dias e indicadores de execuções.
    """
    executions = get_executions_for_month(db, group_id, year, month)

    # Agrupa execuções por dia
    by_day: dict[int, list[Execution]] = {}
    for exec_item in executions:
        day = exec_item.scheduled_date.day
        if day not in by_day:
            by_day[day] = []
        by_day[day].append(exec_item)

    # Constrói grade do calendário
    first_day, days_in_month = monthrange(year, month)

    # Ajusta para segunda-feira como primeiro dia (0 = segunda)
    # Python calendar: 0 = segunda-feira
    start_offset = first_day

    weeks = []
    current_week = []

    # Preenche dias vazios antes do primeiro dia
    for _ in range(start_offset):
        current_week.append(None)

    # Preenche os dias do mês
    for day in range(1, days_in_month + 1):
        day_executions = by_day.get(day, [])

        # Determina indicadores
        has_completed = any(e.status == ExecutionStatus.completed for e in day_executions)
        has_in_progress = any(e.status == ExecutionStatus.in_progress for e in day_executions)
        has_scheduled = any(e.status == ExecutionStatus.scheduled for e in day_executions)
        has_cancelled = any(e.status == ExecutionStatus.cancelled for e in day_executions)

        # Prioridade do indicador: in_progress > scheduled > completed
        if has_in_progress:
            indicator = "in_progress"
        elif has_scheduled:
            indicator = "scheduled"
        elif has_completed:
            indicator = "completed"
        elif has_cancelled:
            indicator = "cancelled"
        else:
            indicator = None

        is_today = today.year == year and today.month == month and today.day == day

        current_week.append(
            {
                "day": day,
                "date": f"{year}-{month:02d}-{day:02d}",
                "is_today": is_today,
                "indicator": indicator,
                "count": len(day_executions),
                "has_completed": has_completed,
                "has_in_progress": has_in_progress,
                "has_scheduled": has_scheduled,
                "has_cancelled": has_cancelled,
            }
        )

        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []

    # Preenche dias restantes da última semana
    if current_week:
        while len(current_week) < 7:
            current_week.append(None)
        weeks.append(current_week)

    return {
        "year": year,
        "month": month,
        "month_name": MONTH_NAMES_PT.get(month, str(month)),
        "weeks": weeks,
        "total_executions": len(executions),
    }


def get_list_executions(
    db: Session,
    group_id: int,
    status: Optional[str] = None,
    period: Optional[str] = None,
) -> list[Execution]:
    """
    Retorna execuções para visualização em lista cronológica.
    Filtros: status, período (upcoming, past, all).
    """
    query = select(Execution).where(Execution.group_id == group_id)

    # Filtro de status
    if status:
        try:
            status_enum = ExecutionStatus(status)
            query = query.where(Execution.status == status_enum)
        except ValueError:
            pass

    # Filtro de período
    now = datetime.now(timezone.utc)
    if period == "upcoming":
        query = query.where(Execution.scheduled_date >= now)
    elif period == "past":
        query = query.where(Execution.scheduled_date < now)

    query = query.order_by(Execution.scheduled_date.desc())

    return db.execute(query).scalars().all()


def calculate_next_date(
    current_date: datetime,
    recurrence: RecurrenceType,
) -> datetime:
    """
    Calcula a próxima data baseada na recorrência.
    Usado para geração automática de próximos ciclos.
    """
    if recurrence == RecurrenceType.daily:
        return current_date + timedelta(days=1)

    elif recurrence == RecurrenceType.weekly:
        return current_date + timedelta(days=7)

    elif recurrence == RecurrenceType.biweekly:
        return current_date + timedelta(days=15)

    elif recurrence == RecurrenceType.monthly:
        # Mesmo dia do mês seguinte, com ajuste
        day = current_date.day
        month = current_date.month + 1
        year = current_date.year

        if month > 12:
            month = 1
            year += 1

        # Ajusta para meses mais curtos
        _, days_in_month = monthrange(year, month)
        if day > days_in_month:
            day = days_in_month

        return current_date.replace(year=year, month=month, day=day)

    elif recurrence == RecurrenceType.yearly:
        next_year = current_date.year + 1
        _, days_in_month = monthrange(next_year, current_date.month)
        return current_date.replace(year=next_year, day=min(current_date.day, days_in_month))

    return current_date


def reschedule_execution(
    db: Session,
    execution: Execution,
    new_date: datetime,
) -> Execution:
    """
    Adianta ou adia uma execução.
    Não altera o ciclo do template.
    """
    if execution.status == ExecutionStatus.in_progress:
        raise ValueError("Não é possível adiar/adiantar execução em andamento.")
    if execution.status == ExecutionStatus.completed:
        raise ValueError("Não é possível alterar execução já finalizada.")

    execution.scheduled_date = new_date
    db.commit()
    db.refresh(execution)
    logger.info(f"Execução {execution.id} reagendada para {new_date.date()}")
    return execution


def generate_next_execution(
    db: Session,
    execution: Execution,
    user: Optional[User]
) -> Optional[Execution]:
    """
    Gera a próxima execução do ciclo, se aplicável.
    Condições:
    - Execução vinculada a template ativo
    - Não é avulsa (is_avulsa=False)
    - Template está ativo
    - Não existe execução agendada futura do mesmo template
    """
    if execution.status != ExecutionStatus.completed or not execution.finished_at:
        return None
    if not execution.template_id:
        return None
    template = execution.template
    if not template or not template.is_active:
        return None
    if execution.is_standalone:
        return None
    # Calcula próxima data
    cycle_date = execution.finished_at or execution.scheduled_date
    next_date = calculate_next_date(cycle_date, template.recurrence)

    # Verifica se já existe execução agendada para esta data
    existing = db.scalar(
        select(func.count(Execution.id)).where(
            Execution.template_id == template.id,
            Execution.scheduled_date == next_date,
            Execution.status.in_(
                [
                    ExecutionStatus.scheduled,
                    ExecutionStatus.in_progress,
                ]
            ),
        )
    )
    if existing and existing > 0:
        logger.info(
            f"Próxima execução do template '{template.name}' "
            f"já existe para {next_date.date()}"
        )
        return None
    # Cria nova execução
    from app.services.execution_service import create_execution_from_template

    new_execution = create_execution_from_template(
        db,
        template,
        next_date,
        user,
    )
    logger.info(
        f"Próximo ciclo gerado: template '{template.name}' " f"para {next_date.date()}"
    )
    return new_execution
