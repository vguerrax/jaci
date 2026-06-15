"""
Dependências reutilizáveis para injeção em rotas.
"""
from fastapi import Request, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.group import Group, group_members
from app.utils.security import decode_access_token
from sqlalchemy import select


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User | None:
    """
    Obtém o usuário autenticado a partir do cookie de sessão.
    Funciona como dependência FastAPI — pode ser usada em qualquer rota.
    """
    token = request.cookies.get("jaci_session")
    
    if not token:
        return None
    
    payload = decode_access_token(token)
    if not payload:
        return None
    
    tupa_user_id = payload.get("sub")
    if not tupa_user_id:
        return None

    user = db.scalar(select(User).where(User.tupa_user_id == str(tupa_user_id)))
    
    return user


async def get_active_group(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
) -> Group | None:
    """
    Obtém o grupo ativo do usuário a partir do cookie.
    Se não houver cookie mas o usuário tiver grupos, retorna o primeiro.
    """
    if not user:
        return None

    active_group_id = request.cookies.get("jaci_active_group")

    if active_group_id:
        try:
            gid = int(active_group_id)
            group = db.scalar(
                select(Group)
                .join(group_members, Group.id == group_members.c.group_id)
                .where(
                    Group.id == gid,
                    group_members.c.user_id == user.id,
                )
            )
            if group:
                return group
        except (ValueError, TypeError):
            pass

    # Fallback: primeiro grupo do usuário
    if user.groups:
        return user.groups[0]

    return None


def require_user(user: User | None = Depends(get_current_user)) -> User:
    """
    Dependência que exige usuário autenticado.
    Levanta exceção se não autenticado.
    """
    if user is None:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária",
        )
    return user


async def get_current_user_ws(
    db: Session = Depends(get_db),
    token: str | None = None,
) -> User | None:
    """
    Get authenticated user from JWT token (for WebSocket).
    """
    if not token:
        return None
 
    from app.utils.security import decode_access_token
    payload = decode_access_token(token)
    if not payload:
        return None
 
    tupa_user_id = payload.get("sub")
    if not tupa_user_id:
        return None

    user = db.scalar(select(User).where(User.tupa_user_id == str(tupa_user_id)))
    return user


async def get_unread_notification_count(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
) -> int:
    """Get unread notification count for navbar badge."""
    if not user:
        return 0
    from app.services.notification_service import get_unread_count
    return get_unread_count(db, user.id)
