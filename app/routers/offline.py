from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.enums import ExecutionStatus
from app.models.execution import ExecutionItem
from app.models.user import User
from app.services.execution_service import (
    add_item_to_execution,
    complete_item as complete_item_service,
    get_execution_by_id,
    incomplete_item as incomplete_item_service,
    start_execution,
)
from app.services.offline_cache_service import build_offline_snapshot
from app.websocket.manager import manager


router = APIRouter(prefix="/api/offline", tags=["Offline"])


class StartExecutionOperation(BaseModel):
    execution_id: int


class ExecutionItemOperation(BaseModel):
    execution_id: int
    item_id: int
    action: str = Field(pattern="^(complete_item|incomplete_item)$")
    version: int
    purchased_quantity: float | None = None
    unit_price: float | None = None
    location: str | None = None
    notes: str | None = None


class AddExecutionItemOperation(BaseModel):
    execution_id: int
    temp_id: str
    name: str
    planned_quantity: float = 1
    category_id: int | None = None
    notes: str | None = None


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


@router.post("/operations/execution-item")
async def sync_execution_item_operation(
    operation: ExecutionItemOperation,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Aplica uma alteração offline em item de execução com bloqueio otimista."""
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
    if execution.status in {ExecutionStatus.completed, ExecutionStatus.cancelled}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Execução não permite alterações.",
        )

    item = db.scalar(
        select(ExecutionItem).where(
            ExecutionItem.id == operation.item_id,
            ExecutionItem.execution_id == operation.execution_id,
        )
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item não encontrado",
        )
    if item.version != operation.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Item alterado por outro usuário.",
        )

    if operation.action == "complete_item":
        if operation.purchased_quantity is None or operation.purchased_quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Quantidade comprada inválida.",
            )
        if operation.unit_price is None or operation.unit_price < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Valor unitário inválido.",
            )
        complete_item_service(
            db,
            item,
            operation.purchased_quantity,
            operation.unit_price,
            operation.location,
            operation.notes,
        )
        event_name = "item_completed"
    else:
        incomplete_item_service(db, item)
        event_name = "item_completed"

    try:
        await manager.broadcast(
            operation.execution_id,
            event_name,
            {
                "item_id": item.id,
                "item_name": item.name,
                "user_email": user.email,
                "total_price": item.total_price,
            },
        )
    except Exception:
        pass

    return {
        "status": "applied",
        "item": {
            "id": item.id,
            "execution_id": item.execution_id,
            "is_completed": item.is_completed,
            "purchased_quantity": item.purchased_quantity,
            "unit_price": item.unit_price,
            "location": item.location,
            "notes": item.notes,
            "version": item.version,
        },
    }


@router.post("/operations/add-execution-item")
async def sync_add_execution_item_operation(
    operation: AddExecutionItemOperation,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Cria no servidor um item de execução gerado offline com ID temporário."""
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
    if execution.status in {ExecutionStatus.completed, ExecutionStatus.cancelled}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Execução não permite alterações.",
        )
    if not operation.name.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nome do item é obrigatório.",
        )
    if operation.planned_quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Quantidade planejada inválida.",
        )

    try:
        item = add_item_to_execution(
            db,
            execution,
            operation.name,
            operation.planned_quantity,
            operation.category_id if operation.category_id and operation.category_id > 0 else None,
            operation.notes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    try:
        await manager.broadcast(
            operation.execution_id,
            "item_added",
            {
                "item_id": item.id,
                "item_name": item.name,
                "user_email": user.email,
            },
        )
    except Exception:
        pass

    return {
        "status": "applied",
        "temp_id": operation.temp_id,
        "item": {
            "id": item.id,
            "execution_id": item.execution_id,
            "category_id": item.category_id,
            "name": item.name,
            "planned_quantity": item.planned_quantity,
            "notes": item.notes,
            "version": item.version,
            "sort_order": item.sort_order,
        },
    }
