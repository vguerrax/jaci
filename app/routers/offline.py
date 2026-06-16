from datetime import datetime, timezone, timedelta

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
    create_execution_from_pending,
    finalize_execution,
    get_execution_by_id,
    get_pending_items,
    incomplete_item as incomplete_item_service,
    remove_item_from_execution,
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


class RemoveExecutionItemOperation(BaseModel):
    execution_id: int
    item_id: int


class FinalizeExecutionOperation(BaseModel):
    execution_id: int
    action: str = Field(pattern="^(discard|new_execution)$")
    new_date: str | None = None


def _serialize_execution_conflict(execution) -> dict:
    return {
        "id": execution.id,
        "status": execution.status.value,
        "scheduled_date": execution.scheduled_date.isoformat()
        if execution.scheduled_date
        else None,
        "finished_at": execution.finished_at.isoformat()
        if execution.finished_at
        else None,
    }


def _serialize_item_conflict(item: ExecutionItem) -> dict:
    return {
        "id": item.id,
        "execution_id": item.execution_id,
        "name": item.name,
        "category_id": item.category_id,
        "planned_quantity": item.planned_quantity,
        "purchased_quantity": item.purchased_quantity,
        "unit_price": item.unit_price,
        "location": item.location,
        "notes": item.notes,
        "is_completed": item.is_completed,
        "version": item.version,
        "is_deleted": item.is_deleted,
    }


def _conflict_detail(
    *,
    message: str,
    entity: str,
    entity_id: int,
    local: BaseModel | dict,
    remote: dict,
    reason: str,
) -> dict:
    return {
        "type": "sync_conflict",
        "message": message,
        "entity": entity,
        "entity_id": entity_id,
        "reason": reason,
        "local": local.model_dump() if isinstance(local, BaseModel) else local,
        "remote": remote,
    }


def _raise_conflict(
    *,
    message: str,
    entity: str,
    entity_id: int,
    local: BaseModel | dict,
    remote: dict,
    reason: str,
) -> None:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=_conflict_detail(
            message=message,
            entity=entity,
            entity_id=entity_id,
            local=local,
            remote=remote,
            reason=reason,
        ),
    )


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
        _raise_conflict(
            message="A execução já foi finalizada no servidor.",
            entity="execution",
            entity_id=execution.id,
            local=operation,
            remote=_serialize_execution_conflict(execution),
            reason="execution_already_completed",
        )
    if execution.status == ExecutionStatus.cancelled:
        _raise_conflict(
            message="A execução foi cancelada no servidor.",
            entity="execution",
            entity_id=execution.id,
            local=operation,
            remote=_serialize_execution_conflict(execution),
            reason="execution_cancelled",
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
        _raise_conflict(
            message="A execução não aceita mais alterações no servidor.",
            entity="execution",
            entity_id=execution.id,
            local=operation,
            remote=_serialize_execution_conflict(execution),
            reason="execution_not_editable",
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
        _raise_conflict(
            message="O item foi alterado por outro usuário antes da sincronização.",
            entity="execution_item",
            entity_id=item.id,
            local=operation,
            remote=_serialize_item_conflict(item),
            reason="stale_version",
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
        _raise_conflict(
            message="A execução não aceita mais novos itens no servidor.",
            entity="execution",
            entity_id=execution.id,
            local=operation,
            remote=_serialize_execution_conflict(execution),
            reason="execution_not_editable",
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


@router.post("/operations/remove-execution-item")
async def sync_remove_execution_item_operation(
    operation: RemoveExecutionItemOperation,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Remove no servidor um item não concluído removido offline."""
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
        _raise_conflict(
            message="A execução não aceita remoções no servidor.",
            entity="execution",
            entity_id=execution.id,
            local=operation,
            remote=_serialize_execution_conflict(execution),
            reason="execution_not_editable",
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
    if item.is_completed:
        _raise_conflict(
            message="O item já foi marcado como comprado no servidor.",
            entity="execution_item",
            entity_id=item.id,
            local=operation,
            remote=_serialize_item_conflict(item),
            reason="item_already_completed",
        )

    item_name = item.name
    remove_item_from_execution(db, item)

    try:
        await manager.broadcast(
            operation.execution_id,
            "item_removed",
            {
                "item_id": operation.item_id,
                "item_name": item_name,
                "user_email": user.email,
            },
        )
    except Exception:
        pass

    return {
        "status": "applied",
        "item": {
            "id": operation.item_id,
            "execution_id": operation.execution_id,
            "is_deleted": True,
        },
    }


@router.post("/operations/finalize-execution")
async def sync_finalize_execution_operation(
    operation: FinalizeExecutionOperation,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Finaliza no servidor uma execução encerrada offline."""
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
    if execution.status == ExecutionStatus.cancelled:
        _raise_conflict(
            message="A execução foi cancelada no servidor e não pode ser finalizada.",
            entity="execution",
            entity_id=execution.id,
            local=operation,
            remote=_serialize_execution_conflict(execution),
            reason="execution_cancelled",
        )
    if execution.status == ExecutionStatus.completed:
        return {
            "status": "applied",
            "execution": {
                "id": execution.id,
                "status": ExecutionStatus.completed.value,
            },
            "next_execution_id": None,
        }

    pending = get_pending_items(db, execution.id)
    if pending and operation.action not in {"discard", "new_execution"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tratamento de pendentes é obrigatório.",
        )

    if operation.action == "discard" or not pending:
        finalize_execution(db, execution, discard_pending=True)
    else:
        new_date = datetime.now(timezone.utc) + timedelta(days=1)
        if operation.new_date:
            try:
                new_date = datetime.strptime(operation.new_date, "%Y-%m-%d")
                new_date = new_date.replace(tzinfo=timezone.utc)
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Data da nova execução inválida.",
                ) from exc
        create_execution_from_pending(db, execution, pending, new_date)
        finalize_execution(db, execution, discard_pending=False)

    from app.services.agenda_service import generate_next_execution

    next_execution = generate_next_execution(db, execution, user)

    try:
        await manager.broadcast(
            operation.execution_id,
            "execution_status_changed",
            {
                "new_status": "completed",
                "user_email": user.email,
            },
        )
    except Exception:
        pass

    return {
        "status": "applied",
        "execution": {
            "id": execution.id,
            "status": ExecutionStatus.completed.value,
            "finished_at": execution.finished_at.isoformat() if execution.finished_at else None,
        },
        "next_execution_id": next_execution.id if next_execution else None,
    }
