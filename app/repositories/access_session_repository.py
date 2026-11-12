"""Lock de sessão compartilhado entre workers, antes de tocar ou rotacionar."""
import hashlib
import re
from sqlalchemy import select, text
from app.models.access_session import AccessSession


def reference_hash(reference):
    if not isinstance(reference,str) or not re.fullmatch(r'[A-Za-z0-9_-]{43}', reference):
        return None
    return hashlib.sha256(reference.encode('ascii')).hexdigest()


def lock_session(db, reference):
    key=reference_hash(reference)
    if key is None: return None
    # SQLite não oferece FOR UPDATE; reservar escrita antes de ler na transação.
    if db.get_bind().dialect.name=='sqlite' and not db.in_transaction():
        db.execute(text('BEGIN IMMEDIATE'))
    return db.scalar(select(AccessSession).where(AccessSession.id_hash==key)
                     .with_for_update().execution_options(populate_existing=True))
