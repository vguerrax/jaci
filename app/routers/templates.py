from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_active_group
from app.models.user import User
from app.models.enums import RecurrenceType
from app.services.template_service import (
    get_templates_by_group,
    get_template_by_id,
    get_template_items_grouped,
    create_template,
    update_template,
    toggle_template_active,
    can_delete_template,
    delete_template,
    count_active_executions,
    add_item_to_template,
    get_template_item_by_id,
    update_template_item,
    remove_template_item,
    get_categories_for_group,
)

router = APIRouter(prefix="/templates", tags=["Templates"])


# ─── Helpers ───

RECURRENCE_LABELS = {
    RecurrenceType.daily: "Diária",
    RecurrenceType.weekly: "Semanal",
    RecurrenceType.biweekly: "Quinzenal",
    RecurrenceType.monthly: "Mensal",
    RecurrenceType.yearly: "Anual",
}


def _get_template_context(
    request: Request,
    user: User,
    active_group,
    template=None,
    error=None,
    message=None,
):
    """Helper para contexto comum dos templates."""
    return {
        "request": request,
        "user": user,
        "active_group": active_group,
        "template": template,
        "error": error,
        "message": message,
        "recurrence_labels": RECURRENCE_LABELS,
        "recurrence_types": RecurrenceType,
        "active_page": "templates",
    }


def _is_htmx(request: Request) -> bool:
    """Return whether the request was issued by HTMX."""
    return request.headers.get("HX-Request", "").lower() == "true"


def _item_add_error_response(request: Request, target: str, message: str):
    """Render an accessible modal error without replacing the item list."""
    from app.main import templates

    return templates.TemplateResponse(
        request,
        "components/item_add_feedback.html",
        {"message": message},
        headers={
            "HX-Retarget": target,
            "HX-Reswap": "innerHTML",
            "X-Jaci-Item-Add-Error": "true",
        },
    )


def _get_template_items_fragment(request: Request, template, db: Session):
    """Render only template items after an HTMX mutation."""
    from app.main import templates

    return templates.TemplateResponse(
        request,
        "pages/templates/_items_fragment.html",
        {
            "request": request,
            "template": template,
            "grouped_items": get_template_items_grouped(db, template.id),
            "categories": get_categories_for_group(db, template.group_id),
        },
    )


# ─── Pages ───

@router.get("", include_in_schema=False)
async def list_templates(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
    show_inactive: bool = Query(False),
):
    """List all templates for the active group."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    if not active_group:
        return templates.TemplateResponse(
            request,
            "pages/templates/list.html",
            {
                "request": request,
                "user": user,
                "active_group": None,
                "templates": [],
                "active_page": "templates",
                "show_inactive": show_inactive,
                "error": "Você precisa ter um grupo ativo para gerenciar listas.",
            },
        )

    template_list = get_templates_by_group(
        db, active_group.id, include_inactive=show_inactive
    )

    # Attach execution counts
    templates_with_counts = []
    for tpl in template_list:
        active_counts = count_active_executions(db, tpl.id)
        templates_with_counts.append({
            "template": tpl,
            "active_executions": active_counts["total"],
            "item_count": len(tpl.items),
        })

    return templates.TemplateResponse(
        request,
        "pages/templates/list.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "templates": templates_with_counts,
            "active_page": "templates",
            "show_inactive": show_inactive,
            "recurrence_labels": RECURRENCE_LABELS,
        },
    )


@router.get("/new", include_in_schema=False)
async def create_template_page(
    request: Request,
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Create template form."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    if not active_group:
        return RedirectResponse(url="/templates", status_code=303)

    return templates.TemplateResponse(
        request,
        "pages/templates/create.html",
        _get_template_context(request, user, active_group),
    )


@router.get("/{template_id}", include_in_schema=False)
async def template_detail(
    request: Request,
    template_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """View template with items grouped by category."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    template = get_template_by_id(db, template_id, user)
    if not template:
        return RedirectResponse(url="/templates", status_code=303)
    
    grouped_items = get_template_items_grouped(db, template_id)
    categories = get_categories_for_group(db, template.group_id)
    execution_counts = count_active_executions(db, template_id)
    
    return templates.TemplateResponse(
        request,
        "pages/templates/detail.html",
        {
            **_get_template_context(request, user, active_group, template=template),
            "grouped_items": grouped_items,
            "categories": categories,
            "execution_counts": execution_counts,
        },
    )


@router.get("/{template_id}/edit", include_in_schema=False)
async def edit_template_page(
    request: Request,
    template_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Edit template form."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    template = get_template_by_id(db, template_id, user)
    if not template:
        return RedirectResponse(url="/templates", status_code=303)

    return templates.TemplateResponse(
        request,
        "pages/templates/edit.html",
        _get_template_context(request, user, active_group, template=template),
    )


# ─── Template Actions ───

@router.post("/new")
async def handle_create_template(
    request: Request,
    name: str = Form(...),
    recurrence: str = Form(...),
    budget: float | None = Form(None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Create a new template."""
    from app.main import templates

    if not user or not active_group:
        return RedirectResponse(url="/auth/login", status_code=303)

    if not name.strip():
        return templates.TemplateResponse(
            request,
            "pages/templates/create.html",
            {
                **_get_template_context(request, user, active_group),
                "error": "O nome do template é obrigatório.",
            },
            status_code=400,
        )

    try:
        rec_type = RecurrenceType(recurrence)
    except ValueError:
        return templates.TemplateResponse(
            request,
            "pages/templates/create.html",
            {
                **_get_template_context(request, user, active_group),
                "error": "Tipo de recorrência inválido.",
            },
            status_code=400,
        )

    new_template = create_template(db, active_group, name, rec_type, budget)
    return RedirectResponse(url=f"/templates/{new_template.id}", status_code=303)


@router.post("/{template_id}/edit")
async def handle_edit_template(
    request: Request,
    template_id: int,
    name: str = Form(...),
    recurrence: str = Form(...),
    budget: float | None = Form(None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Update a template."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    template = get_template_by_id(db, template_id, user)
    if not template:
        return RedirectResponse(url="/templates", status_code=303)

    if not name.strip():
        return templates.TemplateResponse(
            request,
            "pages/templates/edit.html",
            {
                **_get_template_context(request, user, active_group, template=template),
                "error": "O nome do template é obrigatório.",
            },
            status_code=400,
        )

    try:
        rec_type = RecurrenceType(recurrence)
    except ValueError:
        return templates.TemplateResponse(
            request,
            "pages/templates/edit.html",
            {
                **_get_template_context(request, user, active_group, template=template),
                "error": "Tipo de recorrência inválido.",
            },
            status_code=400,
        )

    update_template(db, template, name, rec_type, budget)
    return RedirectResponse(url=f"/templates/{template.id}", status_code=303)


@router.post("/{template_id}/toggle")
async def handle_toggle_template(
    request: Request,
    template_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Toggle template active/inactive."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    template = get_template_by_id(db, template_id, user)
    if not template:
        return RedirectResponse(url="/templates", status_code=303)

    toggle_template_active(db, template)
    return RedirectResponse(url=f"/templates/{template.id}", status_code=303)


@router.post("/{template_id}/delete")
async def handle_delete_template(
    request: Request,
    template_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Delete a template (only if no active executions)."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    template = get_template_by_id(db, template_id, user)
    if not template:
        return RedirectResponse(url="/templates", status_code=303)

    can_delete, message = can_delete_template(db, template)
    if not can_delete:
        grouped_items = get_template_items_grouped(db, template_id)
        categories = get_categories_for_group(db, template.group_id)
        execution_counts = count_active_executions(db, template_id)

        return templates.TemplateResponse(
            request,
            "pages/templates/detail.html",
            {
                **_get_template_context(
                    request, user, active_group,
                    template=template, error=message,
                ),
                "grouped_items": grouped_items,
                "categories": categories,
                "execution_counts": execution_counts,
            },
        )

    delete_template(db, template)
    return RedirectResponse(url="/templates", status_code=303)


# ─── Item Actions ───

@router.post("/{template_id}/items/add")
async def handle_add_item(
    request: Request,
    template_id: int,
    name: str = Form(...),
    planned_quantity: float = Form(1, gt=0, multiple_of=0.001),
    category_id: int | None = Form(None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Add an item to the template."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    template = get_template_by_id(db, template_id, user)
    if not template:
        return RedirectResponse(url="/templates", status_code=303)

    if not name.strip():
        if _is_htmx(request):
            return _item_add_error_response(
                request,
                "#templateItemAddFeedback",
                "O nome do item é obrigatório.",
            )
        grouped_items = get_template_items_grouped(db, template_id)
        categories = get_categories_for_group(db, template.group_id)

        return templates.TemplateResponse(
            request,
            "pages/templates/detail.html",
            {
                **_get_template_context(request, user, active_group, template=template,
                                      error="O nome do item é obrigatório."),
                "grouped_items": grouped_items,
                "categories": categories,
                "execution_counts": count_active_executions(db, template_id),
            },
            status_code=400,
        )

    try:
        add_item_to_template(
            db,
            template,
            name,
            planned_quantity,
            category_id if category_id and category_id > 0 else None,
        )
    except ValueError as error:
        if _is_htmx(request):
            return _item_add_error_response(
                request,
                "#templateItemAddFeedback",
                str(error),
            )
        grouped_items = get_template_items_grouped(db, template_id)
        categories = get_categories_for_group(db, template.group_id)
        return templates.TemplateResponse(
            request,
            "pages/templates/detail.html",
            {
                **_get_template_context(
                    request,
                    user,
                    active_group,
                    template=template,
                    error=str(error),
                ),
                "grouped_items": grouped_items,
                "categories": categories,
                "execution_counts": count_active_executions(db, template_id),
            },
            status_code=400,
        )

    if _is_htmx(request):
        return _get_template_items_fragment(request, template, db)
    return RedirectResponse(url=f"/templates/{template.id}", status_code=303)


@router.post("/{template_id}/items/{item_id}/edit")
async def handle_edit_item(
    request: Request,
    template_id: int,
    item_id: int,
    name: str = Form(...),
    planned_quantity: float = Form(1, gt=0, multiple_of=0.001),
    category_id: int | None = Form(None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Update a template item."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    item = get_template_item_by_id(db, item_id, user)
    if not item or item.template_id != template_id:
        return RedirectResponse(url="/templates", status_code=303)

    if not name.strip():
        return RedirectResponse(
            url=f"/templates/{template_id}?error=Nome+obrigatório",
            status_code=303,
        )

    try:
        update_template_item(
            db,
            item,
            name,
            planned_quantity,
            category_id if category_id and category_id > 0 else None,
        )
    except ValueError as exc:
        return templates.TemplateResponse(
            request,
            "pages/templates/detail.html",
            {
                **_get_template_context(
                    request,
                    user,
                    active_group,
                    template=item.template,
                    error=str(exc),
                ),
                "grouped_items": get_template_items_grouped(db, template_id),
                "categories": get_categories_for_group(db, item.template.group_id),
                "execution_counts": count_active_executions(db, template_id),
            },
            status_code=422,
        )
    return RedirectResponse(url=f"/templates/{template_id}", status_code=303)


@router.post("/{template_id}/items/{item_id}/remove")
async def handle_remove_item(
    request: Request,
    template_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Remove an item from the template."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    item = get_template_item_by_id(db, item_id, user)
    if not item or item.template_id != template_id:
        return RedirectResponse(url="/templates", status_code=303)

    remove_template_item(db, item)
    return RedirectResponse(url=f"/templates/{template_id}", status_code=303)
