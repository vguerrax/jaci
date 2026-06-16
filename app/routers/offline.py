from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.enums import ExecutionStatus
from app.models.user import User
from app.services.execution_service import get_execution_by_id, start_execution
from app.services.offline_cache_service import build_offline_snapshot
from app.websocket.manager import manager


router = APIRouter(prefix="/api/offline", tags=["Offline"])


class StartExecutionOperation(BaseModel):
    execution_id: int


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


@router.post("/operations/start-execution")
async def sync_start_execution_operation(
    operation: StartExecutionOperation,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Aplica uma transição offline de execução agendada para em andamento."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária",
        )

    execution = get_execution_by_id(db, operation.execution_id, user)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execução não encontrada",
        )
    if execution.status == ExecutionStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível iniciar execução já finalizada.",
        )
    if execution.status == ExecutionStatus.cancelled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível iniciar execução cancelada.",
        )

    if execution.status == ExecutionStatus.scheduled:
        start_execution(db, execution)
        try:
            await manager.broadcast(
                execution.id,
                "execution_status_changed",
                {
                    "new_status": "in_progress",
                    "user_email": user.email,
                },
            )
        except Exception:
            pass

    return {
        "status": "applied",
        "execution": {
            "id": execution.id,
            "status": ExecutionStatus.in_progress.value,
        },
    }
