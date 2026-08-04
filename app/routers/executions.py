from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.websocket.manager import manager
from app.utils.datetime import now_local, parse_local_date
from app.database import get_db
from app.dependencies import get_current_user, get_active_group
from app.models.user import User
from app.models.group import Group
from app.models.execution import Execution, ExecutionItem
from app.models.enums import ExecutionStatus
from app.services.template_service import (
    get_template_by_id,
    get_templates_by_group,
)
from app.services.execution_service import (
    get_executions_for_group,
    get_execution_by_id,
    get_execution_items_grouped,
    get_execution_totals,
    get_execution_display_name,
    create_execution_from_template,
    create_execution_standalone,
    update_scheduled_execution,
    start_execution,
    complete_item as complete_item_service,
    incomplete_item as incomplete_item_service,
    add_item_to_execution,
    remove_item_from_execution,
    update_execution_item,
    get_pending_items,
    finalize_execution,
    cancel_execution,
    create_execution_from_pending,
    check_budget_alerts,
)
from app.services.template_learning_service import (
    analyze_template_history,
    apply_template_suggestions,
    dismiss_template_suggestions,
    get_template_suggestions,
)

router = APIRouter(prefix="/executions", tags=["Executions"])


# ─── Helper ───

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


def _to_float(value, default=None):
    if value in (None, ""):
        return default
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default


def _to_int(value, default=None):
    if value in (None, ""):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _read_template_learning_choices(form) -> dict[str, list[dict]]:
    selected_ids = set(form.getlist("template_learning_selected"))
    present_ids = form.getlist("template_learning_present")
    result = {"apply": [], "dismiss": []}

    for suggestion_id in present_ids:
        parts = suggestion_id.split(":")
        if len(parts) < 2:
            continue
        suggestion_type = parts[0]
        entity_id = _to_int(parts[1])
        if not suggestion_type or not entity_id:
            continue

        accepted = suggestion_id in selected_ids
        target = result["apply"] if accepted else result["dismiss"]
        if suggestion_type == "new_item":
            target.append(
                {
                    "suggestion_id": suggestion_id,
                    "type": "new_item",
                    "execution_item_id": entity_id,
                    "category_id": _to_int(form.get(f"category_id_{suggestion_id}")),
                    "planned_quantity": _to_float(
                        form.get(f"planned_quantity_{suggestion_id}"),
                        1,
                    ),
                }
            )
        elif suggestion_type == "quantity":
            target.append(
                {
                    "suggestion_id": suggestion_id,
                    "type": "quantity",
                    "template_item_id": entity_id,
                    "suggested_quantity": _to_float(
                        form.get(f"suggested_quantity_{suggestion_id}"),
                    ),
                }
            )
        elif suggestion_type == "notes":
            target.append(
                {
                    "suggestion_id": suggestion_id,
                    "type": "notes",
                    "template_item_id": entity_id,
                    "suggested_notes": form.get(f"suggested_notes_{suggestion_id}"),
                }
            )
        elif suggestion_type == "budget":
            target.append(
                {
                    "suggestion_id": suggestion_id,
                    "type": "budget",
                    "template_id": entity_id,
                    "suggested_budget": _to_float(
                        form.get(f"suggested_budget_{suggestion_id}"),
                    ),
                }
            )

    return result


# ─── Pages ───


@router.get("", include_in_schema=False)
async def list_executions(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
    status: str | None = Query(None),
):
    """List all executions for the active group."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    if not active_group:
        return templates.TemplateResponse(
            request,
            "pages/executions/index.html",
            {
                "request": request,
                "user": user,
                "active_group": None,
                "executions": [],
                "error": "Selecione um grupo ativo para ver as compras.",
                "status_labels": STATUS_LABELS,
                "status_badge_class": STATUS_BADGE_CLASS,
                "current_status": status,
                "active_page": "executions",
            },
        )

    status_filter = None
    if status:
        try:
            status_filter = ExecutionStatus(status)
        except ValueError:
            pass

    executions = get_executions_for_group(db, active_group.id, status=status_filter)

    # Attach totals to each execution
    executions_with_data = []
    for exec_item in executions:
        totals = get_execution_totals(db, exec_item.id)
        executions_with_data.append(
            {
                "execution": exec_item,
                "totals": totals,
            }
        )

    return templates.TemplateResponse(
        request,
        "pages/executions/index.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "executions": executions_with_data,
            "status_labels": STATUS_LABELS,
            "status_badge_class": STATUS_BADGE_CLASS,
            "current_status": status,
            "active_page": "executions",
        },
    )


@router.get("/new", include_in_schema=False)
async def create_execution_page(
    request: Request,
    template_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
):
    """Create execution form page (from template or standalone)."""
    from app.main import templates

    if not user or not active_group:
        return RedirectResponse(url="/auth/login", status_code=303)

    template = None
    templates_list = get_templates_by_group(db, active_group.id)

    if template_id:
        template = get_template_by_id(db, template_id, user)

    today_str = now_local().strftime("%Y-%m-%d")
    tomorrow_str = (now_local() + timedelta(days=1)).strftime("%Y-%m-%d")

    return templates.TemplateResponse(
        request,
        "pages/executions/create.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "template": template,
            "templates": templates_list,
            "today": today_str,
            "tomorrow": tomorrow_str,
            "active_page": "executions",
        },
    )


@router.get("/{execution_id}", include_in_schema=False)
async def execution_detail(
    request: Request,
    execution_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
):
    """View or execute a purchase."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return RedirectResponse(url="/executions", status_code=303)

    # Redirect based on status
    if execution.status == ExecutionStatus.completed:
        return await _completed_page(request, execution_id, db, user, active_group)

    if execution.status == ExecutionStatus.cancelled:
        return RedirectResponse(url="/executions", status_code=303)

    # In progress or scheduled
    grouped_items = get_execution_items_grouped(db, execution_id)
    totals = get_execution_totals(db, execution_id)

    # Budget alerts
    alerts = []
    if execution.budget and execution.budget > 0:
        alerts = check_budget_alerts(totals["total_spent"], execution.budget)

    jwt_token = request.cookies.get("jaci_session")
    messages = []
    if request.query_params.get("updated") == "1":
        messages.append(("success", "Compra atualizada e sincronizada."))

    return templates.TemplateResponse(
        request,
        "pages/executions/in_progress.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "jwt_token": jwt_token,
            "execution": execution,
            "execution_name": get_execution_display_name(execution),
            "grouped_items": grouped_items,
            "totals": totals,
            "budget_alerts": alerts,
            "messages": messages,
            "status_labels": STATUS_LABELS,
            "status_badge_class": STATUS_BADGE_CLASS,
            "active_page": "executions",
            "expanded_ids": [],
        },
    )


async def _completed_page(
    request: Request,
    execution_id: int,
    db: Session,
    user: User,
    active_group,
):
    """Completed execution summary page."""
    from app.main import templates

    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return RedirectResponse(url="/executions", status_code=303)

    grouped_items = get_execution_items_grouped(db, execution_id)
    totals = get_execution_totals(db, execution_id)

    return templates.TemplateResponse(
        request,
        "pages/executions/completed.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "execution": execution,
            "execution_name": get_execution_display_name(execution),
            "grouped_items": grouped_items,
            "totals": totals,
            "status_labels": STATUS_LABELS,
            "status_badge_class": STATUS_BADGE_CLASS,
            "active_page": "executions",
        },
    )


@router.get("/{execution_id}/items-fragment", include_in_schema=False)
async def execution_items_fragment(
    request: Request,
    execution_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
):
    """
    Retorna apenas o fragmento HTML da lista de itens.
    Usado pelo HTMX para atualização parcial.
    """
    from app.main import templates

    if not user:
        return Response(status_code=401)

    # execution = get_execution_by_id(db, execution_id, user)
    # if not execution:
    #     return Response(status_code=404)

    # grouped_items = get_execution_items_grouped(db, execution_id)
    # totals = get_execution_totals(db, execution_id)

    # # Budget alerts
    # alerts = []
    # if execution.budget and execution.budget > 0:
    #     alerts = check_budget_alerts(totals["total_spent"], execution.budget)

    # collapse_state = request.headers.get("X-Collapse-State", "")
    # expanded_ids = set(collapse_state.split(",") if collapse_state else [])

    # return templates.TemplateResponse(
    #     "pages/executions/_items_fragment.html",
    #     {
    #         "request": request,
    #         "user": user,
    #         "active_group": active_group,
    #         "execution": execution,
    #         "grouped_items": grouped_items,
    #         "totals": totals,
    #         "budget_alerts": alerts,
    #         "status_labels": STATUS_LABELS,
    #         "status_badge_class": STATUS_BADGE_CLASS,
    #         "jwt_token": jwt_token,
    #         "active_page": "executions",
    #         "expanded_ids": expanded_ids,
    #     },
    # )
    return await _get_items_fragment(request, execution_id, db, user, active_group) 


@router.get("/{execution_id}/items/{item_id}/complete-form", include_in_schema=False)
async def complete_item_form(
    request: Request,
    execution_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Retorna o HTML do modal para completar item (HTMX)."""
    from app.main import templates

    if not user:
        return Response(status_code=401)

    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return Response(status_code=404)

    item = db.scalar(
        select(ExecutionItem).where(
            ExecutionItem.id == item_id,
            ExecutionItem.execution_id == execution_id,
        )
    )
    if not item:
        return Response(status_code=404)

    return templates.TemplateResponse(
        request,
        "pages/executions/_complete_modal.html",
        {
            "request": request,
            "execution": execution,
            "item": item,
        },
    )


@router.get("/{execution_id}/items/{item_id}/edit-form", include_in_schema=False)
async def edit_item_form(
    request: Request,
    execution_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
):
    """Retorna o HTML do modal para editar item (HTMX)."""
    from app.main import templates

    if not user:
        return Response(status_code=401)

    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return Response(status_code=404)

    item = db.scalar(
        select(ExecutionItem).where(
            ExecutionItem.id == item_id,
            ExecutionItem.execution_id == execution_id,
        )
    )
    if not item:
        return Response(status_code=404)

    return templates.TemplateResponse(
        request,
        "pages/executions/_edit_modal.html",
        {
            "request": request,
            "execution": execution,
            "item": item,
            "active_group": active_group
        },
    )


@router.get("/{execution_id}/sidebar-fragment", include_in_schema=False)
async def execution_sidebar_fragment(
    request: Request,
    execution_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
):
    """Retorna o fragmento HTML do sidebar (resumo + local)."""
    from app.main import templates
 
    if not user:
        return Response(status_code=401)
 
    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return Response(status_code=404)
 
    totals = get_execution_totals(db, execution_id)
 
    return templates.TemplateResponse(
        request,
        "pages/executions/_sidebar_fragment.html",
        {
            "request": request,
            "execution": execution,
            "totals": totals,
            "active_group": active_group,
        },
    )


@router.get("/{execution_id}/close", include_in_schema=False)
async def close_execution_page(
    request: Request,
    execution_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
):
    """Close execution page — shows pending items if any."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return RedirectResponse(url="/executions", status_code=303)

    pending = get_pending_items(db, execution_id)
    totals = get_execution_totals(db, execution_id)

    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    learning_suggestions = get_template_suggestions(db, execution)
    history_suggestions = (
        analyze_template_history(db, execution.template, execution)
        if execution.template and not execution.is_standalone
        else None
    )

    return templates.TemplateResponse(
        request,
        "pages/executions/close_pending.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "execution": execution,
            "pending_items": pending,
            "totals": totals,
            "tomorrow": tomorrow_str,
            "learning_suggestions": learning_suggestions,
            "history_suggestions": history_suggestions,
            "active_page": "executions",
        },
    )


# ─── Actions ───


@router.post("/new")
async def handle_create_execution(
    request: Request,
    template_id: int | None = Form(None),
    scheduled_date: str = Form(...),
    budget: float | None = Form(None),
    is_standalone: bool = Form(False),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
):
    """Create a new execution."""
    from app.main import templates

    if not user or not active_group:
        return RedirectResponse(url="/auth/login", status_code=303)

    # Parse date
    try:
        date = parse_local_date(scheduled_date)
    except ValueError:
        today_str = now_local().strftime("%Y-%m-%d")
        tomorrow_str = (now_local() + timedelta(days=1)).strftime("%Y-%m-%d")
        return templates.TemplateResponse(
            request,
            "pages/executions/create.html",
            {
                "request": request,
                "user": user,
                "active_group": active_group,
                "template": None,
                "templates": get_templates_by_group(db, active_group.id),
                "today": today_str,
                "tomorrow": tomorrow_str,
                "error": "Data inválida. Use o formato DD/MM/AAAA.",
            },
            status_code=400,
        )

    if template_id > 0:
        # Create from template
        template = get_template_by_id(db, template_id, user)
        if not template:
            return RedirectResponse(url="/executions/new", status_code=303)

        execution = create_execution_from_template(
            db, template, date, user, budget, is_standalone
        )
    else:
        # Create standalone (no template)
        execution = create_execution_standalone(db, active_group, date, user, budget)

    return RedirectResponse(url=f"/executions/{execution.id}", status_code=303)


@router.post("/{execution_id}/start")
async def handle_start_execution(
    execution_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Start a purchase (status -> in_progress)."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return RedirectResponse(url="/executions", status_code=303)

    start_execution(db, execution)

    template_name = get_execution_display_name(execution)
    from app.services.notification_service import notify_execution_started

    notify_execution_started(db, execution, user, template_name)

    await manager.broadcast(
        execution_id,
        "execution_status_changed",
        {
            "new_status": "in_progress",
            "user_email": user.email,
        },
    )

    return RedirectResponse(url=f"/executions/{execution_id}", status_code=303)


@router.post("/{execution_id}/edit")
async def handle_update_execution(
    execution_id: int,
    name: str = Form(...),
    scheduled_date: str = Form(...),
    budget: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Edita dados próprios de uma execução agendada."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return RedirectResponse(url="/executions", status_code=303)

    try:
        parsed_date = parse_local_date(scheduled_date)
    except ValueError:
        return RedirectResponse(url=f"/executions/{execution_id}", status_code=303)

    parsed_budget = None
    if budget not in (None, ""):
        try:
            parsed_budget = float(str(budget).replace(",", "."))
        except ValueError:
            return RedirectResponse(url=f"/executions/{execution_id}", status_code=303)

    try:
        update_scheduled_execution(db, execution, name, parsed_date, parsed_budget)
    except ValueError:
        return RedirectResponse(url=f"/executions/{execution_id}", status_code=303)

    execution_name = get_execution_display_name(execution)
    from app.services.notification_service import notify_execution_updated

    notify_execution_updated(db, execution, user, execution_name)

    await manager.broadcast(
        execution_id,
        "execution_updated",
        {
            "execution_id": execution.id,
            "name": execution_name,
            "scheduled_date": execution.scheduled_date.date().isoformat(),
            "budget": execution.budget,
            "user_email": user.email,
        },
    )

    return RedirectResponse(url=f"/executions/{execution_id}?updated=1", status_code=303)


@router.post("/{execution_id}/items/{item_id}/complete")
async def handle_complete_item(
    request: Request,
    execution_id: int,
    item_id: int,
    purchased_quantity: float = Form(..., gt=0, multiple_of=0.001),
    unit_price: float = Form(...),
    location: str | None = Form(None),
    notes: str | None = Form(None),
    version: int = Form(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
):
    """Mark an item as purchased."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return RedirectResponse(url="/executions", status_code=303)

    # Find the item
    item = db.scalar(
        select(ExecutionItem).where(
            ExecutionItem.id == item_id,
            ExecutionItem.execution_id == execution_id,
        )
    )
    if not item:
        return RedirectResponse(url=f"/executions/{execution_id}", status_code=303)

    # Optimistic lock check
    if item.version != version:
        # Conflito detectado
        await manager.broadcast(
            execution_id,
            "version_conflict",
            {
                "item_id": item_id,
                "message": f"Item '{item.name}' foi alterado por outro usuário.",
            },
        )
        return await _get_items_fragment(request, execution_id, db, user, active_group)

    # Update item
    complete_item_service(db, item, purchased_quantity, unit_price, location, notes)

    # Broadcast para outros usuários
    await manager.broadcast(
        execution_id,
        "item_completed",
        {
            "item_id": item_id,
            "item_name": item.name,
            "user_email": user.email,
            "total_price": item.total_price,
        },
    )

    if execution.budget and execution.budget > 0:
        totals = get_execution_totals(db, execution_id)
        alerts = check_budget_alerts(totals["total_spent"], execution.budget)
        if alerts:
            await manager.broadcast(execution_id, "budget_alert", {"alerts": alerts})

    return await _get_items_fragment(request, execution_id, db, user, active_group)


@router.post("/{execution_id}/items/{item_id}/incomplete")
async def handle_incomplete_item(
    request: Request,
    execution_id: int,
    item_id: int,
    version: int = Form(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
):
    """Mark an item as not purchased."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return RedirectResponse(url="/executions", status_code=303)

    # Find the item
    item = db.scalar(
        select(ExecutionItem).where(
            ExecutionItem.id == item_id,
            ExecutionItem.execution_id == execution_id,
        )
    )
    if not item:
        return RedirectResponse(url=f"/executions/{execution_id}", status_code=303)

    # Optimistic lock check
    if item.version != version:
        # Conflito detectado
        await manager.broadcast(
            execution_id,
            "version_conflict",
            {
                "item_id": item_id,
                "message": f"Item '{item.name}' foi alterado por outro usuário.",
            },
        )
        return await _get_items_fragment(request, execution_id, db, user, active_group)

    # Update item
    incomplete_item_service(db, item)

    # Broadcast para outros usuários
    await manager.broadcast(
        execution_id,
        "item_completed",
        {
            "item_id": item_id,
            "item_name": item.name,
            "user_email": user.email,
            "total_price": item.total_price,
        },
    )

    # Verifica alertas de orçamento
    if execution.budget and execution.budget > 0:
        totals = get_execution_totals(db, execution_id)
        alerts = check_budget_alerts(totals["total_spent"], execution.budget)
        if alerts:
            await manager.broadcast(
                execution_id,
                "budget_alert",
                {"alerts": alerts},
            )

    return await _get_items_fragment(request, execution_id, db, user, active_group)


@router.post("/{execution_id}/items/add")
async def handle_add_item(
    request: Request,
    execution_id: int,
    name: str = Form(...),
    planned_quantity: float = Form(1, gt=0, multiple_of=0.001),
    unit_price: float | None = Form(None, gt=0),
    category_id: int | None = Form(None),
    notes: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
):
    """Add an item during execution."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return RedirectResponse(url="/executions", status_code=303)

    if not name.strip():
        if request.headers.get("HX-Request", "").lower() == "true":
            from app.main import templates

            return templates.TemplateResponse(
                request,
                "components/item_add_feedback.html",
                {"message": "O nome do item é obrigatório."},
                headers={
                    "HX-Retarget": "#executionItemAddFeedback",
                    "HX-Reswap": "innerHTML",
                    "X-Jaci-Item-Add-Error": "true",
                },
            )
        return RedirectResponse(url=f"/executions/{execution_id}", status_code=303)

    try:
        item = add_item_to_execution(
            db,
            execution,
            name,
            planned_quantity,
            category_id if category_id and category_id > 0 else None,
            notes,
            unit_price,
        )
    except ValueError as error:
        if request.headers.get("HX-Request", "").lower() == "true":
            from app.main import templates

            return templates.TemplateResponse(
                request,
                "components/item_add_feedback.html",
                {"message": str(error)},
                headers={
                    "HX-Retarget": "#executionItemAddFeedback",
                    "HX-Reswap": "innerHTML",
                    "X-Jaci-Item-Add-Error": "true",
                },
            )
        return RedirectResponse(url=f"/executions/{execution_id}", status_code=303)

    # Broadcast
    await manager.broadcast(
        execution_id,
        "item_added",
        {
            "item_id": item.id,
            "item_name": item.name,
            "user_email": user.email,
            "is_completed": item.is_completed,
            "total_price": item.total_price,
        },
    )

    if item.is_completed and execution.budget and execution.budget > 0:
        totals = get_execution_totals(db, execution_id)
        alerts = check_budget_alerts(totals["total_spent"], execution.budget)
        if alerts:
            await manager.broadcast(execution_id, "budget_alert", {"alerts": alerts})

    return await _get_items_fragment(request, execution_id, db, user, active_group)


@router.post("/{execution_id}/items/{item_id}/remove")
async def handle_remove_item(
    request: Request,
    execution_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
):
    """Remove an item from execution (only if not completed)."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return RedirectResponse(url="/executions", status_code=303)

    item = db.scalar(
        select(ExecutionItem).where(
            ExecutionItem.id == item_id,
            ExecutionItem.execution_id == execution_id,
        )
    )
    if not item:
        return RedirectResponse(url=f"/executions/{execution_id}", status_code=303)

    try:
        remove_item_from_execution(db, item)
        await manager.broadcast(
            execution_id,
            "item_removed",
            {
                "item_id": item_id,
                "item_name": item.name,
                "user_email": user.email,
            },
        )
    except ValueError:
        pass

    return await _get_items_fragment(request, execution_id, db, user, active_group)


@router.post("/{execution_id}/items/{item_id}/edit")
async def handle_update_item(
    request: Request,
    execution_id: int,
    item_id: int,
    name: str = Form(...),
    planned_quantity: float = Form(1, gt=0, multiple_of=0.001),
    category_id: int | None = Form(None),
    notes: str | None = Form(None),
    version: int = Form(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
):
    """Update an item during execution."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return RedirectResponse(url="/executions", status_code=303)

    # Find the item
    item = db.scalar(
        select(ExecutionItem).where(
            ExecutionItem.id == item_id,
            ExecutionItem.execution_id == execution_id,
        )
    )
    if not item:
        return RedirectResponse(url=f"/executions/{execution_id}", status_code=303)

    # Optimistic lock check
    if item.version != version:
        # Conflito detectado
        await manager.broadcast(
            execution_id,
            "version_conflict",
            {
                "item_id": item_id,
                "message": f"Item '{item.name}' foi alterado por outro usuário.",
            },
        )
        return await _get_items_fragment(request, execution_id, db, user, active_group)

    item = update_execution_item(
        db, item, name, planned_quantity, category_id if category_id > 0 else None, notes
    )

    # Broadcast para outros usuários
    await manager.broadcast(
        execution_id,
        "item_updated",
        {
            "item_id": item_id,
            "item_name": item.name,
            "user_email": user.email
        },
    )

    if execution.budget and execution.budget > 0:
        totals = get_execution_totals(db, execution_id)
        alerts = check_budget_alerts(totals["total_spent"], execution.budget)
        if alerts:
            await manager.broadcast(execution_id, "budget_alert", {"alerts": alerts})

    return await _get_items_fragment(request, execution_id, db, user, active_group)


@router.post("/{execution_id}/close")
async def handle_close_execution(
    request: Request,
    execution_id: int,
    action: str = Form(...),
    new_date: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Finalize execution with action on pending items."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return RedirectResponse(url="/executions", status_code=303)

    pending = get_pending_items(db, execution_id)
    form = await request.form()
    template_suggestions = _read_template_learning_choices(form)
    if execution.template and template_suggestions["apply"]:
        apply_template_suggestions(db, execution.template, template_suggestions["apply"])
    if template_suggestions["dismiss"]:
        dismiss_template_suggestions(db, execution, template_suggestions["dismiss"])
    

    if action == "discard":
        # Discard pending items and finalize
        finalize_execution(db, execution, discard_pending=True)

    elif action == "new_execution" and pending:
        # Create new execution with pending items
        date = datetime.now(timezone.utc) + timedelta(days=1)
        if new_date:
            try:
                date = parse_local_date(new_date)
            except ValueError:
                pass

        create_execution_from_pending(db, execution, pending, date)
        finalize_execution(db, execution, discard_pending=False)

    from app.services.agenda_service import generate_next_execution

    generate_next_execution(db, execution, user)

    # Notificar membros
    totals = get_execution_totals(db, execution.id)
    template_name = get_execution_display_name(execution)
    from app.services.notification_service import notify_execution_completed

    notify_execution_completed(
        db, execution, user, template_name, totals["total_spent"]
    )
    
    await manager.broadcast(
        execution_id,
        "execution_status_changed",
        {
            "new_status": "completed",
            "user_email": user.email,
        },
    )

    return RedirectResponse(url=f"/executions/{execution_id}", status_code=303)


@router.post("/{execution_id}/cancel")
async def handle_cancel_execution(
    execution_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Cancel an execution."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    execution = get_execution_by_id(db, execution_id, user)
    if not execution:
        return RedirectResponse(url="/executions", status_code=303)

    try:
        cancel_execution(db, execution)
    except ValueError:
        pass  # Already completed, ignore
    
    await manager.broadcast(
        execution_id,
        "execution_status_changed",
        {
            "new_status": "cancelled",
            "user_email": user.email,
        },
    )

    return RedirectResponse(url="/executions", status_code=303)


async def _get_items_fragment(
    request: Request,
    execution_id: int,
    db: Session,
    user: User,
    active_group,
):
    """Retorna o fragmento HTML dos itens."""
    from app.main import templates
    execution = get_execution_by_id(db, execution_id, user)
    grouped_items = get_execution_items_grouped(db, execution_id)
    totals = get_execution_totals(db, execution_id)

    alerts = []
    if execution and execution.budget and execution.budget > 0:
        alerts = check_budget_alerts(totals["total_spent"], execution.budget)

    jwt_token = request.cookies.get("jaci_session")
    collapse_state = request.headers.get("X-Collapse-State", "")
    expanded_ids = set(collapse_state.split(",") if collapse_state else [])

    return templates.TemplateResponse(
        request,
        "pages/executions/_items_fragment.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "execution": execution,
            "grouped_items": grouped_items,
            "totals": totals,
            "budget_alerts": alerts,
            "status_labels": STATUS_LABELS,
            "status_badge_class": STATUS_BADGE_CLASS,
            "jwt_token": jwt_token,
            "active_page": "executions",
            "expanded_ids": expanded_ids,
            "include_sidebar_oob": True,
        },
    )
