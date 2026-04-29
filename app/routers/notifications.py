from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_active_group
from app.models.user import User
from app.services.notification_service import (
    get_notifications,
    get_unread_count,
    mark_as_read,
    mark_all_as_read,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", include_in_schema=False)
async def list_notifications(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """List notifications for the current user."""
    from app.main import templates

    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    notifications = get_notifications(db, user.id)

    return templates.TemplateResponse(
        "pages/notifications/list.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "notifications": notifications,
            "unread_count": get_unread_count(db, user.id),
            "active_page": "notifications",
        },
    )


@router.post("/{notification_id}/read")
async def handle_mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Mark a notification as read."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    mark_as_read(db, notification_id, user.id)
    return RedirectResponse(url="/notifications", status_code=303)


@router.post("/read-all")
async def handle_mark_all_read(
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Mark all notifications as read."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    mark_all_as_read(db, user.id)
    return RedirectResponse(url="/notifications", status_code=303)