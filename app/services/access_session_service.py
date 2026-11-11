"""Sessão por dispositivo: relógio servidor, par protegido e refresh sob lock."""
import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import and_, delete, or_, update

from app.config import get_settings
from app.models.access_session import AccessSession
from app.models.user import User
from app.repositories.access_session_repository import lock_session, reference_hash
from app.services.session_policy import AccessTokenExpired, SessionExpired, SessionUnavailable, as_utc, deadline, is_active, utc_now
from app.services.session_provider import provider_for


@dataclass(frozen=True)
class SessionGrant:
    session_id: str
    user_id: int
    subject: str
    product_id: str
    provider: str
    expires_at: datetime
    csrf_token: str
    owner: str


def _key():
    settings = get_settings()
    key = settings.session_token_encryption_key
    if not key and settings.auth_mock and settings.app_env == 'test':
        # Modo exploratório não requer editar ambiente. Reusar segredo privado e
        # estável do provedor mock, com separação de domínio, entre workers.
        from app.services.test_auth_service import _secret
        key = base64.urlsafe_b64encode(hashlib.sha256(('jaci:session-envelope:' + _secret()).encode()).digest())
    try:
        if not key:
            raise ValueError()
        Fernet(key)
        return key.encode() if isinstance(key,str) else key
    except (ValueError, TypeError):
        raise SessionUnavailable('Preparar chave privada de sessão antes de ativar o guard.') from None


def _cipher():
    return Fernet(_key())


def _tokens(value):
    if (not isinstance(value, dict) or type(value.get('expires_in')) is not int
            or not 0 < value['expires_in'] <= 86400
            or not isinstance(value.get('token_type','bearer'),str)
            or value.get('token_type', 'bearer').lower() != 'bearer'
            or any(not isinstance(value.get(key), str) or not 0 < len(value[key]) <= 32768
                   for key in ('access_token', 'refresh_token'))):
        raise SessionExpired('invalid_provider_tokens')
    return {key:value[key] for key in ('access_token','refresh_token','expires_in')}


def _grant(row, reference):
    csrf = hmac.new(_key(), ('jaci:session-csrf:' + reference).encode(), hashlib.sha256).hexdigest()
    identity = json.dumps([row.provider, row.product_id, row.user_id, row.subject])
    owner = hmac.new(_key(), f'jaci:offline-owner:{identity}'.encode(), hashlib.sha256).hexdigest()
    return SessionGrant(reference,row.user_id,row.subject,row.product_id,row.provider,
                        as_utc(row.expires_at),csrf,owner)


def _identity(claims, subject, product, provider):
    if not isinstance(claims,dict) or str(claims.get('sub','')) != subject:
        raise SessionExpired('invalid_identity')
    if provider == 'tupa' and (claims.get('product_id') != product or claims.get('type') != 'access'):
        raise SessionExpired('invalid_identity')
    if provider == 'mock' and claims.get('iss') != 'jaci-test':
        raise SessionExpired('invalid_identity')


def _access_deadline(tokens, issued_at, claims):
    deadline_from_ttl = issued_at + timedelta(seconds=tokens['expires_in'])
    exp = claims.get('exp')
    if type(exp) is int:
        return min(deadline_from_ttl, datetime.fromtimestamp(exp, tz=timezone.utc))
    return deadline_from_ttl


def issue_session(db, user, tokens, *, now=None):
    settings = get_settings()
    provider = provider_for(settings)
    if not user.is_active:
        raise SessionExpired('inactive_user')
    value = _tokens(tokens)
    subject = str(user.id) if provider.name == 'mock' else str(user.tupa_user_id or '')
    product = 'jaci-test' if provider.name == 'mock' else settings.tupa_product_id
    checked = as_utc(now or utc_now())
    claims = provider.validate(value)
    _identity(claims,subject,product,provider.name)
    reference = secrets.token_urlsafe(32)
    row = AccessSession(id_hash=reference_hash(reference),user_id=user.id,subject=subject,
                        product_id=product,provider=provider.name,authenticated_at=checked,
                        last_activity_at=checked,expires_at=deadline(checked),
                        access_expires_at=_access_deadline(value, checked, claims),
                        encrypted_tokens=_cipher().encrypt(json.dumps(value).encode()).decode(),version=1)
    db.add(row)
    db.flush()
    grant = _grant(row,reference)
    db.commit()
    return grant


def _invalidate(db, row, now, reason):
    if row.revoked_at is None:
        row.revoked_at = now
        row.reason = reason
        row.encrypted_tokens = ''
        row.version += 1
        db.commit()
    else:
        db.rollback()


def load_session(db, reference, *, touch=True, allow_refresh=True, now=None):
    row = lock_session(db,reference)
    checked = as_utc(now or utc_now())
    if row is None:
        db.rollback()
        raise SessionExpired()
    try:
        if (not is_active(row.last_activity_at,row.revoked_at,checked)
                or as_utc(row.authenticated_at)>as_utc(row.last_activity_at)
                or as_utc(row.expires_at)!=deadline(row.last_activity_at)):
            raise SessionExpired()
        provider = provider_for(get_settings())
        user = db.get(User,row.user_id)
        if provider.name != row.provider or user is None or not user.is_active:
            raise SessionExpired('invalid_identity')
        subject = str(user.id) if row.provider=='mock' else str(user.tupa_user_id or '')
        product = 'jaci-test' if row.provider=='mock' else get_settings().tupa_product_id
        if subject!=row.subject or product!=row.product_id:
            raise SessionExpired('invalid_identity')
        value = _tokens(json.loads(_cipher().decrypt(row.encrypted_tokens.encode()).decode()))
        refreshed = checked >= as_utc(row.access_expires_at)
        if refreshed:
            if not allow_refresh:
                raise SessionExpired('session_refresh_required')
            started=checked
            value=_tokens(provider.refresh(value['refresh_token']))
            row.encrypted_tokens=_cipher().encrypt(json.dumps(value).encode()).decode()
        try:
            claims = provider.validate(value)
        except AccessTokenExpired:
            if not allow_refresh:
                raise
            checked = as_utc(now or utc_now())
            if not is_active(row.last_activity_at, row.revoked_at, checked):
                raise SessionExpired()
            if refreshed:
                raise SessionUnavailable('O Tupã retornou um access já vencido.') from None
            started = checked
            value = _tokens(provider.refresh(value['refresh_token']))
            row.encrypted_tokens = _cipher().encrypt(json.dumps(value).encode()).decode()
            refreshed = True
            claims = provider.validate(value)
        _identity(claims,row.subject,row.product_id,row.provider)
        if refreshed:
            row.access_expires_at = _access_deadline(value, started, claims)
        checked=as_utc(now or utc_now())
        if (not is_active(row.last_activity_at,row.revoked_at,checked)
                or checked>=as_utc(row.access_expires_at)):
            raise SessionExpired()
        if touch:
            row.last_activity_at=checked
            row.expires_at=deadline(checked)
            row.version+=1
        grant=_grant(row,reference)
        db.commit()
        return grant
    except SessionExpired as exc:
        if exc.code=='session_refresh_required':
            db.rollback()  # WS pede navegação HTTP; não revogar por não renovar no canal.
        else:
            _invalidate(db,row,checked,exc.code)
        raise
    except SessionUnavailable:
        db.rollback()
        raise
    except (InvalidToken,ValueError,TypeError,KeyError,AttributeError):
        _invalidate(db,row,checked,'invalid_session_state')
        raise SessionExpired('invalid_session_state') from None
    except Exception:
        db.rollback()
        raise SessionUnavailable('Sessão temporariamente indisponível.') from None


def revoke_session(db, reference):
    row=lock_session(db,reference)
    if row is None:
        db.rollback()
        return
    remote=None
    try:
        remote=json.loads(_cipher().decrypt(row.encrypted_tokens.encode()).decode())['access_token']
    except (InvalidToken, ValueError, KeyError, SessionUnavailable):
        pass
    provider=provider_for(get_settings())
    _invalidate(db,row,utc_now(),'logout')
    if remote:
        try: provider.logout(remote)
        except Exception: pass  # Local já confirmado, sem reemitir cookie.


def revoke_user_sessions(db,user_id):
    db.execute(update(AccessSession).where(AccessSession.user_id==user_id,
                                          AccessSession.revoked_at.is_(None))
               .values(revoked_at=utc_now(),reason='credentials_changed',encrypted_tokens='',
                       version=AccessSession.version+1))
    db.commit()


def cookie_grant(db, reference):
    row=lock_session(db,reference)
    if row is None or not is_active(row.last_activity_at,row.revoked_at,utc_now()):
        db.rollback()
        return None
    grant=_grant(row,reference)
    db.commit()
    return grant


def prune_sessions(db, *, now=None):
    cutoff=as_utc(now or utc_now())-timedelta(days=30)
    result = db.execute(delete(AccessSession).where(or_(
        AccessSession.revoked_at < cutoff,
        and_(AccessSession.revoked_at.is_(None), AccessSession.expires_at < cutoff),
    )))
    db.commit()
    return result.rowcount
