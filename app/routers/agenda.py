from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_active_group
from app.models.user import User
from app.models.enums import ExecutionStatus
from app.utils.datetime import now_local
from app.services.agenda_service import (
    build_calendar_data,
    get_executions_for_date,
    get_list_executions,
    reschedule_execution,
    MONTH_NAMES_PT,
)
from app.services.execution_service import (
    get_execution_by_id,
    get_execution_totals,
)

router = APIRouter(prefix="/agenda", tags=["Agenda"])


# ─── Helpers ───

STATUS_INDICATOR_CLASS = {
    "scheduled": "indicator-scheduled",
    "in_progress": "indicator-in-progress",
    "completed": "indicator-completed",
    "cancelled": "indicator-cancelled",
}

STATUS_LABELS = {
    ExecutionStatus.scheduled: "Agendada",
    ExecutionStatus.in_progress: "Em andamento",
    ExecutionStatus.completed: "Finalizada",
    ExecutionStatus.cancelled: "Cancelada",
}

STATUS_BADGE_CLASS = {
    ExecutionStatus.scheduled: "badge-scheduled",
    ExecutionStatus.in_progress: "badge-in-progress",
    ExecutionStatus.completed: "badge-completed",
    ExecutionStatus.cancelled: "badge-cancelled",
}


# ─── Pages ───

@router.get("", include_in_schema=False)
async def agenda_calendar(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
    year: int | None = Query(None),
    month: int | None = Query(None),
):
    """Visualização da agenda em calendário mensal."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    if not active_group:
        return templates.TemplateResponse(
            "pages/executions/index.html",
            {
                "request": request,
                "user": user,
                "active_group": None,
                "error": "Selecione um grupo ativo para ver a agenda.",
            },
        )

    now = now_local()
    year = year or now.year
    month = month or now.month

    # Ajusta limites
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    calendar_data = build_calendar_data(db, active_group.id, year, month, now.date())

    # Navegação
    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1

    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    return templates.TemplateResponse(
        "pages/agenda/calendar.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "calendar": calendar_data,
            "prev_month": prev_month,
            "prev_year": prev_year,
            "next_month": next_month,
            "next_year": next_year,
            "today": now,
            "active_page": "agenda",
            "indicator_class": STATUS_INDICATOR_CLASS,
            "month_names": MONTH_NAMES_PT,
        },
    )


@router.get("/list", include_in_schema=False)
async def agenda_list(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
    status: str | None = Query(None),
    period: str | None = Query(None),
    date: str | None = Query(None),
):
    """Visualização da agenda em lista cronológica."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    if not active_group:
        return RedirectResponse(url="/", status_code=303)

    # Se uma data específica foi clicada no calendário
    selected_date = None
    if date:
        try:
            selected_date = datetime.strptime(date, "%Y-%m-%d")
            selected_date = selected_date.replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    if selected_date:
        executions = get_executions_for_date(db, active_group.id, selected_date)
    else:
        executions = get_list_executions(db, active_group.id, status, period)

    # Attach totals
    executions_with_data = []
    for exec_item in executions:
        totals = get_execution_totals(db, exec_item.id)
        template_name = exec_item.template.name if exec_item.template else None
        executions_with_data.append({
            "execution": exec_item,
            "totals": totals,
            "template_name": template_name,
        })

    # Agrupa por data
    grouped_by_date = {}
    for item in executions_with_data:
        date_key = item["execution"].scheduled_date.strftime("%Y-%m-%d")
        if date_key not in grouped_by_date:
            grouped_by_date[date_key] = {
                "date": item["execution"].scheduled_date,
                "executions": [],
            }
        grouped_by_date[date_key]["executions"].append(item)

    # Ordena por data decrescente
    grouped_list = sorted(
        grouped_by_date.values(),
        key=lambda x: x["date"],
        reverse=True,
    )

    return templates.TemplateResponse(
        "pages/agenda/list.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "grouped_executions": grouped_list,
            "selected_date": selected_date,
            "current_status": status,
            "current_period": period,
            "status_labels": STATUS_LABELS,
            "status_badge_class": STATUS_BADGE_CLASS,
            "active_page": "agenda",
        },
    )


@router.get("/day/{date}", include_in_schema=False)
async def agenda_day(
    request: Request,
    date: str,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Redireciona para a lista filtrada por uma data específica."""
    return RedirectResponse(
        url=f"/agenda/list?date={date}",
        status_code=303,
    )


# ─── Actions ───

@router.post("/{execution_id}/reschedule")
async def handle_reschedule(
    request: Request,
    execution_id: int,
    new_date: str = Form(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Adianta ou adia uma execução."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return RedirectResponse(url="/agenda", status_code=303)

    try:
        date = datetime.strptime(new_date, "%Y-%m-%d")
        date = date.replace(tzinfo=timezone.utc)
    except ValueError:
        return RedirectResponse(url="/agenda", status_code=303)

    try:
        reschedule_execution(db, execution, date)
    except ValueError:
        # Execução em andamento não pode ser reagendada
        pass

    # Redireciona de volta para a página anterior
    referer = request.headers.get("referer", "/agenda")
    return RedirectResponse(url=referer, status_code=303)