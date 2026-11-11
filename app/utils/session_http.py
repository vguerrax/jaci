"""HTTP adapter for the opt-in persisted session; no heartbeat or timer."""
import hmac
import math
import secrets
from contextlib import contextmanager
from urllib.parse import urlencode, urlsplit

from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.services import access_session_service as sessions
from app.services.session_provider import TupaSessionProvider, provider_for
from app.services.session_policy import SessionExpired, SessionUnavailable, internal_return_url, utc_now


@contextmanager
def session_database():
    from app.database import SessionLocal
    with SessionLocal() as db:
        yield db


def guard_enabled():
    return getattr(get_settings(), 'session_guard_enabled', False)


def session_grant(request):
    return getattr(request.state,'issued_session',None) or getattr(request.state,'auth_session',None)


def csrf_value(request):
    grant=session_grant(request)
    if grant and request.url.path not in _ANONYMOUS_FORMS:
        return grant.csrf_token
    return getattr(request.state, 'login_csrf', '')


def offline_owner(request):
    grant=session_grant(request)
    return grant.owner if grant and request.url.path not in _ANONYMOUS_FORMS else ''


def same_origin(request):
    origin = request.headers.get('origin') or request.headers.get('referer')
    if not origin:
        return True  # O CSRF continua obrigatório em formulários sem Referer.
    try:
        source = urlsplit(origin)
        allowed = (urlsplit(str(request.base_url)), urlsplit(get_settings().app_url))
        return any(
            (source.scheme, source.netloc) == (expected.scheme, expected.netloc)
            for expected in allowed
        )
    except ValueError:
        return False


_ANONYMOUS_FORMS = {
    '/auth/login', '/auth/password-login', '/auth/register',
    '/auth/forgot-password', '/auth/reset-password', '/reset-password',
}


def require_login_provider():
    if guard_enabled():
        provider = provider_for()
        if isinstance(provider, TupaSessionProvider):
            provider.check_configuration()
        sessions._key()


def prepare_login(request, user, tokens, db):
    if guard_enabled():
        request.state.issued_session = sessions.issue_session(db, user, tokens)


def _secure_cookie():
    settings = get_settings()
    return settings.secure_cookie or settings.app_env == 'production'


def set_session_cookie(response, grant):
    ttl = math.ceil((grant.expires_at - utc_now()).total_seconds())
    response.set_cookie(
        'jaci_session', grant.session_id, httponly=True, secure=_secure_cookie(),
        samesite='lax', path='/', max_age=max(0, ttl),
    )


def _load(reference, touch=True):
    with session_database() as db:
        return sessions.load_session(db,reference,touch=touch)


def _current(reference):
    with session_database() as db:
        return sessions.cookie_grant(db,reference)


def _public(path):
    return (path.startswith('/static/') or path in {
        '/health','/manifest.webmanifest','/service-worker.js','/privacy','/terms',
        '/auth/login','/auth/register','/auth/password-login','/auth/login/error',
        '/auth/login/sent','/auth/magic-link','/auth/verify',
        '/auth/logout','/auth/forgot-password','/auth/reset-password','/reset-password',
    })


def failure_response(request, code, status=401):
    path = request.url.path
    query = request.url.query
    return_to = internal_return_url(f'{path}?{query}' if query else path)
    parameters = {'return_to': return_to}
    if code != 'authentication_required':
        parameters['expired'] = '1'
    target = '/auth/login?' + urlencode(parameters)
    if status == 503:
        response = JSONResponse({
            'detail': {'code': 'session_unavailable', 'message': 'Autenticação temporariamente indisponível.'},
        }, status_code=503)
    elif (
        'application/json' in request.headers.get('accept', '')
        or path.startswith('/api/')
        or request.headers.get('hx-request') == 'true'
        or request.method not in {'GET', 'HEAD'}
    ):
        response = JSONResponse({
            'detail': {
                'code': code,
                'message': 'Entre para continuar.' if code == 'authentication_required' else 'Entre novamente para continuar.',
            },
        }, status_code=status)
        response.headers['X-Session-Login'] = target
    else:
        response = RedirectResponse(target, status_code=303)
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Jaci-Session-Guard'] = '1'
    return response


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if not guard_enabled():
            return await call_next(request)
        request.state.auth_session=None
        if request.url.path in _ANONYMOUS_FORMS:
            request.state.login_csrf = request.cookies.get('jaci_login_csrf') or secrets.token_urlsafe(32)
        request.state.session_terminal=False
        reference=request.cookies.get('jaci_session')
        failed=None
        if reference:
            try:
                request.state.auth_session=await run_in_threadpool(_load,reference)
            except SessionExpired as exc:
                failed=exc.code
            except (SessionUnavailable,SQLAlchemyError):
                if not _public(request.url.path):
                    return failure_response(request,'session_unavailable',503)
        if not _public(request.url.path) and request.state.auth_session is None:
            reason = failed or (
                'session_expired' if request.cookies.get('jaci_offline_owner') else 'authentication_required'
            )
            return failure_response(request, reason)
        grant = request.state.auth_session
        supplied_owner = request.headers.get('x-jaci-offline-owner')
        needs_owner = request.url.path.startswith('/api/offline/')
        if grant and (needs_owner or supplied_owner) and supplied_owner != grant.owner:
            return JSONResponse(
                {'detail': {'code': 'offline_account_changed', 'message': 'Entre na conta das pendências.'}},
                status_code=403,
                headers={'Cache-Control': 'no-store', 'X-Jaci-Session-Guard': '1', 'X-Jaci-Account-Changed': '1'},
            )
        if request.method not in {'GET', 'HEAD', 'OPTIONS'}:
            provided=request.headers.get('x-csrf-token','')
            if request.headers.get('content-type','').split(';')[0] in {'application/x-www-form-urlencoded','multipart/form-data'}:
                await request.body()  # Cache para que a rota ainda receba o mesmo corpo.
                form=await request.form()
                provided=provided or str(form.get('_csrf',''))
                request.state.login_return=internal_return_url(form.get('return_to'))
            expected=csrf_value(request)
            if (not same_origin(request) or not expected or not provided
                    or not hmac.compare_digest(expected.encode(), provided.encode())):
                return JSONResponse({'detail':'Formulário expirado ou origem inválida.'},status_code=403,
                                    headers={'Cache-Control':'no-store','X-Jaci-Session-Guard':'1'})
        try:
            response=await call_next(request)
        except SessionExpired as exc:
            return failure_response(request,exc.code)
        except SessionUnavailable:
            return failure_response(request,'session_unavailable',503)
        response.headers['X-Jaci-Session-Guard']='1'
        grant=session_grant(request)
        current = None
        if not request.state.session_terminal and grant:
            try:
                current=await run_in_threadpool(_current,grant.session_id)
            except (SessionUnavailable, SQLAlchemyError):
                if getattr(request.state, 'issued_session', None):
                    return failure_response(request, 'session_unavailable', 503)
            response.headers['Cache-Control'] = 'no-store'
            if current:
                set_session_cookie(response, current)
                response.delete_cookie('jaci_refresh',path='/')
                if request.url.path == '/api/offline/snapshot' and response.status_code == 200:
                    response.headers['X-Jaci-CSRF'] = current.csrf_token
                if (request.url.path not in _ANONYMOUS_FORMS
                        and 'text/html' in response.headers.get('Content-Type', '')):
                    response.headers['X-Jaci-Offline-Owner'] = current.owner
        elif request.state.session_terminal:
            from app.utils.security import clear_auth_cookies
            clear_auth_cookies(response)
            response.delete_cookie('jaci_offline_owner', path='/', secure=_secure_cookie())
        if request.url.path in _ANONYMOUS_FORMS and not getattr(request.state, 'issued_session', None):
            response.set_cookie('jaci_login_csrf',request.state.login_csrf,httponly=True,
                                secure=_secure_cookie(),samesite='lax',path='/',max_age=3600)
            response.headers['Cache-Control']='no-store'
        if getattr(request.state,'issued_session',None):
            response.delete_cookie('jaci_login_csrf',path='/')
            if current:
                response.headers['X-Jaci-Offline-Owner'] = current.owner
                response.set_cookie(
                    'jaci_offline_owner', current.owner, max_age=30 * 86400,
                    path='/', secure=_secure_cookie(), samesite='lax',
                )
        return response
