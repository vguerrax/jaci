from datetime import datetime, timezone
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.group import Group, group_members
from app.models.category import Category, DEFAULT_CATEGORIES
from app.utils.security import (
    create_magic_token,
    decode_magic_token,
    hash_password,
    verify_password,
)
from app.utils.email import send_magic_link

logger = logging.getLogger("jaci.auth")


async def request_magic_link(db: Session, email: str) -> dict:
    """
    Gera magic token e envia por e-mail.
    Retorna status e mensagem.
    """
    email = email.lower().strip()

    # Gera token
    token = create_magic_token(email)

    # Envia e-mail
    sent = await send_magic_link(email, token)

    if not sent:
        return {
            "success": False,
            "message": "Não foi possível enviar o e-mail. Tente novamente.",
        }

    return {
        "success": True,
        "message": f"Enviamos um link mágico para {email}. Verifique sua caixa de entrada.",
    }


def authenticate_with_password(
    db: Session, email: str, password: str
) -> User | None:
    """Autentica usuário com e-mail e senha."""
    email = email.lower().strip()
    user = db.scalar(select(User).where(User.email == email))

    if not user or not user.password_hash:
        return None

    if not verify_password(password, user.password_hash):
        return None

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    return user


def verify_magic_token(db: Session, token: str) -> User | None:
    """
    Valida magic token.
    Se o e-mail não existe, cria usuário + grupo padrão + categorias padrão.
    Retorna o usuário (existente ou recém-criado) ou None se token inválido.
    """
    from app.utils.security import decode_magic_token

    email = decode_magic_token(token)
    if not email:
        return None

    email = email.lower().strip()

    # Busca usuário existente
    user = db.scalar(select(User).where(User.email == email))

    if user is None:
        # Cria novo usuário
        user = User(email=email, is_profile_complete=False)
        db.add(user)
        db.flush()  # Gera user.id

        # Cria grupo padrão
        default_group = Group(
            name="Minha Casa",
            owner_id=user.id,
        )
        db.add(default_group)
        db.flush()  # Gera group.id

        # Adiciona usuário como membro do grupo
        db.execute(
            group_members.insert().values(
                user_id=user.id,
                group_id=default_group.id,
                joined_at=datetime.now(timezone.utc),
            )
        )

        # Cria categorias padrão
        for sort_order, cat_data in enumerate(DEFAULT_CATEGORIES):
            category = Category(
                name=cat_data["name"],
                color=cat_data["color"],
                group_id=default_group.id,
                sort_order=sort_order,
            )
            db.add(category)

        db.commit()
        db.refresh(user)
        logger.info(f"Novo usuário criado: {email}")

    # Atualiza último login
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    return user


def setup_profile(
    db: Session, user: User, name: str, password: str
) -> User:
    """Completa o perfil do usuário com nome e senha."""
    user.name = name.strip()
    user.password_hash = hash_password(password)
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


def email_is_available(db: Session, email: str, user: User) -> bool:
    """Verifica se o e-mail pode ser usado pelo usuário."""
    existing_user = db.scalar(
        select(User).where(
            User.email == email.lower().strip(),
            User.id != user.id,
        )
    )
    return existing_user is None


def change_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str,
) -> bool:
    """Altera a senha após validar a senha atual."""
    if not user.password_hash or not verify_password(current_password, user.password_hash):
        return False

    user.password_hash = hash_password(new_password)
    db.commit()
    logger.info(f"Senha alterada para {user.email}")
    return True
