import logging
from fastapi import APIRouter, Request, Response, Depends, Form, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user, get_active_group

from app.services.auth_service import (
    authenticate_with_password,
    register_with_password,
    setup_profile,
    update_profile,
)
from app.services.group_service import add_member_to_group

from app.utils.security import set_auth_cookies, clear_auth_cookies
from app.services.tupa_auth_service import TupaError, logout as tupa_logout

from app.models.user import User
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger("jaci.auth")
router = APIRouter(prefix="/auth", tags=["Autenticação"])


# ─── Páginas ───

@router.get("/login", include_in_schema=False)
async def login_page(request: Request):
    """Tela de login."""
    from app.main import templates

    return templates.TemplateResponse(
        "pages/login.html",
        {
            "request": request,
            "user": None,
            "active_page": "login",
        },
    )


@router.get("/register", include_in_schema=False)
async def register_page(request: Request):
    """Tela de cadastro."""
    from app.main import templates

    return templates.TemplateResponse(
        "pages/register.html",
        {
            "request": request,
            "user": None,
            "active_page": "register",
        },
    )


@router.get("/login/sent", include_in_schema=False)
async def login_sent_page(request: Request, email: str = Query(...)):
    """Confirmação de envio do magic link."""
    from app.main import templates

    return templates.TemplateResponse(
        "pages/login_sent.html",
        {
            "request": request,
            "user": None,
            "email": email,
        },
    )


@router.get("/login/error", include_in_schema=False)
async def login_error_page(request: Request, reason: str = Query("unknown")):
    """Tela de erro de autenticação."""
    from app.main import templates

    error_messages = {
        "expired": "O link expirou. Solicite um novo.",
        "used": "Este link já foi usado. Solicite um novo acesso.",
        "invalid": "Link inválido. Solicite um novo.",
        "unknown": "Ocorreu um erro. Tente novamente.",
    }

    return templates.TemplateResponse(
        "pages/login_error.html",
        {
            "request": request,
            "user": None,
            "message": error_messages.get(reason, error_messages["unknown"]),
        },
    )


@router.get("/setup", include_in_schema=False)
async def setup_profile_page(
    request: Request,
    user: User | None = Depends(get_current_user),
):
    """Tela de configuração de perfil (primeiro acesso)."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    if user.is_profile_complete:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        "pages/setup_profile.html",
        {
            "request": request,
            "user": user,
            "active_page": "setup",
        },
    )


@router.get("/profile", include_in_schema=False)
async def profile_page(
    request: Request,
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Tela de edição do perfil."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    return templates.TemplateResponse(
        "pages/profile.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "active_page": "profile",
        },
    )


# ─── Ações ───

@router.post("/magic-link")
async def send_link(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    """Magic link de login foi substituído pelo Tupã."""
    return RedirectResponse(url="/auth/login", status_code=303)


@router.post("/password-login")
async def password_login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Login com e-mail e senha."""
    from app.main import templates

    try:
        result = await authenticate_with_password(db, email, password)
    except TupaError as exc:
        if exc.status_code >= 500:
            return templates.TemplateResponse(
                "pages/login.html",
                {"request": request, "user": None, "error": str(exc)},
                status_code=502,
            )
        result = None

    if not result:
        return templates.TemplateResponse(
            "pages/login.html",
            {
                "request": request,
                "user": None,
                "error": "E-mail ou senha incorretos.",
                "show_password_option": True,
            },
            status_code=400,
        )
        
    user, tokens = result

    if not user.is_profile_complete:
        response = RedirectResponse(url="/auth/setup", status_code=303)
        set_auth_cookies(response, **tokens)
        return response

    response = templates.TemplateResponse(
        "pages/auth_verify.html",
        {
            "request": request,
            "user": None,
            "redirect_url": "/",
            "user_id": user.id,
            "email": user.email,
            "group_id": user.groups[0].id,
        },
    )
    
    # Set cookies on the response
    set_auth_cookies(response, **tokens)
    
    response.set_cookie(
        key="jaci_active_group",
        value=str(user.groups[0].id),
        httponly=True,
        secure=settings.secure_cookie,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 30,
    )
    
    return response


@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db),
):
    """Cria uma conta no Tupã e o perfil correspondente no Jaci."""
    from app.main import templates

    if len(password) < 8:
        error = "A senha deve ter pelo menos 8 caracteres."
    elif password != password_confirm:
        error = "As senhas não conferem."
    elif not name.strip():
        error = "O nome é obrigatório."
    else:
        error = None

    if error:
        return templates.TemplateResponse(
            "pages/register.html",
            {
                "request": request,
                "user": None,
                "register_error": error,
                "form_name": name,
                "form_email": email,
            },
            status_code=400,
        )

    try:
        user, tokens = await register_with_password(db, name, email, password)
    except TupaError as exc:
        return templates.TemplateResponse(
            "pages/register.html",
            {
                "request": request,
                "user": None,
                "register_error": str(exc),
                "form_name": name,
                "form_email": email,
            },
            status_code=exc.status_code if exc.status_code < 500 else 502,
        )

    response = RedirectResponse(url="/", status_code=303)
    set_auth_cookies(response, **tokens)
    response.set_cookie(
        key="jaci_active_group",
        value=str(user.groups[0].id),
        httponly=True,
        secure=settings.secure_cookie,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 30,
    )
    return response


@router.get("/verify")
async def verify_link(
    request: Request,
    token: str = Query(...),
    group_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """
    Validate magic token and create session.
    Uses an intermediate page to ensure cookie is set properly.
    """
    from app.utils.security import decode_magic_token

    invited_email = decode_magic_token(token)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    if not group_id or invited_email != user.email:
        return RedirectResponse(url="/auth/login/error?reason=invalid", status_code=303)

    add_member_to_group(db, group_id, user)
    response = RedirectResponse(url="/", status_code=303)
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


@router.post("/setup")
async def handle_setup_profile(
    request: Request,
    response: Response,
    name: str = Form(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Configura nome e senha do perfil."""
    from app.main import templates
    
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    if user.is_profile_complete:
        return RedirectResponse(url="/", status_code=303)

    # Validações
    if not name.strip():
        return templates.TemplateResponse(
            "pages/setup_profile.html",
            {
                "request": request,
                "user": user,
                "error": "O nome é obrigatório.",
            },
            status_code=400,
        )

    setup_profile(db, user, name)
    
    return RedirectResponse(url="/", status_code=303)


@router.post("/profile")
async def handle_update_profile(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Atualiza nome e e-mail do usuário."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    name = name.strip()
    context = {
        "request": request,
        "user": user,
        "active_group": active_group,
        "active_page": "profile",
        "profile_name": name,
    }

    if not name:
        return templates.TemplateResponse(
            "pages/profile.html",
            {**context, "profile_error": "O nome é obrigatório."},
            status_code=400,
        )

    if len(name) > 100:
        return templates.TemplateResponse(
            "pages/profile.html",
            {**context, "profile_error": "O nome deve ter no máximo 100 caracteres."},
            status_code=400,
        )

    update_profile(db, user, name, user.email)
    response = templates.TemplateResponse(
        "pages/profile.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "active_page": "profile",
            "profile_message": "Dados pessoais atualizados.",
        },
    )
    return response


@router.post("/profile/password")
async def handle_change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    new_password_confirm: str = Form(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Altera a senha do usuário."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    context = {
        "request": request,
        "user": user,
        "active_group": active_group,
        "active_page": "profile",
    }

    if len(new_password) < 6:
        return templates.TemplateResponse(
            "pages/profile.html",
            {**context, "password_error": "A nova senha deve ter pelo menos 6 caracteres."},
            status_code=400,
        )

    if new_password != new_password_confirm:
        return templates.TemplateResponse(
            "pages/profile.html",
            {**context, "password_error": "As novas senhas não conferem."},
            status_code=400,
        )

    return templates.TemplateResponse(
        "pages/profile.html",
        {**context, "password_error": "A alteração de senha deve ser feita no serviço de autenticação."},
        status_code=501,
    )


@router.get("/logout")
async def logout(request: Request):
    """Clear session and redirect to home."""
    from app.main import templates

    response = templates.TemplateResponse(
        "pages/logout.html",
        {
            "request": request,
            "user": None,
        },
    )
    access_token = request.cookies.get("jaci_session")
    if access_token:
        try:
            await tupa_logout(access_token)
        except TupaError:
            pass
    clear_auth_cookies(response)
    # Also clear active group cookie
    response.delete_cookie(
        key="jaci_active_group",
        path="/",
        httponly=True,
        secure=settings.secure_cookie,
        samesite="lax",
    )
    return response
