from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Response

from app.config import get_settings
from app.services.tupa_auth_service import decode_access_token

settings = get_settings()

def create_magic_token(email: str) -> str:
    """Cria token para magic link (15 minutos)."""
    payload = {
        "sub": email,
        "type": "magic_link",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.magic_link_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_magic_token(token: str) -> str | None:
    """
    Decodifica magic token.
    Retorna o e-mail se válido, None caso contrário.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "magic_link":
            return None
        return payload.get("sub")
    except (JWTError, ExpiredSignatureError):
        return None


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    expires_in: int,
    token_type: str = "bearer",
) -> None:
    """Define os cookies httpOnly emitidos pelo Tupã."""
    response.set_cookie(
        key="jaci_session",
        value=access_token,
        httponly=True,
        secure=settings.secure_cookie,
        samesite="lax",
        max_age=expires_in,
        path="/",
    )
    response.set_cookie(
        key="jaci_refresh",
        value=refresh_token,
        httponly=True,
        secure=settings.secure_cookie,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    """Remove os cookies de autenticação."""
    for key in ("jaci_session", "jaci_refresh"):
        response.delete_cookie(
            key=key,
            path="/",
            httponly=True,
            secure=settings.secure_cookie,
            samesite="lax",
        )
