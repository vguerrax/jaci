from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_active_group
from app.models.user import User
from app.services.group_service import (
    create_group,
    get_user_groups,
    get_group_by_id,
    get_group_members,
    is_group_owner,
    update_group_settings,
    invite_member,
    remove_member,
)
from app.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/groups", tags=["Grupos"])


# ─── Páginas ───

@router.get("", include_in_schema=False)
async def list_groups(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Lista todos os grupos do usuário."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    groups = get_user_groups(db, user)

    return templates.TemplateResponse(
        request,
        "pages/groups/list.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "groups": groups,
            "active_page": "groups",
        },
    )


@router.get("/new", include_in_schema=False)
async def create_group_page(
    request: Request,
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Formulário de criação de grupo."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    return templates.TemplateResponse(
        request,
        "pages/groups/create.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "active_page": "groups",
        },
    )


@router.get("/{group_id}", include_in_schema=False)
async def group_detail(
    request: Request,
    group_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Detalhes do grupo: membros, opções de gestão."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    group = get_group_by_id(db, group_id, user)
    if not group:
        return RedirectResponse(url="/groups", status_code=303)

    members = get_group_members(db, group_id)
    owner = is_group_owner(db, group_id, user)

    return templates.TemplateResponse(
        request,
        "pages/groups/detail.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "group": group,
            "members": members,
            "is_owner": owner,
            "active_page": "groups",
        },
    )


# ─── Ações ───

@router.post("/new")
async def handle_create_group(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Cria um novo grupo."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    if not name.strip():
        return templates.TemplateResponse(
            request,
            "pages/groups/create.html",
            {
                "request": request,
                "user": user,
                "active_group": active_group,
                "error": "O nome do grupo é obrigatório.",
            },
            status_code=400,
        )

    group = create_group(db, name, user)
    return RedirectResponse(url=f"/groups/{group.id}", status_code=303)


@router.post("/{group_id}/edit")
async def handle_edit_group(
    request: Request,
    group_id: int,
    name: str = Form(...),
    template_learning_enabled: bool = Form(False),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Altera configurações do grupo."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    group = get_group_by_id(db, group_id, user)
    if not group:
        return RedirectResponse(url="/groups", status_code=303)

    result = update_group_settings(
        db,
        group,
        name,
        user,
        template_learning_enabled=template_learning_enabled,
    )
    members = get_group_members(db, group_id)

    return templates.TemplateResponse(
        request,
        "pages/groups/detail.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "group": group,
            "members": members,
            "is_owner": is_group_owner(db, group_id, user),
            "active_page": "groups",
            "message": result["message"] if result["success"] else None,
            "error": result["message"] if not result["success"] else None,
        },
        status_code=200 if result["success"] else 400,
    )


@router.post("/{group_id}/invite")
async def handle_invite(
    request: Request,
    group_id: int,
    email: str = Form(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Convida um novo membro para o grupo."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    group = get_group_by_id(db, group_id, user)
    if not group:
        return RedirectResponse(url="/groups", status_code=303)

    result = await invite_member(db, group, email, user)

    members = get_group_members(db, group_id)
    owner = is_group_owner(db, group_id, user)
    
    return templates.TemplateResponse(
        request,
        "pages/groups/detail.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "group": group,
            "members": members,
            "is_owner": owner,
            "active_page": "groups",
            "message": result["message"] if result["success"] else None,
            "error": result["message"] if not result["success"] else None,
        },
    )


@router.post("/{group_id}/remove/{member_id}")
async def handle_remove_member(
    request: Request,
    group_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Remove um membro do grupo."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    result = remove_member(db, group_id, member_id, user)

    if not result["success"]:
        group = get_group_by_id(db, group_id, user)
        members = get_group_members(db, group_id)
        owner = is_group_owner(db, group_id, user)

        return templates.TemplateResponse(
            request,
            "pages/groups/detail.html",
            {
                "request": request,
                "user": user,
                "active_group": active_group,
                "group": group,
                "members": members,
                "is_owner": owner,
                "active_page": "groups",
                "error": result["message"],
            },
        )

    if member_id == user.id:
        return RedirectResponse(url="/groups", status_code=303)

    return RedirectResponse(url=f"/groups/{group_id}", status_code=303)


@router.post("/{group_id}/switch")
async def handle_switch_group(
    request: Request,
    group_id: int,
    return_to: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Switch active group."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    group = get_group_by_id(db, group_id, user)
    if not group:
        return RedirectResponse(url="/groups", status_code=303)

    redirect_url = (
        return_to
        if return_to and return_to.startswith("/") and not return_to.startswith("//")
        else f"/groups/{group_id}"
    )

    # A página intermediária garante que o navegador persista o cookie antes de navegar.
    response = templates.TemplateResponse(
        request,
        "pages/switch_group.html",
        {
            "request": request,
            "user": user,
            "group_id": group_id,
            "redirect_url": redirect_url,
        },
    )
    response.set_cookie(
        key="jaci_active_group",
        value=str(group_id),
        httponly=True,
        secure=settings.secure_cookie,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 30,
    )
    return response
