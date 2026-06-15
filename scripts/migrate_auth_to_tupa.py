"""Migra hashes de senha locais para o Tupã e associa os IDs retornados."""

import asyncio
import logging

from sqlalchemy import select

from app.database import SessionLocal, ensure_schema_compatibility
from app.models.user import User
from app.services.tupa_service import TupaError, migrate_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jaci.auth.migration")


async def main() -> None:
    ensure_schema_compatibility()
    db = SessionLocal()
    try:
        users = db.scalars(
            select(User).where(
                User.tupa_user_id.is_(None),
                User.password_hash.is_not(None),
            )
        ).all()
        for user in users:
            try:
                user.tupa_user_id = await migrate_user(user.email, user.password_hash)
                user.password_hash = None
                db.commit()
                logger.info("Migrado: %s", user.email)
            except TupaError as exc:
                db.rollback()
                logger.error("Falha ao migrar %s: %s", user.email, exc)
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
