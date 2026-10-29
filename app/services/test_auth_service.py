"""Autenticação sintética. Só é acessível após as guardas de APP_ENV/AUTH_MOCK."""
from contextlib import closing
import hashlib
import hmac
import os
import secrets
import sqlite3
import time

from jose import JWTError, jwt

from app.config import get_settings
from app.testing_environment import validate_database

ISSUER = 'jaci-test'
PASSWORD = 'jaci-test-only'
ACCOUNTS = {'owner@example.com', 'member@example.com', 'outsider@example.com'}


def _runtime():
    settings = get_settings()
    if not settings.auth_mock or settings.app_env != 'test':
        raise ValueError('AUTH_MOCK não autorizado.')
    return validate_database(settings.database_url).parent


def _secret():
    return (_runtime() / 'auth-secret').read_text()


def _sessions():
    path = _runtime() / 'auth-sessions.sqlite3'
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    os.close(fd)
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY, sub TEXT NOT NULL, email TEXT NOT NULL,
        jti TEXT NOT NULL, refresh_hash TEXT NOT NULL, refresh_until INTEGER NOT NULL,
        revoked INTEGER NOT NULL DEFAULT 0)''')
    return db


def _user(email):
    with closing(sqlite3.connect(_runtime() / 'jaci.sqlite3')) as db:
        return db.execute('SELECT tupa_user_id FROM users WHERE email=? AND is_active=1',
                          (email,)).fetchone()


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
    email = email.strip().lower()
    if email not in ACCOUNTS or not hmac.compare_digest(password, PASSWORD):
        raise _error()
    user = _user(email)
    if user is None:
        raise _error()
    sid = secrets.token_urlsafe(24)
    jti, refresh_hash, tokens = _tokens(sid, user[0], email)
    with closing(_sessions()) as db, db:
        db.execute('INSERT INTO sessions VALUES (?,?,?,?,?,?,0)',
                   (sid, user[0], email, jti, refresh_hash, int(time.time())+86400))
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
        if (row is None or row['revoked'] or row['sub'] != payload['sub']
                or row['email'] != payload.get('email') or row['jti'] != payload.get('jti')
                or _user(row['email']) is None):
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
                or _user(row['email']) is None):
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
