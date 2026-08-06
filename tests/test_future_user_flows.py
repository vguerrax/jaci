"""Contratos dos fluxos documentados e dos fluxos futuros ainda pendentes."""

from datetime import datetime, timezone
from importlib import import_module

import pytest

from app.models.enums import RecurrenceType
from app.services.execution_service import (
    add_item_to_execution,
    complete_item,
    create_execution_from_template,
    finalize_execution,
)
from app.services.template_service import add_item_to_template, create_template


future_flow = pytest.mark.xfail(
    strict=True,
    reason="Fluxo documentado aguardando implementação",
)


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

    assert len(suggestions) == 1
    assert suggestions[0]["type"] == "new_item"
    assert suggestions[0]["execution_item_id"] == execution.items[0].id
    assert suggestions[0]["name"] == "Item esquecido"
    assert suggestions[0]["planned_quantity"] == 2
    assert template.items == []


def test_fl06_only_selected_suggestions_are_applied_to_template(
    db, make_user, make_group
):
    learning = import_module("app.services.template_learning_service")
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    selected = add_item_to_execution(db, execution, "Feijão", 2)
    ignored = add_item_to_execution(db, execution, "Chocolate", 1)
    finalize_execution(db, execution)
    suggestions = learning.get_template_suggestions(db, execution)

    learning.apply_template_suggestions(
        db,
        template,
        [
            {
                "suggestion_id": suggestions.by_execution_item(selected.id).id,
                "planned_quantity": 3,
            }
        ],
        execution=execution,
    )

    assert [(item.name, item.planned_quantity) for item in template.items] == [("Feijão", 3)]
    assert ignored.name not in [item.name for item in template.items]


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
