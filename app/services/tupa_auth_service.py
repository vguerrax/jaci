from functools import lru_cache
from typing import Any

import httpx
from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


class TupaError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def _url(path: str) -> str:
    return f"{settings.tupa_url.rstrip('/')}{path}"


def _service_headers() -> dict[str, str]:
    if not settings.tupa_service_token:
        return {}
    return {"x-service-token": settings.tupa_service_token}


async def _request(method: str, path: str, **kwargs) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=settings.tupa_timeout_seconds) as client:
            response = await client.request(method, _url(path), **kwargs)
    except httpx.HTTPError as exc:
        raise TupaError("O serviço de autenticação está indisponível.") from exc

    if response.is_error:
        message = "Não foi possível concluir a autenticação."
        try:
            detail = response.json().get("detail")
            if isinstance(detail, str):
                message = detail
        except (ValueError, AttributeError):
            pass
        raise TupaError(message, response.status_code)

    return response.json()


def _credentials(email: str, password: str) -> dict[str, str]:
    if not settings.tupa_product_id:
        raise TupaError("TUPA_PRODUCT_ID não está configurado.", 500)
    return {
        "product_id": settings.tupa_product_id,
        "email": email.lower().strip(),
        "password": password,
    }


async def create_user(email: str, password: str) -> str:
    data = await _request(
        "POST",
        "/auth/users",
        headers=_service_headers(),
        json=_credentials(email, password),
    )
    return data["user_id"]


async def migrate_user(email: str, password_hash: str) -> str:
    if not settings.tupa_product_id:
        raise TupaError("TUPA_PRODUCT_ID não está configurado.", 500)
    data = await _request(
        "POST",
        "/auth/migrate",
        headers=_service_headers(),
        json={
            "product_id": settings.tupa_product_id,
            "email": email.lower().strip(),
            "password_hash": password_hash,
        },
    )
    return data["user_id"]


async def token(email: str, password: str) -> dict[str, Any]:
    return await _request("POST", "/auth/token", json=_credentials(email, password))


async def refresh(refresh_token: str) -> dict[str, Any]:
    return await _request(
        "POST", "/auth/refresh", json={"refresh_token": refresh_token}
    )


async def logout(access_token: str) -> None:
    await _request(
        "POST",
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )


@lru_cache(maxsize=1)
def _jwks() -> dict[str, Any]:
    try:
        with httpx.Client(timeout=settings.tupa_timeout_seconds) as client:
            response = client.get(_url("/.well-known/jwks"))
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise TupaError("Não foi possível validar a sessão.") from exc


def decode_access_token(access_token: str) -> dict[str, Any] | None:
    try:
        header = jwt.get_unverified_header(access_token)
        keys = _jwks().get("keys", [])
        key = next(
            (candidate for candidate in keys if candidate.get("kid") == header.get("kid")),
            keys[0] if len(keys) == 1 else None,
        )
        if not key:
            _jwks.cache_clear()
            return None
        algorithm = key.get("alg")
        if not algorithm or header.get("alg") != algorithm:
            return None
        return jwt.decode(
            access_token,
            key,
            algorithms=[algorithm],
            options={"verify_aud": False},
        )
    except (JWTError, KeyError, TupaError):
        return None
