import asyncio
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.models import Execution, ExecutionItem, SyncConflictAudit
from app.models.enums import ExecutionStatus, RecurrenceType
from app.routers.offline import (
    AddExecutionItemOperation,
    ExecutionItemOperation,
    FinalizeExecutionOperation,
    RemoveExecutionItemOperation,
    StartExecutionOperation,
    ConflictResolutionOperation,
    offline_conflict_history,
    offline_snapshot,
    record_conflict_resolution,
    sync_add_execution_item_operation,
    sync_execution_item_operation,
    sync_finalize_execution_operation,
    sync_remove_execution_item_operation,
    sync_start_execution_operation,
)
from app.services.offline_cache_service import build_offline_snapshot
from app.services.template_service import add_item_to_template, create_template


def test_offline_snapshot_contains_essential_read_only_data(
    db, make_user, make_group, make_category
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    category = make_category(group, "Mantimentos")
    template = create_template(db, group, "Mensal", RecurrenceType.monthly, 500)
    item = add_item_to_template(db, template, "Arroz", 2, category.id)
    execution = Execution(
        group_id=group.id,
        template_id=template.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        created_by=user.id,
    )
    db.add(execution)
    db.flush()
    db.add(
        ExecutionItem(
            execution_id=execution.id,
            name="Arroz",
            category_id=category.id,
            planned_quantity=2,
        )
    )
    db.commit()

    snapshot = build_offline_snapshot(db, user)

    assert snapshot["schema_version"] == 1
    assert snapshot["groups"] == [
        {
            "id": group.id,
            "name": "Casa",
            "owner_id": user.id,
            "uncategorized_first": False,
            "created_at": snapshot["groups"][0]["created_at"],
        }
    ]
    assert snapshot["categories"][0]["name"] == "Mantimentos"
    assert snapshot["templates"][0]["recurrence"] == "monthly"
    assert snapshot["template_items"][0]["id"] == item.id
    assert snapshot["executions"][0]["status"] == "in_progress"
    assert snapshot["execution_items"][0]["name"] == "Arroz"
    assert "location" in snapshot["execution_items"][0]


def test_offline_snapshot_is_scoped_to_user_groups(db, make_user, make_group):
    user = make_user("ana@example.com")
    group = make_group("Casa", owner=user)
    other_group = make_group("Outra")
    create_template(db, group, "Minha lista", RecurrenceType.monthly)
    create_template(db, other_group, "Lista alheia", RecurrenceType.monthly)

    snapshot = build_offline_snapshot(db, user)

    assert [group["name"] for group in snapshot["groups"]] == ["Casa"]
    assert [template["name"] for template in snapshot["templates"]] == ["Minha lista"]


def test_offline_snapshot_requires_authentication(db):
    with pytest.raises(HTTPException) as error:
        asyncio.run(offline_snapshot(db=db, user=None))

    assert error.value.status_code == 401


def test_offline_start_execution_operation_applies_pending_change(db, make_user, make_group):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.scheduled,
        created_by=user.id,
    )
    db.add(execution)
    db.commit()

    result = asyncio.run(
        sync_start_execution_operation(
            StartExecutionOperation(execution_id=execution.id),
            db=db,
            user=user,
        )
    )

    db.refresh(execution)
    assert result["status"] == "applied"
    assert result["execution"]["status"] == "in_progress"
    assert execution.status == ExecutionStatus.in_progress


def test_offline_start_execution_operation_rejects_foreign_execution(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    other_user = make_user("bia@example.com")
    other_group = make_group("Outra", owner=other_user)
    execution = Execution(
        group_id=other_group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.scheduled,
        created_by=other_user.id,
    )
    db.add(execution)
    db.commit()

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            sync_start_execution_operation(
                StartExecutionOperation(execution_id=execution.id),
                db=db,
                user=user,
            )
        )

    assert error.value.status_code == 404


def test_offline_complete_item_operation_applies_pending_change(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        created_by=user.id,
    )
    db.add(execution)
    db.flush()
    item = ExecutionItem(execution_id=execution.id, name="Arroz", planned_quantity=2)
    db.add(item)
    db.commit()

    result = asyncio.run(
        sync_execution_item_operation(
            ExecutionItemOperation(
                execution_id=execution.id,
                item_id=item.id,
                action="complete_item",
                version=item.version,
                purchased_quantity=1.5,
                unit_price=8.9,
                location="Mercado",
                notes="Pacote pequeno",
            ),
            db=db,
            user=user,
        )
    )

    db.refresh(item)
    assert result["status"] == "applied"
    assert result["item"]["is_completed"] is True
    assert item.is_completed is True
    assert item.purchased_quantity == 1.5
    assert item.unit_price == 8.9
    assert item.location == "Mercado"
    assert item.notes == "Pacote pequeno"
    assert item.version == 2


def test_offline_incomplete_item_operation_applies_pending_change(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        created_by=user.id,
    )
    db.add(execution)
    db.flush()
    item = ExecutionItem(
        execution_id=execution.id,
        name="Feijão",
        planned_quantity=1,
        purchased_quantity=1,
        unit_price=7,
        location="Mercado",
        is_completed=True,
    )
    db.add(item)
    db.commit()

    result = asyncio.run(
        sync_execution_item_operation(
            ExecutionItemOperation(
                execution_id=execution.id,
                item_id=item.id,
                action="incomplete_item",
                version=item.version,
            ),
            db=db,
            user=user,
        )
    )

    db.refresh(item)
    assert result["status"] == "applied"
    assert item.is_completed is False
    assert item.purchased_quantity is None
    assert item.unit_price is None
    assert item.location is None
    assert item.version == 2


def test_offline_update_item_operation_applies_pending_change(
    db, make_user, make_group, make_category
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    category = make_category(group, "Limpeza")
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        created_by=user.id,
    )
    db.add(execution)
    db.flush()
    item = ExecutionItem(
        execution_id=execution.id,
        name="Sabão",
        planned_quantity=1,
        notes="Em pó",
    )
    db.add(item)
    db.commit()

    result = asyncio.run(
        sync_execution_item_operation(
            ExecutionItemOperation(
                execution_id=execution.id,
                item_id=item.id,
                action="update_item",
                version=item.version,
                name="Sabão líquido",
                planned_quantity=2,
                category_id=category.id,
                notes="Refil",
            ),
            db=db,
            user=user,
        )
    )

    db.refresh(item)
    assert result["status"] == "applied"
    assert result["item"]["name"] == "Sabão líquido"
    assert result["item"]["planned_quantity"] == 2
    assert result["item"]["category_id"] == category.id
    assert item.name == "Sabão líquido"
    assert item.planned_quantity == 2
    assert item.category_id == category.id
    assert item.notes == "Refil"
    assert item.is_completed is False
    assert item.version == 2


def test_offline_item_operation_rejects_stale_version(db, make_user, make_group):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        created_by=user.id,
    )
    db.add(execution)
    db.flush()
    item = ExecutionItem(
        execution_id=execution.id,
        name="Café",
        planned_quantity=1,
        version=3,
    )
    db.add(item)
    db.commit()

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            sync_execution_item_operation(
                ExecutionItemOperation(
                    execution_id=execution.id,
                    item_id=item.id,
                    action="complete_item",
                    version=2,
                    purchased_quantity=1,
                    unit_price=12,
                ),
                db=db,
                user=user,
            )
        )

    assert error.value.status_code == 409
    assert error.value.detail["type"] == "sync_conflict"
    assert error.value.detail["audit_id"]
    assert error.value.detail["local"]["version"] == 2
    assert error.value.detail["remote"]["version"] == 3

    audit = db.scalar(select(SyncConflictAudit))
    assert audit is not None
    assert audit.execution_id == execution.id
    assert audit.user_id == user.id
    assert audit.operation_type == "ExecutionItemOperation"
    assert audit.entity == "execution_item"
    assert audit.entity_id == str(item.id)
    assert audit.local_state["version"] == 2
    assert audit.remote_state["version"] == 3
    assert audit.resolution_applied is None


def test_offline_conflict_history_lists_and_resolves_audits(db, make_user, make_group):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        created_by=user.id,
    )
    db.add(execution)
    db.flush()
    item = ExecutionItem(
        execution_id=execution.id,
        name="Café",
        planned_quantity=1,
        version=3,
    )
    db.add(item)
    db.commit()

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            sync_execution_item_operation(
                ExecutionItemOperation(
                    execution_id=execution.id,
                    item_id=item.id,
                    action="complete_item",
                    version=2,
                    purchased_quantity=1,
                    unit_price=12,
                ),
                db=db,
                user=user,
            )
        )
    audit_id = error.value.detail["audit_id"]

    history = asyncio.run(offline_conflict_history(db=db, user=user))
    assert history["conflicts"][0]["id"] == audit_id
    assert history["conflicts"][0]["resolution_applied"] is None

    resolved = asyncio.run(
        record_conflict_resolution(
            audit_id,
            ConflictResolutionOperation(resolution="discard_local"),
            db=db,
            user=user,
        )
    )

    history_after_resolution = asyncio.run(offline_conflict_history(db=db, user=user))
    assert resolved["conflict"]["resolution_applied"] == "discard_local"
    assert resolved["conflict"]["resolved_at"] is not None
    assert history_after_resolution["conflicts"][0]["id"] == audit_id
    assert history_after_resolution["conflicts"][0]["resolution_applied"] == "discard_local"


def test_offline_add_item_operation_creates_real_item_from_temp_id(
    db, make_user, make_group, make_category
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    category = make_category(group, "Hortifruti")
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        created_by=user.id,
    )
    db.add(execution)
    db.commit()

    result = asyncio.run(
        sync_add_execution_item_operation(
            AddExecutionItemOperation(
                execution_id=execution.id,
                temp_id="temp-123",
                name="Banana",
                planned_quantity=6,
                category_id=category.id,
                notes="Prata",
            ),
            db=db,
            user=user,
        )
    )

    item = db.scalar(
        select(ExecutionItem)
        .where(ExecutionItem.execution_id == execution.id)
        .where(ExecutionItem.name == "Banana")
    )

    assert result["status"] == "applied"
    assert result["temp_id"] == "temp-123"
    assert result["item"]["id"] != "temp-123"
    assert result["item"]["name"] == "Banana"
    assert item is not None


def test_offline_add_item_operation_rejects_foreign_category(
    db, make_user, make_group, make_category
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    other_group = make_group("Outra")
    foreign_category = make_category(other_group, "Alheia")
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        created_by=user.id,
    )
    db.add(execution)
    db.commit()

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            sync_add_execution_item_operation(
                AddExecutionItemOperation(
                    execution_id=execution.id,
                    temp_id="temp-456",
                    name="Sabão",
                    planned_quantity=1,
                    category_id=foreign_category.id,
                ),
                db=db,
                user=user,
            )
        )

    assert error.value.status_code == 422


def test_offline_remove_item_operation_removes_incomplete_item(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        created_by=user.id,
    )
    db.add(execution)
    db.flush()
    item = ExecutionItem(execution_id=execution.id, name="Arroz", planned_quantity=2)
    db.add(item)
    db.commit()
    item_id = item.id

    result = asyncio.run(
        sync_remove_execution_item_operation(
            RemoveExecutionItemOperation(
                execution_id=execution.id,
                item_id=item_id,
            ),
            db=db,
            user=user,
        )
    )

    stored = db.scalar(select(ExecutionItem).where(ExecutionItem.id == item_id))
    assert result["status"] == "applied"
    assert result["item"]["is_deleted"] is True
    assert stored is None


def test_offline_remove_item_operation_rejects_completed_item(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        created_by=user.id,
    )
    db.add(execution)
    db.flush()
    item = ExecutionItem(
        execution_id=execution.id,
        name="Feijão",
        planned_quantity=1,
        is_completed=True,
    )
    db.add(item)
    db.commit()

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            sync_remove_execution_item_operation(
                RemoveExecutionItemOperation(
                    execution_id=execution.id,
                    item_id=item.id,
                ),
                db=db,
                user=user,
            )
        )

    assert error.value.status_code == 409


def test_offline_finalize_execution_operation_generates_next_cycle_on_sync(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly, 500)
    execution = Execution(
        group_id=group.id,
        template_id=template.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        created_by=user.id,
    )
    db.add(execution)
    db.flush()
    db.add(
        ExecutionItem(
            execution_id=execution.id,
            name="Arroz",
            planned_quantity=1,
            purchased_quantity=1,
            unit_price=10,
            is_completed=True,
        )
    )
    db.commit()

    result = asyncio.run(
        sync_finalize_execution_operation(
            FinalizeExecutionOperation(
                execution_id=execution.id,
                action="discard",
            ),
            db=db,
            user=user,
        )
    )

    db.refresh(execution)
    next_execution = db.scalar(
        select(Execution).where(
            Execution.template_id == template.id,
            Execution.id != execution.id,
            Execution.status == ExecutionStatus.scheduled,
        )
    )

    assert result["status"] == "applied"
    assert result["execution"]["status"] == "completed"
    assert result["next_execution_id"] == next_execution.id
    assert execution.status == ExecutionStatus.completed


def test_offline_finalize_execution_operation_handles_pending_items_on_sync(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        created_by=user.id,
    )
    db.add(execution)
    db.flush()
    db.add(
        ExecutionItem(
            execution_id=execution.id,
            name="Feijão",
            planned_quantity=1,
        )
    )
    db.commit()

    result = asyncio.run(
        sync_finalize_execution_operation(
            FinalizeExecutionOperation(
                execution_id=execution.id,
                action="new_execution",
                new_date="2026-06-20",
            ),
            db=db,
            user=user,
        )
    )

    db.refresh(execution)
    carryover = db.scalar(
        select(Execution).where(
            Execution.id != execution.id,
            Execution.group_id == group.id,
            Execution.status == ExecutionStatus.scheduled,
        )
    )

    assert result["status"] == "applied"
    assert execution.status == ExecutionStatus.completed
    assert carryover is not None
    assert carryover.is_standalone is True


def test_offline_cache_frontend_uses_indexeddb_and_read_only_snapshot():
    script = Path("app/static/js/offline-cache.js").read_text()

    assert "indexedDB.open" in script
    assert "const DB_VERSION = 10" in script
    assert "'indexedDB' in window" in script
    assert "jaci-offline-cache" in script
    assert "'groups'" in script
    assert "'categories'" in script
    assert "'templates'" in script
    assert "'executions'" in script
    assert "'execution_items'" in script
    assert "'pending_operations'" in script
    assert "buildQueuedOperation" in script
    assert "tipo:" in script
    assert "entidade:" in script
    assert "entidade_id:" in script
    assert "tentativas: 0" in script
    assert "sortOperationsByCreation" in script
    assert "recordSyncAttempt" in script
    assert "tentativas: Number(operation.tentativas || 0) + 1" in script
    assert "PENDING_ERRORS_KEY" in script
    assert "jaci_pending_errors" in script
    assert "PENDING_CONFLICTS_KEY" in script
    assert "jaci_pending_conflicts" in script
    assert "renderPendingState" in script
    assert "Number(operation.tentativas || 0) > 0" in script
    assert "SYNC_RETRY_BASE_DELAY_MS" in script
    assert "SYNC_RETRY_MAX_DELAY_MS" in script
    assert "getRetryDelay" in script
    assert "isTransientStatus" in script
    assert "requires_manual_intervention" in script
    assert "renderSyncCenter" in script
    assert "scheduleAutomaticRetry" in script
    assert "runAutomaticSync" in script
    assert "syncInFlight" in script
    assert "window.addEventListener('jaci:sync-manual'" in script
    assert "fetch(SNAPSHOT_URL" in script
    assert "START_EXECUTION_SYNC_URL" in script
    assert "EXECUTION_ITEM_SYNC_URL" in script
    assert "ADD_EXECUTION_ITEM_SYNC_URL" in script
    assert "REMOVE_EXECUTION_ITEM_SYNC_URL" in script
    assert "FINALIZE_EXECUTION_SYNC_URL" in script
    assert "data-offline-start-execution" in script
    assert "data-offline-add-item" in script
    assert "data-offline-finalize-link" in script
    assert "data-offline-finalize-execution" in script
    assert "data-offline-complete-item" in script
    assert "data-offline-edit-item" in script
    assert "data-offline-edit-item-form" in script
    assert "readEditItemOperationFromForm" in script
    assert "openOfflineEditModal" in script
    assert "handleOfflineEditItemClick" in script
    assert "document.addEventListener('click', handleOfflineEditItemClick, true)" in script
    assert "offlineEditItemModal" in script
    assert "openOfflineCompleteModal" in script
    assert "showManualModal" in script
    assert "closeManualModal" in script
    assert "setupOfflineCompleteModalControls" in script
    assert "window.JaciModal" in script
    assert "dataset.jaciModalBackdrop" in script
    assert "bootstrap.Modal.getOrCreateInstance(modalEl" not in script
    assert "offlineCompleteItemModal" in script
    assert "disableOfflineCompleteBootstrapTriggers" in script
    assert "disableMissingCompleteModalTriggers" in script
    assert "document.addEventListener('pointerdown', disableMissingCompleteModalTriggers, true)" in script
    assert "document.addEventListener('touchstart', disableMissingCompleteModalTriggers, true)" in script
    assert "completeModalTargetMissing" in script
    assert "shouldUseOfflineCompleteModal" in script
    assert "targetSelector && !document.querySelector(targetSelector)" in script
    assert "form.dataset.forceOfflineSubmit = 'true'" in script
    assert "forcedOfflineSubmit" in script
    assert "setOfflineCompleteBootstrapTriggersEnabled" in script
    assert "button.removeAttribute('data-bs-toggle')" in script
    assert "button.removeAttribute('data-bs-target')" in script
    assert "window.addEventListener('online', function ()" in script
    assert "window.addEventListener('offline', disableOfflineCompleteBootstrapTriggers)" in script
    assert "getLastLocationForExecution" in script
    assert "getLastLocationFromPage" in script
    assert "await getLastLocationForExecution(button.dataset.executionId, button.dataset.itemId)" in script
    assert "offlineActionConfirmation" in script
    assert "window.JaciConfirm.show" in script
    assert "Removido offline" in script
    assert "Não comprado offline" in script
    assert "applyPersistedOfflineItemState" in script
    assert "clearOfflineItemIndicators" in script
    assert "clearOfflineItemIndicatorsWhenSynced" in script
    assert "pendingCount === 0" in script
    assert "badge.classList.add('d-none')" in script
    assert "snapshot.pending_operations.forEach" in script
    assert "window.addEventListener('load', function ()" in script
    assert "document.body.addEventListener('htmx:afterSwap'" in script
    assert "refreshCurrentExecutionFragments" in script
    assert "`/executions/${executionId}/items-fragment`" in script
    assert "`/executions/${executionId}/sidebar-fragment`" in script
    assert "cache: 'no-store'" in script
    assert "reconcileAppliedOperationInDom" in script
    assert "removeEmptyOfflineCategoryCard" in script
    assert "operation.action === 'remove_execution_item'" in script
    assert "operation.action !== 'incomplete_item'" in script
    assert "incompleteForm.remove()" in script
    assert "element.classList.remove('text-strikethrough')" in script
    assert "markItemRowAsOfflineUpdated" in script
    assert "is-offline-updated" in script
    assert "Comprado offline" in script
    assert "prompt(" not in script
    assert "data-offline-incomplete-item" in script
    assert "data-offline-remove-item" in script
    assert "enqueueStartExecution" in script
    assert "enqueueAddExecutionItemOperation" in script
    assert "enqueueExecutionItemOperation" in script
    assert "enqueueRemoveExecutionItemOperation" in script
    assert "enqueueFinalizeExecutionOperation" in script
    assert "createTempId" in script
    assert "is_temporary" in script
    assert "add_execution_item" in script
    assert "remove_execution_item" in script
    assert "finalize_execution" in script
    assert "offline_finalized_at" in script
    assert "offline_removed_at" in script
    assert "offline_base_version" in script
    assert "start_execution" in script
    assert "complete_item" in script
    assert "incomplete_item" in script
    assert "update_item" in script
    assert "UPDATE_ITEM" in script
    assert "credentials: 'same-origin'" in script
    assert "window.addEventListener('online'" in script
    assert "indexedDB.deleteDatabase" in script
    assert "window.location.pathname === '/auth/logout'" in script
    assert "Alterações offline ainda não são suportadas" not in script


def test_offline_queue_contract_uses_persistent_created_order_and_attempts():
    script = Path("app/static/js/offline-cache.js").read_text()

    assert "STORE_NAMES" in script
    assert "'pending_operations'" in script
    assert "created_at: created" in script
    assert "return operations.slice().sort" in script
    assert "localeCompare(String(b.created_at || ''))" in script
    assert "sortOperationsByCreation(await readStore(db, 'pending_operations'))" in script
    assert "await recordSyncAttempt(operation, false)" in script
    assert "await recordSyncAttempt(operation, requiresManualIntervention, conflict)" in script
    assert "await deleteRecord(nextDb, 'pending_operations', operation.id)" in script


def test_offline_sync_runs_automatically_manually_and_retries_failures():
    script = Path("app/static/js/offline-cache.js").read_text()

    assert "window.addEventListener('online', runAutomaticSync)" in script
    assert "window.addEventListener('load'" in script
    assert "runAutomaticSync();" in script
    assert "syncNow: runAutomaticSync" in script
    assert "runAutomaticSync({ manual: true })" in script
    assert "getNextRetryDelay().then(scheduleAutomaticRetry)" in script
    assert "window.setTimeout(function ()" in script
    assert "retryTimer = null" in script


def test_offline_sync_uses_exponential_backoff_and_only_notifies_manual_errors():
    script = Path("app/static/js/offline-cache.js").read_text()

    assert "2 ** (attempts - 1)" in script
    assert "Math.min(SYNC_RETRY_MAX_DELAY_MS" in script
    assert "status === 429 || status >= 500" in script
    assert "requiresManualIntervention = !isTransientStatus(response.status)" in script
    assert "new SyncFailure('Falha temporária de rede.', false)" in script
    assert "if (error.requiresManualIntervention)" in script
    assert "window.dispatchEvent(new CustomEvent('jaci:sync-error'))" in script
    assert "window.dispatchEvent(new CustomEvent('jaci:sync-retry-scheduled'))" in script


def test_execution_sync_handles_item_updated_event():
    script = Path("app/static/js/execution-sync.js").read_text()

    assert "case 'item_updated':" in script
    assert "_onItemUpdated" in script
    assert "Item ${data.item_id} atualizado" in script
    assert "this._refreshItems();" in script


def test_base_template_exposes_offline_cache_panel():
    base = Path("app/templates/base.html").read_text()

    assert 'id="offline-cache-panel"' in base
    assert 'id="offline-cache-summary"' in base
    assert base.index("</nav>") < base.index('id="offline-cache-panel"') < base.index("<!-- Flash Messages -->")
    assert 'id="offlineCompleteItemModal"' in base
    assert "data-offline-complete-item-modal-form" in base
    assert 'id="offlineEditItemModal"' in base
    assert "data-offline-edit-item-modal-form" in base
    assert "Compras iniciadas offline serão sincronizadas automaticamente." in base
    assert "data-bs-toggle=\"modal\"" in base
    assert "!document.querySelector(targetSelector)" in base
    assert "event.stopImmediatePropagation()" in base
    assert "/static/js/offline-cache.js" in base


def test_start_execution_forms_are_offline_capable():
    home = Path("app/templates/pages/index.html").read_text()
    detail = Path("app/templates/pages/executions/in_progress.html").read_text()

    assert "data-offline-start-execution" in home
    assert 'data-execution-id="{{ execution.id }}"' in home
    assert "data-offline-start-execution" in detail
    assert 'data-execution-id="{{ execution.id }}"' in detail


def test_add_item_form_is_offline_capable():
    detail = Path("app/templates/pages/executions/in_progress.html").read_text()

    assert "data-offline-add-item" in detail
    assert 'data-execution-id="{{ execution.id }}"' in detail
    assert 'name="name"' in detail
    assert 'name="planned_quantity"' in detail
    assert 'name="category_id"' in detail
    assert 'name="notes"' in detail


def test_finalize_controls_are_offline_capable():
    detail = Path("app/templates/pages/executions/in_progress.html").read_text()
    close = Path("app/templates/pages/executions/close_pending.html").read_text()

    assert "data-offline-finalize-link" in detail
    assert "data-offline-finalize-execution" in close
    assert 'name="action" value="discard"' in close
    assert 'name="action" value="new_execution"' in close
    assert 'name="new_date"' in close


def test_execution_item_controls_are_offline_capable():
    items = Path("app/templates/pages/executions/_items_fragment.html").read_text()
    modal = Path("app/templates/pages/executions/_complete_modal.html").read_text()
    edit_modal = Path("app/templates/pages/executions/_edit_modal.html").read_text()

    assert "data-offline-complete-item" in items
    assert "data-offline-edit-item" in items
    assert "data-offline-incomplete-item" in items
    assert "data-offline-remove-item" in items
    assert 'data-bs-toggle="modal"' not in items
    assert 'data-bs-target="#completeItemModal' not in items
    assert 'data-bs-target="#editItemModal' not in items
    assert 'hx-swap="innerHTML""' not in items
    assert "data-execution-item-row" in items
    assert "data-item-location" in items
    assert "data-item-name-label" in items
    assert "data-item-planned-quantity-label" in items
    assert "data-item-notes-label" in items
    assert "data-offline-item-badge" in items
    assert "Comprado offline" in items
    assert "data-item-completed-summary" in items
    assert "data-purchased-quantity" in items
    assert "data-unit-price" in items
    assert "data-category-id" in items
    assert "data-offline-complete-item-form" in modal
    assert 'value="{{ item.unit_price if item.unit_price else \'\' }}"' in modal
    assert "window.JaciModal.show(modalEl)" in modal
    assert "window.JaciModal.hide" in modal
    assert "bootstrap.Modal" not in modal
    assert "window.JaciModal.show(modalEl)" in edit_modal
    assert "window.JaciModal.hide" in edit_modal
    assert "bootstrap.Modal" not in edit_modal


def test_offline_item_state_is_visible_and_mobile_panel_does_not_overlay_content():
    styles = Path("app/static/css/jaci-theme.css").read_text()

    assert ".offline-item-badge" in styles
    assert ".list-group-jaci .list-group-item.is-offline-updated" in styles
    assert ".list-group-jaci .list-group-item.is-offline-removed" in styles
    assert "@media (max-width: 767.98px)" in styles
    assert ".offline-cache-panel {\n        position: static;" in styles
    assert "box-shadow: none;" in styles
