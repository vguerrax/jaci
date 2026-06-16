from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.offline_cache_service import build_offline_snapshot


router = APIRouter(prefix="/api/offline", tags=["Offline"])


@router.get("/snapshot")
async def offline_snapshot(
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Snapshot somente leitura dos dados essenciais para cache local."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária",
        )
    return build_offline_snapshot(db, user)
