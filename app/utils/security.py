from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt, JWTError, ExpiredSignatureError
import bcrypt
from fastapi import Response

from app.config import get_settings

settings = get_settings()

def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha."""
    truncated = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(truncated, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    truncated = plain_password[:72].encode('utf-8')
    hashed = hashed_password.encode('utf-8')
    return bcrypt.checkpw(truncated, hashed)


def create_access_token(user_id: int, email: str) -> str:
    """Cria JWT de sessão (1 hora)."""
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decodifica JWT de sessão. Retorna None se inválido/expirado."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "access":
            return None
        return payload
    except (JWTError, ExpiredSignatureError):
        return None


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


def set_auth_cookie(response: Response, user_id: int, email: str) -> None:
    """Define cookie httpOnly com JWT de sessão."""
    token = create_access_token(user_id, email)
    response.set_cookie(
        key="jaci_session",
        value=token,
        httponly=True,
        secure=settings.secure_coockie,        # True em produção com HTTPS
        samesite="lax",
        max_age=settings.jwt_expire_minutes * 60,
        path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    """Remove cookie de sessão."""
    response.delete_cookie(
        key="jaci_session",
        path="/",
        httponly=True,
        secure=False,
        samesite="lax",
    )