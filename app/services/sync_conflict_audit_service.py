from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sync_conflict_audit import SyncConflictAudit
from app.models.user import User


def _jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_jsonable(item) for item in value]
    return value


def create_conflict_audit(
    db: Session,
    *,
    user: User,
    group_id: int,
    execution_id: int | None,
    operation_type: str,
    entity: str,
    entity_id: int | str,
    reason: str,
    message: str,
    local_state: BaseModel | dict[str, Any],
    remote_state: dict[str, Any] | None,
) -> SyncConflictAudit:
    audit = SyncConflictAudit(
        group_id=group_id,
        execution_id=execution_id,
        user_id=user.id,
        operation_type=operation_type,
        entity=entity,
        entity_id=str(entity_id),
        reason=reason,
        message=message,
        local_state=_jsonable(local_state),
        remote_state=_jsonable(remote_state) if remote_state is not None else None,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def list_conflict_audits(db: Session, user: User) -> list[SyncConflictAudit]:
    group_ids = [group.id for group in user.groups]
    if not group_ids:
        return []

    return list(
        db.scalars(
            select(SyncConflictAudit)
            .where(SyncConflictAudit.group_id.in_(group_ids))
            .order_by(SyncConflictAudit.created_at.desc(), SyncConflictAudit.id.desc())
        )
    )


def resolve_conflict_audit(
    db: Session,
    *,
    audit_id: int,
    user: User,
    resolution: str,
) -> SyncConflictAudit | None:
    group_ids = [group.id for group in user.groups]
    if not group_ids:
        return None

    audit = db.scalar(
        select(SyncConflictAudit)
        .where(SyncConflictAudit.id == audit_id)
        .where(SyncConflictAudit.group_id.in_(group_ids))
    )
    if not audit:
        return None

    audit.resolution_applied = resolution
    audit.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(audit)
    return audit


def serialize_conflict_audit(audit: SyncConflictAudit) -> dict[str, Any]:
    return {
        "id": audit.id,
        "group_id": audit.group_id,
        "execution_id": audit.execution_id,
        "user_id": audit.user_id,
        "operation_type": audit.operation_type,
        "entity": audit.entity,
        "entity_id": audit.entity_id,
        "reason": audit.reason,
        "message": audit.message,
        "local_state": audit.local_state,
        "remote_state": audit.remote_state,
        "resolution_applied": audit.resolution_applied,
        "created_at": audit.created_at.isoformat() if audit.created_at else None,
        "resolved_at": audit.resolved_at.isoformat() if audit.resolved_at else None,
    }
