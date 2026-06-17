import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, update

from app.models.user import User
from app.models.group import Group, group_members
from app.models.execution import Execution
from app.models.notification import Notification

logger = logging.getLogger("jaci.notifications")


def create_notification(
    db: Session,
    user_id: int,
    group_id: int,
    type_: str,
    title: str,
    message: str,
    execution_id: Optional[int] = None,
) -> Notification:
    """Cria uma notificação para um usuário."""
    notification = Notification(
        user_id=user_id,
        group_id=group_id,
        execution_id=execution_id,
        type=type_,
        title=title,
        message=message,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    logger.info(
        f"Notificação criada: user={user_id}, type={type_}, title='{title}'"
    )
    return notification


def notify_group_members(
    db: Session,
    group_id: int,
    exclude_user_id: Optional[int],
    type_: str,
    title: str,
    message: str,
    execution_id: Optional[int] = None,
) -> list[Notification]:
    """
    Envia notificação para todos os membros do grupo,
    exceto o usuário que gerou o evento.
    """
    members = db.execute(
        select(User)
        .join(group_members, User.id == group_members.c.user_id)
        .where(group_members.c.group_id == group_id)
    ).scalars().all()

    notifications = []
    for member in members:
        if exclude_user_id and member.id == exclude_user_id:
            continue
        notification = create_notification(
            db, member.id, group_id, type_, title, message, execution_id
        )
        notifications.append(notification)

    return notifications


def notify_execution_started(
    db: Session,
    execution: Execution,
    started_by: User,
    template_name: str,
) -> None:
    """Notifica membros que uma compra foi iniciada."""
    notify_group_members(
        db,
        execution.group_id,
        started_by.id,
        "execution_started",
        "Compra iniciada",
        f"{started_by.name} iniciou a compra '{template_name}'.",
        execution.id,
    )


def notify_execution_completed(
    db: Session,
    execution: Execution,
    finished_by: User,
    template_name: str,
    total_spent: float,
) -> None:
    """Notifica membros que uma compra foi finalizada."""
    notify_group_members(
        db,
        execution.group_id,
        finished_by.id,
        "execution_completed",
        "Compra finalizada",
        f"{finished_by.name} finalizou '{template_name}'. Total: R$ {total_spent:.2f}",
        execution.id,
    )


def notify_execution_updated(
    db: Session,
    execution: Execution,
    updated_by: User,
    execution_name: str,
) -> None:
    """Notifica membros que uma compra agendada foi alterada."""
    actor = updated_by.name or updated_by.email
    notify_group_members(
        db,
        execution.group_id,
        updated_by.id,
        "execution_updated",
        "Compra alterada",
        f"{actor} alterou a compra '{execution_name}'.",
        execution.id,
    )


def get_unread_count(db: Session, user_id: int) -> int:
    """Retorna contagem de notificações não lidas."""
    return db.scalar(
        select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
    ) or 0


def get_notifications(
    db: Session,
    user_id: int,
    limit: int = 50,
    unread_only: bool = False,
) -> list[Notification]:
    """Retorna notificações do usuário, mais recentes primeiro."""
    query = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    if unread_only:
        query = query.where(Notification.is_read == False)
    return db.execute(query).scalars().all()


def mark_as_read(db: Session, notification_id: int, user_id: int) -> bool:
    """Marca uma notificação como lida."""
    notification = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )
    if notification:
        notification.is_read = True
        db.commit()
        return True
    return False


def mark_all_as_read(db: Session, user_id: int) -> int:
    """Marca todas as notificações do usuário como lidas."""
    result = db.execute(
        update(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        .values(is_read=True)
    )
    db.commit()
    count = result.rowcount
    logger.info(f"{count} notificações marcadas como lidas para user={user_id}")
    return count
