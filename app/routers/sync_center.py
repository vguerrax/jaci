from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_active_group, get_current_user
from app.models.user import User
from app.templating import templates


router = APIRouter(prefix="/sync", tags=["Sync"])


@router.get("", include_in_schema=False)
async def sync_center(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
    active_group=Depends(get_active_group),
):
    """Central local para visualização e resolução da fila de sincronização."""
    _ = db
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    return templates.TemplateResponse(
        request,
        "pages/sync/center.html",
        {
            "request": request,
            "user": user,
            "active_group": active_group,
            "active_page": "sync",
        },
    )
