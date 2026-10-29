"""Bypass Tupã para usuários locais, habilitado somente por APP_ENV=test/AUTH_MOCK."""
from contextlib import closing
import hashlib
import hmac
import os
import secrets
import sqlite3
import time
import tempfile
from pathlib import Path

from jose import JWTError, jwt
from sqlalchemy import func, select

from app.config import get_settings
from app.testing_environment import PROJECT_ROOT

ISSUER = 'jaci-test'


def _runtime():
    settings = get_settings()
    if not settings.auth_mock or settings.app_env != 'test':
        raise ValueError('AUTH_MOCK não autorizado.')
    fingerprint = hashlib.sha256(
        f'{PROJECT_ROOT}\0{settings.database_url}'.encode()
    ).hexdigest()
    root = Path(tempfile.gettempdir()) / f'jaci-auth-mock-{os.getuid()}'
    directory = root / fingerprint
    for path in (root, directory):
        path.mkdir(mode=0o700, exist_ok=True)
        if path.is_symlink() or path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
            raise ValueError('Cache de sessão mock deve ser privado ao usuário do processo.')
    return directory


def _secret():
    directory = _runtime()
    target = directory / 'auth-secret'
    # Publicar o arquivo completo de modo atômico também no primeiro login concorrente.
    if not target.exists():
        with tempfile.NamedTemporaryFile(mode='w', dir=directory, delete=False) as output:
            temporary = Path(output.name)
            output.write(secrets.token_urlsafe(48))
        try:
            try:
                os.link(temporary, target)
            except FileExistsError:
                pass
        finally:
            temporary.unlink()
    if target.is_symlink() or target.stat().st_mode & 0o077:
        raise ValueError('Segredo de sessão mock deve ser privado.')
    return target.read_text()


def _sessions():
    path = _runtime() / 'auth-sessions.sqlite3'
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    os.close(fd)
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY, sub TEXT NOT NULL, email TEXT NOT NULL,
        jti TEXT NOT NULL, refresh_hash TEXT NOT NULL, refresh_until INTEGER NOT NULL,
        revoked INTEGER NOT NULL DEFAULT 0)''')
    return db


def _user(*, email=None, user_id=None):
    from app.database import SessionLocal
    from app.models.user import User
    with SessionLocal() as db:
        query = select(User.id, User.email).where(User.is_active.is_(True))
        if email is not None:
            query = query.where(func.lower(User.email) == email.strip().lower())
        else:
            try:
                user_id = int(user_id)
            except (ValueError, TypeError):
                return None
            query = query.where(User.id == user_id)
        return db.execute(query).first()


def _error():
    from app.services.tupa_auth_service import TupaError
    return TupaError('Credenciais de teste inválidas ou sessão revogada.', 401)


def _hash(value):
    return hashlib.sha256(value.encode()).hexdigest()


def _tokens(sid, sub, email):
    now = int(time.time())
    jti = secrets.token_urlsafe(24)
    refresh_token = sid + '.' + secrets.token_urlsafe(32)
    access = jwt.encode({'iss': ISSUER, 'aud': ISSUER, 'sub': sub, 'email': email,
                         'sid': sid, 'jti': jti, 'iat': now, 'exp': now + 900},
                        _secret(), algorithm='HS256')
    return jti, _hash(refresh_token), {
        'access_token': access, 'refresh_token': refresh_token,
        'expires_in': 900, 'token_type': 'bearer',
    }


def token(email, password):
    _runtime()  # Validar o modo antes de consultar a base configurada.
    user = _user(email=email)
    if user is None:
        raise _error()
    sid = secrets.token_urlsafe(24)
    jti, refresh_hash, tokens = _tokens(sid, str(user.id), user.email)
    with closing(_sessions()) as db, db:
        db.execute('INSERT INTO sessions VALUES (?,?,?,?,?,?,0)',
                   (sid, str(user.id), user.email, jti, refresh_hash, int(time.time())+86400))
    return tokens


def _decode(access, *, verify_exp=True):
    return jwt.decode(access, _secret(), algorithms=['HS256'], issuer=ISSUER,
                      audience=ISSUER, options={'verify_exp': verify_exp,
                      'require_exp': True, 'require_iat': True, 'require_sub': True})


def decode_access_token(access):
    try:
        payload = _decode(access)
        with closing(_sessions()) as db:
            row = db.execute('SELECT * FROM sessions WHERE id=?',
                             (payload.get('sid'),)).fetchone()
        user = _user(user_id=payload['sub'])
        if (row is None or row['revoked'] or row['sub'] != payload['sub']
                or row['email'] != payload.get('email') or row['jti'] != payload.get('jti')
                or user is None or user.email != row['email']):
            return None
        return payload
    except (JWTError, KeyError, TypeError, ValueError):
        return None


def refresh(refresh_token):
    sid = refresh_token.split('.', 1)[0]
    with closing(_sessions()) as db, db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT * FROM sessions WHERE id=?', (sid,)).fetchone()
        if (row is None or row['revoked'] or row['refresh_until'] <= time.time()
                or not hmac.compare_digest(row['refresh_hash'], _hash(refresh_token))
                or _user(user_id=row['sub']) is None):
            raise _error()
        jti, digest, tokens = _tokens(sid, row['sub'], row['email'])
        db.execute('UPDATE sessions SET jti=?, refresh_hash=? WHERE id=?', (jti,digest,sid))
    return tokens


def logout(access):
    try:
        payload = _decode(access, verify_exp=False)
    except (JWTError, ValueError, TypeError):
        raise _error()
    with closing(_sessions()) as db, db:
        db.execute('UPDATE sessions SET revoked=1 WHERE id=? AND sub=?',
                   (payload.get('sid'), payload['sub']))
