"""Contratos TDD dos fluxos documentados que ainda não possuem implementação."""

from datetime import datetime, timezone
from importlib import import_module

import pytest

from app.models.enums import RecurrenceType
from app.services.execution_service import (
    add_item_to_execution,
    complete_item,
    create_execution_from_template,
    finalize_execution,
    update_execution_item,
)
from app.services.template_service import add_item_to_template, create_template


future_flow = pytest.mark.xfail(
    strict=True,
    reason="Fluxo documentado aguardando implementação",
)


@future_flow
def test_fl06_finishing_purchase_suggests_runtime_items_without_applying_them(
    db, make_user, make_group
):
    learning = import_module("app.services.template_learning_service")
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    add_item_to_execution(db, execution, "Item esquecido", 2)
    finalize_execution(db, execution)

    suggestions = learning.get_template_suggestions(db, execution)

    assert suggestions == [
        {
            "type": "new_item",
            "execution_item_id": execution.items[0].id,
            "name": "Item esquecido",
            "planned_quantity": 2,
        }
    ]
    assert template.items == []


@future_flow
def test_fl06_only_selected_suggestions_are_applied_to_template(
    db, make_user, make_group
):
    learning = import_module("app.services.template_learning_service")
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    original = add_item_to_template(db, template, "Arroz", 1, notes="Pacote pequeno")
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    update_execution_item(db, execution.items[0], "Arroz", 5, None, "Pacote grande")
    add_item_to_execution(db, execution, "Feijão", 2)
    finalize_execution(db, execution)
    suggestions = learning.get_template_suggestions(db, execution)

    learning.apply_template_suggestions(
        db,
        template,
        suggestions,
        selected_types={"quantity", "notes"},
    )

    assert [(item.name, item.planned_quantity, item.notes) for item in template.items] == [
        ("Arroz", 5, "Pacote grande")
    ]
    assert original.id == template.items[0].id


@future_flow
def test_fl08_price_history_is_scoped_by_group_and_item(db, make_user, make_group):
    history_service = import_module("app.services.history_service")
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    add_item_to_template(db, template, "Arroz", 1)
    for day, price in [(1, 10), (15, 12)]:
        execution = create_execution_from_template(
            db, template, datetime(2026, 6, day, tzinfo=timezone.utc), user
        )
        complete_item(db, execution.items[0], 1, price)
        finalize_execution(db, execution)

    history = history_service.get_price_history(db, group.id, "Arroz")

    assert [entry.unit_price for entry in history] == [10, 12]


@future_flow
def test_fl08_spending_analysis_uses_completed_executions_only(
    db, make_user, make_group
):
    history_service = import_module("app.services.history_service")
    user = make_user("ana@example.com")
    group = make_group(owner=user)

    summary = history_service.get_spending_summary(
        db,
        group.id,
        date_from=datetime(2026, 6, 1, tzinfo=timezone.utc),
        date_to=datetime(2026, 6, 30, tzinfo=timezone.utc),
    )

    assert summary.total_spent == 0
    assert summary.execution_count == 0


@future_flow
def test_fl09_offline_operation_is_queued_before_remote_sync():
    sync = import_module("app.services.sync_service")
    queue = sync.create_local_queue()

    operation = queue.enqueue(
        entity="execution_item",
        entity_id=42,
        action="complete",
        payload={"purchased_quantity": 2, "unit_price": 10, "version": 1},
    )

    assert operation.status == "pending"
    assert queue.pending() == [operation]


@future_flow
def test_fl09_reconnection_synchronizes_queued_operations_without_data_loss():
    sync = import_module("app.services.sync_service")
    queue = sync.create_local_queue()
    operation = queue.enqueue(
        entity="execution_item",
        entity_id=42,
        action="complete",
        payload={"purchased_quantity": 2, "unit_price": 10, "version": 1},
    )

    result = sync.synchronize(queue)

    assert result.applied == [operation]
    assert result.conflicts == []
    assert queue.pending() == []


@future_flow
def test_fl09_sync_conflict_requires_explicit_resolution_and_preserves_both_versions():
    sync = import_module("app.services.sync_service")
    conflict = sync.detect_conflict(
        local={"name": "Arroz integral", "version": 2},
        remote={"name": "Arroz branco", "version": 2},
    )

    assert conflict.requires_resolution is True
    assert conflict.local["name"] == "Arroz integral"
    assert conflict.remote["name"] == "Arroz branco"
    assert conflict.resolved_value is None

