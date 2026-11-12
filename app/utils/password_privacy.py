"""Cabeçalhos de recuperação e remoção de queries sensíveis dos logs."""
import logging
import re

from starlette.middleware.base import BaseHTTPMiddleware

SENSITIVE_PASSWORD_PATHS = frozenset({
    "/reset-password", "/auth/reset-password", "/auth/forgot-password",
    "/auth/profile/password",
})
SENSITIVE_QUERY = re.compile(
    r'((?:https?://[^\s/?#]+)?/(?:reset-password|auth/(?:reset-password|forgot-password|profile/password)))/?\?[^\s"\x27<>]*'
)


def _redact(value):
    if isinstance(value, str):
        return SENSITIVE_QUERY.sub(r"\1?[redacted]", value)
    if isinstance(value, tuple):
        return tuple(_redact(item) for item in value)
    if isinstance(value, dict):
        return {key: _redact(item) for key, item in value.items()}
    return value


class PasswordLogFilter(logging.Filter):
    def filter(self, record):
        record.msg = _redact(record.msg)
        record.args = _redact(record.args)
        return True


def install_password_log_filters():
    for name in ("uvicorn.access", "httpx", "httpcore", "jaci.auth", "jaci.password"):
        logger = logging.getLogger(name)
        if not any(isinstance(item, PasswordLogFilter) for item in logger.filters):
            logger.addFilter(PasswordLogFilter())


class PasswordPrivacyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path.rstrip("/") in SENSITIVE_PASSWORD_PATHS:
            response.headers["Cache-Control"] = "no-store"
            response.headers["Referrer-Policy"] = "no-referrer"
        return response
