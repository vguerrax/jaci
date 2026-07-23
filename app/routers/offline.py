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
    get_execution_display_name,
    get_pending_items,
    incomplete_item as incomplete_item_service,
    remove_item_from_execution,
    start_execution,
    update_scheduled_execution,
    update_execution_item,
)
from app.services.notification_service import notify_execution_updated
from app.services.offline_cache_service import build_offline_snapshot
from app.services.sync_conflict_audit_service import (
    create_conflict_audit,
    list_conflict_audits,
    resolve_conflict_audit,
    serialize_conflict_audit,
)
from app.utils.datetime import parse_local_date
from app.websocket.manager import manager


router = APIRouter(prefix="/api/offline", tags=["Offline"])


class StartExecutionOperation(BaseModel):
    execution_id: int


class UpdateExecutionOperation(BaseModel):
    execution_id: int
    name: str
    scheduled_date: str
    budget: float | None = None


class ExecutionItemOperation(BaseModel):
    execution_id: int
    item_id: int
    action: str = Field(pattern="^(complete_item|incomplete_item|update_item)$")
    version: int
    name: str | None = None
    planned_quantity: float | None = None
    category_id: int | None = None
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


class ConflictResolutionOperation(BaseModel):
    resolution: str = Field(pattern="^(retry_local|discard_local|manual)$")


def _execution_state(execution) -> dict:
    return {
        "id": execution.id,
        "group_id": execution.group_id,
        "name": get_execution_display_name(execution),
        "status": execution.status.value if hasattr(execution.status, "value") else str(execution.status),
        "scheduled_date": execution.scheduled_date.isoformat() if execution.scheduled_date else None,
        "budget": execution.budget,
        "finished_at": execution.finished_at.isoformat() if execution.finished_at else None,
    }


def _item_state(item: ExecutionItem) -> dict:
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


def _raise_sync_conflict(
    db: Session,
    *,
    user: User,
    group_id: int,
    execution_id: int | None,
    operation: BaseModel,
    entity: str,
    entity_id: int | str,
    reason: str,
    message: str,
    remote_state: dict,
) -> None:
    audit = create_conflict_audit(
        db,
        user=user,
        group_id=group_id,
        execution_id=execution_id,
        operation_type=operation.__class__.__name__,
        entity=entity,
        entity_id=entity_id,
        reason=reason,
        message=message,
        local_state=operation,
        remote_state=remote_state,
    )
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "type": "sync_conflict",
            "audit_id": audit.id,
            "message": message,
            "entity": entity,
            "entity_id": entity_id,
            "reason": reason,
            "local": audit.local_state,
            "remote": audit.remote_state,
        },
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


@router.get("/conflicts")
async def offline_conflict_history(
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Histórico auditável de conflitos de sincronização dos grupos do usuário."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária",
        )
    return {
        "conflicts": [
            serialize_conflict_audit(audit)
            for audit in list_conflict_audits(db, user)
        ]
    }


@router.post("/conflicts/{audit_id}/resolution")
async def record_conflict_resolution(
    audit_id: int,
    operation: ConflictResolutionOperation,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Registra a resolução aplicada a um conflito sem apagar sua auditoria."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária",
        )

    audit = resolve_conflict_audit(
        db,
        audit_id=audit_id,
        user=user,
        resolution=operation.resolution,
    )
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conflito não encontrado",
        )
    return {"conflict": serialize_conflict_audit(audit)}


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
        _raise_sync_conflict(
            db,
            user=user,
            group_id=execution.group_id,
            execution_id=execution.id,
            operation=operation,
            entity="execution",
            entity_id=execution.id,
            reason="execution_already_completed",
            message="Não é possível iniciar execução já finalizada.",
            remote_state=_execution_state(execution),
        )
    if execution.status == ExecutionStatus.cancelled:
        _raise_sync_conflict(
            db,
            user=user,
            group_id=execution.group_id,
            execution_id=execution.id,
            operation=operation,
            entity="execution",
            entity_id=execution.id,
            reason="execution_cancelled",
            message="Não é possível iniciar execução cancelada.",
            remote_state=_execution_state(execution),
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


@router.post("/operations/update-execution")
async def sync_update_execution_operation(
    operation: UpdateExecutionOperation,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Aplica edição offline idempotente em uma execução agendada."""
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
    if execution.status != ExecutionStatus.scheduled:
        _raise_sync_conflict(
            db,
            user=user,
            group_id=execution.group_id,
            execution_id=execution.id,
            operation=operation,
            entity="execution",
            entity_id=execution.id,
            reason="execution_not_scheduled",
            message="Apenas execuções agendadas podem ser editadas.",
            remote_state=_execution_state(execution),
        )

    try:
        scheduled_date = parse_local_date(operation.scheduled_date)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Data agendada inválida.",
        ) from exc

    try:
        update_scheduled_execution(
            db,
            execution,
            operation.name,
            scheduled_date,
            operation.budget,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    execution_name = get_execution_display_name(execution)
    notify_execution_updated(db, execution, user, execution_name)

    try:
        await manager.broadcast(
            execution.id,
            "execution_updated",
            {
                "execution_id": execution.id,
                "name": execution_name,
                "scheduled_date": execution.scheduled_date.date().isoformat(),
                "budget": execution.budget,
                "user_email": user.email,
            },
        )
    except Exception:
        pass

    return {
        "status": "applied",
        "execution": {
            "id": execution.id,
            "name": execution_name,
            "status": ExecutionStatus.scheduled.value,
            "scheduled_date": execution.scheduled_date.date().isoformat(),
            "budget": execution.budget,
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
        _raise_sync_conflict(
            db,
            user=user,
            group_id=execution.group_id,
            execution_id=execution.id,
            operation=operation,
            entity="execution",
            entity_id=execution.id,
            reason="execution_not_editable",
            message="Execução não permite alterações.",
            remote_state=_execution_state(execution),
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
        _raise_sync_conflict(
            db,
            user=user,
            group_id=execution.group_id,
            execution_id=execution.id,
            operation=operation,
            entity="execution_item",
            entity_id=item.id,
            reason="stale_version",
            message="Item alterado por outro usuário.",
            remote_state=_item_state(item),
        )

    if operation.action == "update_item":
        if not operation.name or not operation.name.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Nome do item é obrigatório.",
            )
        if operation.planned_quantity is None or operation.planned_quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Quantidade planejada inválida.",
            )
        try:
            update_execution_item(
                db,
                item,
                operation.name.strip(),
                operation.planned_quantity,
                operation.category_id if operation.category_id and operation.category_id > 0 else None,
                operation.notes,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        event_name = "item_updated"
    elif operation.action == "complete_item":
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
        event_name = "item_updated"

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
            "name": item.name,
            "category_id": item.category_id,
            "planned_quantity": item.planned_quantity,
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
        _raise_sync_conflict(
            db,
            user=user,
            group_id=execution.group_id,
            execution_id=execution.id,
            operation=operation,
            entity="execution",
            entity_id=execution.id,
            reason="execution_not_editable",
            message="Execução não permite alterações.",
            remote_state=_execution_state(execution),
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
        _raise_sync_conflict(
            db,
            user=user,
            group_id=execution.group_id,
            execution_id=execution.id,
            operation=operation,
            entity="execution",
            entity_id=execution.id,
            reason="execution_not_editable",
            message="Execução não permite alterações.",
            remote_state=_execution_state(execution),
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
        _raise_sync_conflict(
            db,
            user=user,
            group_id=execution.group_id,
            execution_id=execution.id,
            operation=operation,
            entity="execution_item",
            entity_id=item.id,
            reason="item_already_completed",
            message="Não é possível remover item já concluído.",
            remote_state=_item_state(item),
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
        _raise_sync_conflict(
            db,
            user=user,
            group_id=execution.group_id,
            execution_id=execution.id,
            operation=operation,
            entity="execution",
            entity_id=execution.id,
            reason="execution_cancelled",
            message="Execução cancelada não pode ser finalizada.",
            remote_state=_execution_state(execution),
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
                new_date = parse_local_date(operation.new_date)
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
