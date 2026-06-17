from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_active_group
from app.models.user import User
from app.models.group import Group
from app.services.category_service import (
    get_categories_by_group,
    get_category_by_id,
    create_category,
    update_category,
    move_category,
    set_uncategorized_position,
    count_items_using_category,
    delete_category,
)

router = APIRouter(prefix="/categories", tags=["Categories"])


# ─── Pages ───

@router.get("", include_in_schema=False)
async def list_categories(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """List all categories for the active group."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    if not active_group:
        return templates.TemplateResponse(
            request,
            "pages/categories/list.html",
            {
                "request": request,
                "user": user,
                "active_group": None,
                "categories": [],
                "active_page": "categories",
                "error": "Você precisa ter um grupo ativo para gerenciar categorias.",
            },
        )

    categories = get_categories_by_group(db, active_group.id)

    # Attach item count to each category
    categories_with_counts = []
    for cat in categories:
        counts = count_items_using_category(db, cat.id)
        categories_with_counts.append({
            "category": cat,
            "item_count": counts["total"],
        })

    return templates.TemplateResponse(
        request,
        "pages/categories/list.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "categories": categories_with_counts,
            "active_page": "categories",
        },
    )


@router.get("/new", include_in_schema=False)
async def create_category_page(
    request: Request,
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Create category form."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    if not active_group:
        return RedirectResponse(url="/categories", status_code=303)

    return templates.TemplateResponse(
        request,
        "pages/categories/create.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "active_page": "categories",
        },
    )


@router.get("/{category_id}/edit", include_in_schema=False)
async def edit_category_page(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Edit category form."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    category = get_category_by_id(db, category_id, user)
    if not category:
        return RedirectResponse(url="/categories", status_code=303)

    return templates.TemplateResponse(
        request,
        "pages/categories/edit.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "category": category,
            "active_page": "categories",
        },
    )
    
    
@router.get("/{category_id}/delete", include_in_schema=False)
async def delete_category_confirm_page(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Delete confirmation page."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    category = get_category_by_id(db, category_id, user)
    if not category:
        return RedirectResponse(url="/categories", status_code=303)

    counts = count_items_using_category(db, category.id)

    return templates.TemplateResponse(
        request,
        "pages/categories/delete_confirm.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "category": category,
            "counts": counts,
            "active_page": "categories",
        },
    )


# ─── Actions ───

@router.post("/new")
async def handle_create_category(
    request: Request,
    name: str = Form(...),
    color: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Create a new category."""
    from app.main import templates

    if not user or not active_group:
        return RedirectResponse(url="/auth/login", status_code=303)

    if not name.strip():
        return templates.TemplateResponse(
            request,
            "pages/categories/create.html",
            {
                "request": request,
                "user": user,
                "active_group": active_group,
                "error": "O nome da categoria é obrigatório.",
            },
            status_code=400,
        )

    create_category(db, active_group, name, color if color else None)
    return RedirectResponse(url="/categories", status_code=303)


@router.post("/{category_id}/move")
async def handle_move_category(
    category_id: int,
    direction: str = Form(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
):
    """Move uma categoria na ordem de exibição."""
    if not user or not active_group:
        return RedirectResponse(url="/auth/login", status_code=303)

    category = get_category_by_id(db, category_id, user)
    if category and category.group_id == active_group.id:
        move_category(db, category, direction)

    return RedirectResponse(url="/categories", status_code=303)


@router.post("/order/uncategorized")
async def handle_uncategorized_position(
    position: str = Form(...),
    user: User | None = Depends(get_current_user),
    active_group: Group | None = Depends(get_active_group),
    db: Session = Depends(get_db),
):
    """Define a posição do grupo sem categoria."""
    if not user or not active_group:
        return RedirectResponse(url="/auth/login", status_code=303)

    set_uncategorized_position(db, active_group, position)
    return RedirectResponse(url="/categories", status_code=303)


@router.post("/{category_id}/edit")
async def handle_edit_category(
    request: Request,
    category_id: int,
    name: str = Form(...),
    color: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Update a category."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    category = get_category_by_id(db, category_id, user)
    if not category:
        return RedirectResponse(url="/categories", status_code=303)

    if not name.strip():
        return templates.TemplateResponse(
            request,
            "pages/categories/edit.html",
            {
                "request": request,
                "user": user,
                "active_group": active_group,
                "category": category,
                "error": "O nome da categoria é obrigatório.",
            },
            status_code=400,
        )

    update_category(db, category, name, color if color else None)
    return RedirectResponse(url="/categories", status_code=303)


@router.post("/{category_id}/delete")
async def handle_delete_category(
    request: Request,
    category_id: int,
    confirm: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Delete a category after confirmation."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    category = get_category_by_id(db, category_id, user)
    if not category:
        return RedirectResponse(url="/categories", status_code=303)

    counts = count_items_using_category(db, category.id)

    # If there are items and no confirmation, show confirmation page
    if counts["total"] > 0 and confirm != "yes":
        return templates.TemplateResponse(
            request,
            "pages/categories/delete_confirm.html",
            {
                "request": request,
                "user": user,
                "active_group": active_group,
                "category": category,
                "counts": counts,
                "active_page": "categories",
            },
        )

    delete_category(db, category)
    return RedirectResponse(url="/categories", status_code=303)
