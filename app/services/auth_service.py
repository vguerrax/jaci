from datetime import datetime, timezone
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.group import Group, group_members
from app.models.category import Category, DEFAULT_CATEGORIES
from app.services import tupa_auth_service

logger = logging.getLogger("jaci.auth")


def get_or_create_tupa_user(
    db: Session, tupa_user_id: str, email: str
) -> User:
    """Associa uma identidade Tupã ao perfil local do Jaci."""
    email = email.lower().strip()
    user = db.scalar(select(User).where(User.tupa_user_id == tupa_user_id))
    if user:
        return user

    user = db.scalar(select(User).where(User.email == email))
    if user:
        user.tupa_user_id = tupa_user_id
        db.commit()
        db.refresh(user)
        return user

    user = User(email=email, tupa_user_id=tupa_user_id, is_profile_complete=False)
    db.add(user)
    db.flush()

    default_group = Group(name="Minha Casa", owner_id=user.id)
    db.add(default_group)
    db.flush()
    db.execute(
        group_members.insert().values(
            user_id=user.id,
            group_id=default_group.id,
            joined_at=datetime.now(timezone.utc),
        )
    )
    for sort_order, cat_data in enumerate(DEFAULT_CATEGORIES):
        db.add(
            Category(
                name=cat_data["name"],
                color=cat_data["color"],
                group_id=default_group.id,
                sort_order=sort_order,
            )
        )
    db.commit()
    db.refresh(user)
    return user


async def authenticate_with_password(
    db: Session, email: str, password: str
) -> tuple[User, dict] | None:
    """Autentica no Tupã e carrega o perfil local."""
    tokens = await tupa_auth_service.token(email, password)
    payload = tupa_auth_service.decode_access_token(tokens["access_token"])
    if not payload or not payload.get("sub"):
        return None

    user = get_or_create_tupa_user(db, str(payload["sub"]), payload.get("email", email))
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return user, tokens


async def register_with_password(
    db: Session, name: str, email: str, password: str
) -> tuple[User, dict]:
    """Cria a identidade no Tupã e o perfil local no Jaci."""
    tupa_user_id = await tupa_auth_service.create_user(email, password)
    tokens = await tupa_auth_service.token(email, password)
    user = get_or_create_tupa_user(db, tupa_user_id, email)
    user.name = name.strip()
    user.is_profile_complete = True
    db.commit()
    db.refresh(user)
    return user, tokens


def setup_profile(db: Session, user: User, name: str) -> User:
    """Completa os dados locais do perfil."""
    user.name = name.strip()
    user.is_profile_complete = True
    db.commit()
    db.refresh(user)
    logger.info(f"Perfil configurado para {user.email}")
    return user


def update_profile(db: Session, user: User, name: str, email: str) -> User:
    """Atualiza os dados pessoais do usuário."""
    user.name = name.strip()
    user.email = email.lower().strip()
    db.commit()
    db.refresh(user)
    logger.info(f"Perfil atualizado para {user.email}")
    return user
