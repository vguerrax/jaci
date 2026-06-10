from datetime import datetime, timezone
import logging
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.models.user import User
from app.models.group import Group, group_members
from app.models.category import Category, DEFAULT_CATEGORIES
from app.utils.security import create_magic_token
from app.utils.email import send_magic_link

logger = logging.getLogger("jaci.groups")


def create_group(db: Session, name: str, owner: User) -> Group:
    """Cria um novo grupo e adiciona o owner como membro."""
    group = Group(name=name.strip(), owner_id=owner.id)
    db.add(group)
    db.flush()

    # Adiciona owner como membro
    db.execute(
        group_members.insert().values(
            user_id=owner.id,
            group_id=group.id,
            joined_at=datetime.now(timezone.utc),
        )
    )

    # Cria categorias padrão
    for sort_order, cat_data in enumerate(DEFAULT_CATEGORIES):
        category = Category(
            name=cat_data["name"],
            color=cat_data["color"],
            group_id=group.id,
            sort_order=sort_order,
        )
        db.add(category)

    db.commit()
    db.refresh(group)
    logger.info(f"Grupo '{group.name}' criado por {owner.email}")
    return group


def get_user_groups(db: Session, user: User) -> list[Group]:
    """Retorna todos os grupos do usuário."""
    return (
        db.execute(
            select(Group)
            .join(group_members, Group.id == group_members.c.group_id)
            .where(group_members.c.user_id == user.id)
            .order_by(Group.name)
        )
        .scalars()
        .all()
    )


def get_group_by_id(db: Session, group_id: int, user: User) -> Optional[Group]:
    """Retorna um grupo se o usuário for membro."""
    return db.scalar(
        select(Group)
        .join(group_members, Group.id == group_members.c.group_id)
        .where(
            Group.id == group_id,
            group_members.c.user_id == user.id,
        )
    )


def get_group_members(db: Session, group_id: int) -> list[User]:
    """Retorna todos os membros de um grupo."""
    return (
        db.execute(
            select(User)
            .join(group_members, User.id == group_members.c.user_id)
            .where(group_members.c.group_id == group_id)
            .order_by(User.email)
        )
        .scalars()
        .all()
    )


def is_group_owner(db: Session, group_id: int, user: User) -> bool:
    """Verifica se o usuário é o criador/dono do grupo."""
    group = db.scalar(select(Group).where(Group.id == group_id))
    if not group:
        return False
    return group.owner_id == user.id


def update_group_name(db: Session, group: Group, name: str, updated_by: User) -> dict:
    """Atualiza o nome do grupo quando solicitado pelo criador."""
    if group.owner_id != updated_by.id:
        return {
            "success": False,
            "message": "Apenas o criador do grupo pode alterar o nome.",
        }

    name = name.strip()
    if not name:
        return {"success": False, "message": "O nome do grupo é obrigatório."}

    if len(name) > 150:
        return {
            "success": False,
            "message": "O nome do grupo deve ter no máximo 150 caracteres.",
        }

    old_name = group.name
    group.name = name
    db.commit()
    db.refresh(group)
    logger.info(f"Grupo '{old_name}' renomeado para '{group.name}' por {updated_by.email}")
    return {"success": True, "message": "Nome do grupo atualizado."}


async def invite_member(
    db: Session,
    group: Group,
    email: str,
    invited_by: User,
) -> dict:
    """
    Convida um novo membro para o grupo via magic link.
    Retorna dict com success, message.
    """
    email = email.lower().strip()
 
    # Verifica se já é membro
    existing = db.scalar(
        select(User)
        .join(group_members, User.id == group_members.c.user_id)
        .where(
            User.email == email,
            group_members.c.group_id == group.id,
        )
    )
    if existing:
        return {
            "success": False,
            "message": f"{email} já é membro deste grupo.",
        }
 
    # Gera magic token
    token = create_magic_token(email)
 
    # Envia e-mail de convite
    sent = await send_magic_link(
        email=email,
        token=token,
        group_id=group.id,
        group_name=group.name,
        invited_by=invited_by.email,
    )
 
    if not sent:
        return {
            "success": False,
            "message": "Não foi possível enviar o convite. Tente novamente.",
        }
 
    logger.info(f"Convite enviado para {email} no grupo '{group.name}'")
    return {
        "success": True,
        "message": f"Convite enviado para {email}.",
    }


def add_member_to_group(db: Session, group_id: int, user: User) -> bool:
    """Adiciona usuário a um grupo. Retorna True se adicionado, False se já membro."""
    existing = db.scalar(
        select(group_members).where(
            group_members.c.user_id == user.id,
            group_members.c.group_id == group_id,
        )
    )
    if existing:
        return False

    db.execute(
        group_members.insert().values(
            user_id=user.id,
            group_id=group_id,
            joined_at=datetime.now(timezone.utc),
        )
    )
    db.commit()
    logger.info(f"{user.email} adicionado ao grupo {group_id}")
    return True


def remove_member(db: Session, group_id: int, member_id: int, removed_by: User) -> dict:
    """
    Remove um membro do grupo.
    Apenas o owner pode remover (exceto ele mesmo, com regras especiais).
    """
    # Verifica se quem remove é owner
    if not is_group_owner(db, group_id, removed_by):
        return {"success": False, "message": "Apenas o criador do grupo pode remover membros."}

    # Busca o membro a ser removido
    member = db.scalar(select(User).where(User.id == member_id))
    if not member:
        return {"success": False, "message": "Usuário não encontrado."}

    # Verifica se é o último membro
    member_count = db.scalar(
        select(func.count())
        .select_from(group_members)
        .where(group_members.c.group_id == group_id)
    )
    if member_count <= 1:
        return {
            "success": False,
            "message": "Não é possível remover o último membro do grupo.",
        }

    # Se remover a si mesmo (owner saindo), transfere ownership
    if member_id == removed_by.id:
        # Busca o membro mais antigo (exceto o owner atual)
        oldest_member = db.scalar(
            select(User)
            .join(group_members, User.id == group_members.c.user_id)
            .where(
                group_members.c.group_id == group_id,
                User.id != removed_by.id,
            )
            .order_by(group_members.c.joined_at.asc())
            .limit(1)
        )
        if oldest_member:
            group = db.scalar(select(Group).where(Group.id == group_id))
            group.owner_id = oldest_member.id
            db.commit()
            logger.info(
                f"Ownership do grupo '{group.name}' transferido "
                f"de {removed_by.email} para {oldest_member.email}"
            )

    # Remove o vínculo
    db.execute(
        delete(group_members).where(
            group_members.c.user_id == member_id,
            group_members.c.group_id == group_id,
        )
    )
    db.commit()
    logger.info(f"{member.email} removido do grupo {group_id} por {removed_by.email}")
    return {"success": True, "message": f"{member.email} removido do grupo."}


def switch_active_group(request, group_id: int, user: User) -> dict:
    """Troca o grupo ativo na sessão."""
    # A validação de pertencimento é feita na rota
    request.session["active_group_id"] = group_id
    return {"success": True}
