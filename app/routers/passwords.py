import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_active_group, get_current_user
from app.models import User
from app.services import access_session_service as sessions, password_service as passwords
from app.templating import templates

router = APIRouter(tags=["Recuperação de senha"])
logger = logging.getLogger("jaci.password")
COOKIE_CHUNK_SIZE = 3500


def _secure_cookie():
    settings = get_settings()
    return settings.secure_cookie or settings.app_env == "production"


def _context(request):
    return "".join(request.cookies.get(name, "") for name in passwords.RESET_COOKIE_NAMES)


def _set_context(response, value=""):
    for index, name in enumerate(passwords.RESET_COOKIE_NAMES):
        chunk = value[index*COOKIE_CHUNK_SIZE:(index+1)*COOKIE_CHUNK_SIZE]
        if chunk:
            response.set_cookie(
                name, chunk, httponly=True, secure=_secure_cookie(), samesite="lax",
                path=passwords.RESET_COOKIE_PATH, max_age=passwords.RESET_CONTEXT_SECONDS,
            )
        else:
            response.delete_cookie(name, path=passwords.RESET_COOKIE_PATH, secure=_secure_cookie(),
                                   httponly=True, samesite="lax")


def _page(request, name, status_code=200, **context):
    return templates.TemplateResponse(request, "pages/"+name, {
        "request": request, "user": None, "password_mock": get_settings().auth_mock, **context,
    }, status_code=status_code)


@router.get("/auth/forgot-password", include_in_schema=False)
async def forgot_page(request: Request):
    return _page(request, "forgot_password.html")


@router.post("/auth/forgot-password", include_in_schema=False)
async def forgot_password(
    request: Request, email: str = Form(""), db: Session = Depends(get_db),
):
    try:
        origin = request.client.host if request.client else "unknown"
        await passwords.request_recovery(db, email, origin)
    except passwords.PasswordFlowError as exc:
        response = _page(request, "forgot_password.html", exc.status_code,
                         error=str(exc), form_email=email)
        if exc.status_code == 429:
            response.headers["Retry-After"] = str(get_settings().password_recovery_window_seconds)
        return response
    return _page(request, "forgot_password.html", confirmation=passwords.RECOVERY_CONFIRMATION)


@router.get("/reset-password", include_in_schema=False)
async def reset_link(request: Request):
    response = RedirectResponse("/auth/reset-password", status_code=303)
    try:
        context = passwords.seal_reset_token(request.query_params.get("token", ""))
    except passwords.PasswordFlowError:
        context = ""
    _set_context(response, context)
    return response


@router.get("/auth/reset-password", include_in_schema=False)
async def reset_page(request: Request):
    if get_settings().auth_mock:
        return _page(request, "reset_password.html", 501,
                     error="Operação indisponível na autenticação simulada.")
    valid = passwords.open_reset_token(_context(request)) is not None
    response = _page(request, "reset_password.html", 200 if valid else 400,
                     context_valid=valid, error=None if valid else "Link inválido ou expirado.")
    if not valid:
        _set_context(response)
    return response


def _password_success(request):
    request.state.session_terminal = True
    response = RedirectResponse("/auth/login?password_changed=1", status_code=303)
    _set_context(response)
    return response


@router.post("/auth/reset-password", include_in_schema=False)
async def reset_password(
    request: Request, new_password: str = Form(""),
    new_password_confirm: str = Form(""), db: Session = Depends(get_db),
):
    context = _context(request)
    try:
        await passwords.reset_password(context, new_password, new_password_confirm)
    except passwords.PasswordFlowError as exc:
        invalid = isinstance(exc, passwords.InvalidResetLink)
        response = _page(request, "reset_password.html", exc.status_code,
                         error=str(exc), context_valid=not invalid and bool(context))
        if invalid:
            _set_context(response)
        return response
    grant = getattr(request.state, "auth_session", None)
    if grant:
        try:
            sessions.revoke_session(db, grant.session_id, propagate=False, reason="password_reset")
        except SQLAlchemyError:
            try:
                db.rollback()
            except SQLAlchemyError:
                pass
            logger.warning("password.local_session_cleanup_pending")
    return _password_success(request)


@router.post("/auth/profile/password", include_in_schema=False)
async def change_password(
    request: Request, current_password: str = Form(""), new_password: str = Form(""),
    new_password_confirm: str = Form(""), db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user), active_group=Depends(get_active_group),
):
    if not user:
        return RedirectResponse("/auth/login", status_code=303)
    grant = getattr(request.state, "auth_session", None)
    reference = grant.session_id if grant else request.cookies.get("jaci_session")
    try:
        await passwords.change_password(
            db, user, reference, current_password, new_password, new_password_confirm,
        )
    except passwords.PasswordFlowError as exc:
        return _page(request, "profile.html", exc.status_code,
                     user=user, active_group=active_group, active_page="profile", password_error=str(exc))
    return _password_success(request)
