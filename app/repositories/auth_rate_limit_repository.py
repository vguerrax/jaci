from datetime import datetime, timedelta

from sqlalchemy import case, delete
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.models.auth_rate_limit import AuthRateLimit


def remove_expired(db: Session, now: datetime) -> None:
    db.execute(delete(AuthRateLimit).where(AuthRateLimit.expires_at <= now))


def consume(db: Session, key_hash: str, now: datetime, window_seconds: int) -> int:
    insert = postgres_insert if db.get_bind().dialect.name == "postgresql" else sqlite_insert
    expires_at = now + timedelta(seconds=window_seconds)
    expired = AuthRateLimit.expires_at <= now
    statement = insert(AuthRateLimit).values(key_hash=key_hash, attempts=1, expires_at=expires_at)
    statement = statement.on_conflict_do_update(
        index_elements=[AuthRateLimit.key_hash],
        set_={
            "attempts": case((expired, 1), else_=AuthRateLimit.attempts + 1),
            "expires_at": case((expired, expires_at), else_=AuthRateLimit.expires_at),
        },
    ).returning(AuthRateLimit.attempts)
    return db.execute(statement).scalar_one()
