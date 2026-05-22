import logging
from fastapi import APIRouter, Request, Response, Depends, Form, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user, get_active_group

from app.services.auth_service import (
    request_magic_link,
    verify_magic_token,
    authenticate_with_password,
    setup_profile,
)
from app.services.group_service import add_member_to_group

from app.utils.security import set_auth_cookie, clear_auth_cookie, decode_access_token

from app.models.user import User

logger = logging.getLogger("jaci.auth")
router = APIRouter(prefix="/auth", tags=["Autenticação"])


# ─── Páginas ───

@router.get("/login", include_in_schema=False)
async def login_page(request: Request):
    """Tela de solicitação de e-mail."""
    from app.main import templates
    
    from app.utils.security import create_magic_token
    # token = create_magic_token("vguerrax@gmail.com")
    token = create_magic_token("lopesmariaclara@outlook.com.br")

    return templates.TemplateResponse(
        "pages/login.html",
        {
            "request": request,
            "user": None,
            "active_page": "login",
            "resend_cooldown": False,
            "token": token
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


# ─── Ações ───

@router.post("/magic-link")
async def send_link(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    """Send magic link to email."""
    from app.services.auth_service import request_magic_link
    from app.main import templates
    
    result = await request_magic_link(db, email)

    if not result["success"]:
        return templates.TemplateResponse(
            "pages/login.html",
            {
                "request": request,
                "user": None,
                "error": result["message"],
                "resend_cooldown": False,
            },
            status_code=400,
        )

    # Use direct TemplateResponse instead of RedirectResponse
    response = templates.TemplateResponse(
        "pages/login_sent.html",
        {
            "request": request,
            "user": None,
            "email": email,
        },
    )
    return response


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

    user = authenticate_with_password(db, email, password)

    if not user:
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
        
    set_auth_cookie(response, user.id, user.email)

    if not user.is_profile_complete:
        return RedirectResponse(url="/auth/setup", status_code=303)

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
    set_auth_cookie(response, user.id, user.email)
    
    response.set_cookie(
        key="jaci_active_group",
        value=str(user.groups[0].id),
        httponly=True,
        secure=False,
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
):
    """
    Validate magic token and create session.
    Uses an intermediate page to ensure cookie is set properly.
    """
    from app.services.auth_service import verify_magic_token
    from app.services.group_service import add_member_to_group
    from app.main import templates

    user = verify_magic_token(db, token)

    if user is None:
        from app.utils.security import decode_magic_token
        email = decode_magic_token(token)
        reason = "expired" if email is None else "invalid"
        return RedirectResponse(
            url=f"/auth/login/error?reason={reason}",
            status_code=303,
        )

    # If group_id present, add user to group (invite flow)
    if group_id:
        add_member_to_group(db, group_id, user)

    # Render intermediate page that sets cookie and redirects
    redirect_url = "/auth/setup" if not user.is_profile_complete else "/"
    
    # Create the response with the template
    response = templates.TemplateResponse(
        "pages/auth_verify.html",
        {
            "request": request,
            "user": None,
            "redirect_url": redirect_url,
            "user_id": user.id,
            "email": user.email,
            "group_id": group_id,
        },
    )
    
    # Set cookies on the response
    set_auth_cookie(response, user.id, user.email)
    
    if group_id:
        response.set_cookie(
            key="jaci_active_group",
            value=str(group_id),
            httponly=True,
            secure=False,
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
    password: str = Form(...),
    password_confirm: str = Form(...),
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

    if len(password) < 6:
        return templates.TemplateResponse(
            "pages/setup_profile.html",
            {
                "request": request,
                "user": user,
                "error": "A senha deve ter pelo menos 6 caracteres.",
            },
            status_code=400,
        )

    if password != password_confirm:
        return templates.TemplateResponse(
            "pages/setup_profile.html",
            {
                "request": request,
                "user": user,
                "error": "As senhas não conferem.",
            },
            status_code=400,
        )

    setup_profile(db, user, name, password)
    set_auth_cookie(response, user.id, user.email)
    
    return RedirectResponse(url="/", status_code=303)


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
    clear_auth_cookie(response)
    # Also clear active group cookie
    response.delete_cookie(
        key="jaci_active_group",
        path="/",
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return response