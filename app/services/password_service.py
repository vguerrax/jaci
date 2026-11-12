"""Política de recuperação, contexto temporário e alteração pelo Tupã."""
import asyncio
import base64
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime

from cryptography.fernet import InvalidToken
from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.config import get_settings
from app.repositories import auth_rate_limit_repository as limits
from app.services import access_session_service as sessions, tupa_auth_service as tupa
from app.services.session_policy import SessionExpired, SessionUnavailable, utc_now
from app.services.session_provider import TupaSessionProvider

logger = logging.getLogger("jaci.password")
RESET_COOKIE_NAMES = tuple("jaci_password_reset_"+str(index) for index in range(4))
RESET_COOKIE_PATH = "/auth/reset-password"
RESET_CONTEXT_SECONDS = 3600
RECOVERY_CONFIRMATION = "Se o e-mail estiver cadastrado, você receberá as instruções para redefinir a senha."


class PasswordFlowError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class InvalidResetLink(PasswordFlowError):
    def __init__(self):
        super().__init__("Link inválido ou expirado.")


def validate_password(password: str, confirmation: str) -> None:
    if not 8 <= len(password) <= 128:
        raise PasswordFlowError("A nova senha deve ter entre 8 e 128 caracteres.")
    if len(password.encode("utf-8")) > 72:
        raise PasswordFlowError("A nova senha deve ter no máximo 72 bytes em UTF-8.")
    if password != confirmation:
        raise PasswordFlowError("As novas senhas não conferem.")


def normalize_email(value: str) -> str:
    try:
        if len(value) > 320:
            raise ValueError()
        return str(TypeAdapter(EmailStr).validate_python(value.strip().lower()))
    except (ValidationError, ValueError):
        raise PasswordFlowError("Informe um e-mail válido.") from None


def _available() -> None:
    if get_settings().auth_mock:
        raise PasswordFlowError("Operação indisponível na autenticação simulada.", 501)


def _limit_key(kind: str, value: str) -> str:
    identity = json.dumps([kind, get_settings().tupa_product_id, value])
    return hmac.new(sessions._key(), ("jaci:password-limit:"+identity).encode(), hashlib.sha256).hexdigest()


async def request_recovery(db: Session, email: str, origin: str) -> None:
    _available()
    email = normalize_email(email)
    settings = get_settings()
    started = time.monotonic()
    try:
        now = utc_now()
        limits.remove_expired(db, now)
        origin_attempts = limits.consume(
            db, _limit_key("origin", origin), now, settings.password_recovery_window_seconds,
        )
        if origin_attempts > settings.password_recovery_origin_limit:
            db.commit()
            raise PasswordFlowError("Muitas solicitações. Tente novamente mais tarde.", 429)
        email_attempts = limits.consume(
            db, _limit_key("email", email), now, settings.password_recovery_window_seconds,
        )
        db.commit()
        if email_attempts <= settings.password_recovery_email_limit:
            await tupa.forgot_password(email)
    except tupa.TupaError as exc:
        status = 501 if exc.status_code == 501 else 503
        raise PasswordFlowError("Não foi possível solicitar a recuperação. Tente novamente mais tarde.", status) from None
    except SQLAlchemyError:
        db.rollback()
        raise PasswordFlowError("Não foi possível solicitar a recuperação. Tente novamente mais tarde.", 503) from None
    finally:
        remaining = settings.password_recovery_min_response_seconds - (time.monotonic() - started)
        if remaining > 0:
            await asyncio.sleep(remaining)


def _valid_token(token) -> bool:
    return (
        isinstance(token, str) and bool(token) and len(token.encode("utf-8")) <= 4096
        and all(ord(char) >= 32 and ord(char) != 127 for char in token)
    )


def seal_reset_token(token: str, *, now: datetime | None = None) -> str:
    _available()
    if not _valid_token(token):
        raise InvalidResetLink()
    settings = get_settings()
    if not settings.tupa_product_id:
        raise SessionUnavailable("Configurar o produto antes da recuperação.")
    payload = json.dumps(
        {"purpose": "password-reset", "product_id": settings.tupa_product_id, "token": token},
        ensure_ascii=False,
    ).encode("utf-8")
    return sessions._cipher().encrypt_at_time(payload, int((now or utc_now()).timestamp())).decode()


def open_reset_token(value: str, *, now: datetime | None = None) -> str | None:
    if not value or len(value) > 14000:
        return None
    try:
        encoded = value.encode("ascii")
        raw = base64.b64decode(encoded, altchars=b"-_", validate=True)
        if base64.urlsafe_b64encode(raw) != encoded:
            return None
        payload = json.loads(sessions._cipher().decrypt_at_time(
            encoded, ttl=RESET_CONTEXT_SECONDS, current_time=int((now or utc_now()).timestamp()),
        ))
        if (payload.get("purpose") != "password-reset"
                or payload.get("product_id") != get_settings().tupa_product_id
                or not _valid_token(payload.get("token"))):
            return None
        return payload["token"]
    except (InvalidToken, ValueError, TypeError, UnicodeError, AttributeError):
        return None


async def reset_password(context: str, password: str, confirmation: str) -> None:
    _available()
    validate_password(password, confirmation)
    token = open_reset_token(context)
    if token is None:
        raise InvalidResetLink()
    try:
        await tupa.reset_password(token, password)
    except tupa.TupaError as exc:
        if exc.status_code == 400:
            raise InvalidResetLink() from None
        raise PasswordFlowError(
            "Não foi possível confirmar a alteração. Tente entrar com a nova senha antes de repetir.",
            503,
        ) from None


async def change_password(db: Session, user, reference: str | None, current: str,
                          password: str, confirmation: str) -> None:
    _available()
    validate_password(password, confirmation)
    if not current or len(current) > 128 or len(current.encode("utf-8")) > 72:
        raise PasswordFlowError("Informe sua senha atual.")
    if get_settings().session_guard_enabled:
        access = sessions.access_token_for_user(db, reference, user.id)
    else:
        access = reference
    if not access:
        raise SessionExpired()
    try:
        await tupa.change_password(access, current, password)
    except tupa.TupaError as exc:
        if exc.status_code == 401:
            await run_in_threadpool(TupaSessionProvider(get_settings()).validate, {"access_token": access})
            raise PasswordFlowError("A senha atual está incorreta.") from None
        raise PasswordFlowError(
            "Não foi possível confirmar a alteração. Tente entrar com a nova senha antes de repetir.",
            503,
        ) from None
    try:
        sessions.revoke_user_sessions(db, user.id)
    except SQLAlchemyError:
        try:
            db.rollback()
        except SQLAlchemyError:
            pass
        # O Tupã já confirmou a revogação global, conferida no próximo acesso.
        logger.warning("password.local_session_cleanup_pending")
