"""Política local de inatividade. Identidade e revogação pertencem ao provedor."""
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote, urlsplit, urlunsplit

IDLE_SECONDS = 28800


class SessionExpired(Exception):
    def __init__(self, code='session_expired'):
        self.code = code
        super().__init__('Autenticação necessária.')


class AccessTokenExpired(SessionExpired):
    def __init__(self):
        super().__init__('session_refresh_required')


class SessionUnavailable(Exception):
    """Falha temporária: não equivale a revogação nem renova atividade."""


def utc_now():
    return datetime.now(timezone.utc)


def as_utc(value):
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def deadline(last_activity):
    return as_utc(last_activity) + timedelta(seconds=IDLE_SECONDS)


def is_active(last_activity, revoked_at, now):
    return revoked_at is None and as_utc(last_activity) <= as_utc(now) < deadline(last_activity)


def internal_return_url(value):
    if not isinstance(value, str) or not value or len(value)>2048:
        return '/'
    decoded=value
    for _ in range(5):
        if any(ord(char)<32 or ord(char)==127 or char=='\\' for char in decoded):
            return '/'
        expanded=unquote(decoded)
        if expanded==decoded: break
        decoded=expanded
    else: return '/'
    if not decoded.startswith('/') or decoded.startswith('//') or decoded!=decoded.strip():
        return '/'
    try: parsed=urlsplit(decoded)
    except ValueError: return '/'
    if parsed.scheme or parsed.netloc: return '/'
    import re
    if not re.fullmatch(r'/(?:|agenda|sync|templates(?:/new|/\d+(?:/edit)?)?|executions(?:/new|/\d+(?:/edit)?)?|categories|groups(?:/\d+)?|auth/profile)', parsed.path):
        return '/'
    return urlunsplit(('', '', parsed.path, parsed.query, ''))
