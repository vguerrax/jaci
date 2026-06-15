from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.enums import ExecutionStatus
from app.models.execution import Execution, ExecutionItem
from app.services.execution_service import get_execution_totals


def _execution_name(execution: Execution) -> str:
    return execution.template.name if execution.template else "Compra Avulsa"


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def get_priority_execution(
    db: Session,
    group_id: int,
    now: datetime,
) -> Execution | None:
    """Retorna a compra mais relevante: em andamento, depois agendada."""
    in_progress = db.scalar(
        select(Execution)
        .where(
            Execution.group_id == group_id,
            Execution.status == ExecutionStatus.in_progress,
        )
        .order_by(Execution.scheduled_date.asc(), Execution.id.asc())
        .limit(1)
    )
    if in_progress:
        return in_progress

    return db.scalar(
        select(Execution)
        .where(
            Execution.group_id == group_id,
            Execution.status == ExecutionStatus.scheduled,
        )
        .order_by(
            case((Execution.scheduled_date >= now, 0), else_=1),
            Execution.scheduled_date.asc(),
            Execution.id.asc(),
        )
        .limit(1)
    )


def get_home_metrics(db: Session, group_id: int, now: datetime) -> dict:
    """Calcula indicadores rápidos do grupo ativo."""
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (
        month_start.replace(year=month_start.year + 1, month=1)
        if month_start.month == 12
        else month_start.replace(month=month_start.month + 1)
    )

    scheduled = db.scalar(
        select(func.count(Execution.id)).where(
            Execution.group_id == group_id,
            Execution.status == ExecutionStatus.scheduled,
        )
    ) or 0
    in_progress = db.scalar(
        select(func.count(Execution.id)).where(
            Execution.group_id == group_id,
            Execution.status == ExecutionStatus.in_progress,
        )
    ) or 0

    completed_this_month = db.scalars(
        select(Execution).where(
            Execution.group_id == group_id,
            Execution.status == ExecutionStatus.completed,
            Execution.finished_at >= month_start,
            Execution.finished_at < next_month,
        )
    ).all()
    month_spent = round(
        sum(get_execution_totals(db, execution.id)["total_spent"] for execution in completed_this_month),
        2,
    )

    pending_items = db.scalar(
        select(func.count(ExecutionItem.id))
        .join(Execution, ExecutionItem.execution_id == Execution.id)
        .where(
            Execution.group_id == group_id,
            Execution.status.in_(
                [ExecutionStatus.scheduled, ExecutionStatus.in_progress]
            ),
            ExecutionItem.is_completed == False,
            ExecutionItem.is_deleted == False,
        )
    ) or 0

    return {
        "scheduled": scheduled,
        "in_progress": in_progress,
        "month_spent": month_spent,
        "pending_items": pending_items,
    }


def get_recent_history(db: Session, group_id: int, limit: int = 3) -> list[dict]:
    """Retorna as compras concluídas mais recentes do grupo."""
    executions = db.scalars(
        select(Execution)
        .where(
            Execution.group_id == group_id,
            Execution.status == ExecutionStatus.completed,
        )
        .order_by(Execution.finished_at.desc(), Execution.id.desc())
        .limit(limit)
    ).all()
    return [
        {
            "execution": execution,
            "name": _execution_name(execution),
            "totals": get_execution_totals(db, execution.id),
        }
        for execution in executions
    ]


def get_home_alerts(
    db: Session,
    group_id: int,
    now: datetime,
    limit: int = 3,
) -> list[dict]:
    """Retorna alertas contextuais ordenados por criticidade."""
    active = db.scalars(
        select(Execution).where(
            Execution.group_id == group_id,
            Execution.status.in_(
                [ExecutionStatus.scheduled, ExecutionStatus.in_progress]
            ),
        )
    ).all()

    alerts: list[dict] = []
    for execution in active:
        name = _execution_name(execution)
        totals = get_execution_totals(db, execution.id)

        if execution.budget and totals["total_spent"] > execution.budget:
            alerts.append(
                {
                    "priority": 0,
                    "level": "danger",
                    "icon": "bi-exclamation-octagon-fill",
                    "message": f"{name} ultrapassou o orçamento.",
                    "url": f"/executions/{execution.id}",
                }
            )
        if execution.status == ExecutionStatus.in_progress:
            alerts.append(
                {
                    "priority": 1,
                    "level": "warning",
                    "icon": "bi-bag-heart-fill",
                    "message": f"{name} está em andamento.",
                    "url": f"/executions/{execution.id}",
                }
            )
        if (
            execution.status == ExecutionStatus.scheduled
            and _as_utc(now)
            <= _as_utc(execution.scheduled_date)
            <= _as_utc(now) + timedelta(hours=24)
        ):
            alerts.append(
                {
                    "priority": 2,
                    "level": "info",
                    "icon": "bi-calendar-event-fill",
                    "message": f"{name} está agendada para as próximas 24 horas.",
                    "url": f"/executions/{execution.id}",
                }
            )

    alerts.sort(key=lambda alert: alert["priority"])
    return alerts[:limit]


def build_home_dashboard(
    db: Session,
    group_id: int,
    now: datetime | None = None,
) -> dict:
    """Monta os dados operacionais da home para um único grupo."""
    now = now or datetime.now(timezone.utc)
    priority = get_priority_execution(db, group_id, now)
    return {
        "priority": (
            {
                "execution": priority,
                "name": _execution_name(priority),
                "totals": get_execution_totals(db, priority.id),
            }
            if priority
            else None
        ),
        "metrics": get_home_metrics(db, group_id, now),
        "alerts": get_home_alerts(db, group_id, now),
        "recent_history": get_recent_history(db, group_id),
    }
