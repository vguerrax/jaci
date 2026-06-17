"""Contratos TDD da Sprint 4: aprendizado contínuo dos templates."""

from datetime import datetime, timezone
from importlib import import_module

import pytest

from app.models.enums import RecurrenceType
from app.services.execution_service import (
    add_item_to_execution,
    complete_item,
    create_execution_from_template,
    create_execution_standalone,
    finalize_execution,
)
from app.services.template_service import add_item_to_template, create_template


sprint4_contract = pytest.mark.xfail(
    strict=True,
    reason="Sprint 4 aguardando implementação",
)


def learning_service():
    return import_module("app.services.template_learning_service")


@sprint4_contract
def test_bl029_detects_runtime_items_only_for_template_executions(
    db, make_user, make_group
):
    learning = learning_service()
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    add_item_to_template(db, template, "Arroz", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    runtime_item = add_item_to_execution(db, execution, "Feijão", 2)
    standalone = create_execution_standalone(
        db, group, datetime(2026, 6, 16, tzinfo=timezone.utc), user
    )
    add_item_to_execution(db, standalone, "Leite", 1)
    finalize_execution(db, execution)
    finalize_execution(db, standalone)

    suggestions = learning.get_template_suggestions(db, execution)
    standalone_suggestions = learning.get_template_suggestions(db, standalone)

    assert [suggestion["type"] for suggestion in suggestions] == ["new_item"]
    assert suggestions[0]["execution_item_id"] == runtime_item.id
    assert suggestions[0]["template_id"] == template.id
    assert suggestions[0]["explanation"] == "Item adicionado durante a compra e ausente no template."
    assert standalone_suggestions == []


@sprint4_contract
def test_bl030_applies_only_selected_new_item_suggestions_to_future_executions(
    db, make_user, make_group, make_category
):
    learning = learning_service()
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    category = make_category(group, "Mantimentos")
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
                "category_id": category.id,
                "planned_quantity": 3,
            }
        ],
    )
    next_execution = create_execution_from_template(
        db, template, datetime(2026, 7, 15, tzinfo=timezone.utc), user
    )

    assert [(item.name, item.planned_quantity, item.category_id) for item in template.items] == [
        ("Feijão", 3, category.id)
    ]
    assert [item.name for item in next_execution.items] == ["Feijão"]
    assert ignored.name not in [item.name for item in template.items]


@sprint4_contract
def test_bl031_quantity_suggestions_require_recurrent_divergence(
    db, make_user, make_group
):
    learning = learning_service()
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Semanal", RecurrenceType.weekly)
    template_item = add_item_to_template(db, template, "Banana", 1)
    for day in [1, 8, 15]:
        execution = create_execution_from_template(
            db, template, datetime(2026, 6, day, tzinfo=timezone.utc), user
        )
        complete_item(db, execution.items[0], 3, 2)
        finalize_execution(db, execution)

    suggestions = learning.analyze_template_history(db, template)

    assert suggestions.quantity == [
        {
            "type": "quantity",
            "template_item_id": template_item.id,
            "current_quantity": 1,
            "suggested_quantity": 3,
            "sample_size": 3,
            "explanation": "Comprado 3x em 3 execuções recentes.",
        }
    ]


@sprint4_contract
def test_bl031_quantity_suggestions_are_not_generated_from_single_occurrence(
    db, make_user, make_group
):
    learning = learning_service()
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Semanal", RecurrenceType.weekly)
    add_item_to_template(db, template, "Banana", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 1, tzinfo=timezone.utc), user
    )
    complete_item(db, execution.items[0], 3, 2)
    finalize_execution(db, execution)

    suggestions = learning.analyze_template_history(db, template)

    assert suggestions.quantity == []


@sprint4_contract
def test_bl032_applies_quantity_suggestion_only_to_template_future_runs(
    db, make_user, make_group
):
    learning = learning_service()
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Semanal", RecurrenceType.weekly)
    template_item = add_item_to_template(db, template, "Banana", 1)
    active_execution = create_execution_from_template(
        db, template, datetime(2026, 6, 20, tzinfo=timezone.utc), user
    )

    learning.apply_template_suggestions(
        db,
        template,
        [{"type": "quantity", "template_item_id": template_item.id, "suggested_quantity": 4}],
    )
    next_execution = create_execution_from_template(
        db, template, datetime(2026, 6, 27, tzinfo=timezone.utc), user
    )

    assert template_item.planned_quantity == 4
    assert active_execution.items[0].planned_quantity == 1
    assert next_execution.items[0].planned_quantity == 4


@sprint4_contract
def test_bl033_detects_recurrent_notes_only_for_template_items(
    db, make_user, make_group
):
    learning = learning_service()
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    template_item = add_item_to_template(db, template, "Leite", 1)
    for day in [1, 8, 15]:
        execution = create_execution_from_template(
            db, template, datetime(2026, 6, day, tzinfo=timezone.utc), user
        )
        execution.items[0].notes = "Comprar sem lactose"
        finalize_execution(db, execution)

    suggestions = learning.analyze_template_history(db, template)

    assert suggestions.notes == [
        {
            "type": "notes",
            "template_item_id": template_item.id,
            "current_notes": None,
            "suggested_notes": "Comprar sem lactose",
            "sample_size": 3,
            "explanation": "Observação repetida em 3 execuções recentes.",
        }
    ]


@sprint4_contract
def test_bl034_accepts_or_rejects_note_suggestions_without_representing_ignored_ones(
    db, make_user, make_group
):
    learning = learning_service()
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    accepted_item = add_item_to_template(db, template, "Leite", 1)
    ignored_item = add_item_to_template(db, template, "Café", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    finalize_execution(db, execution)

    learning.apply_template_suggestions(
        db,
        template,
        [{"type": "notes", "template_item_id": accepted_item.id, "suggested_notes": "Sem lactose"}],
    )
    learning.dismiss_template_suggestions(
        db,
        execution,
        [{"type": "notes", "template_item_id": ignored_item.id, "suggested_notes": "Moagem grossa"}],
    )

    suggestions = learning.get_template_suggestions(db, execution)

    assert accepted_item.notes == "Sem lactose"
    assert all(
        suggestion.get("template_item_id") != ignored_item.id
        for suggestion in suggestions
    )


@sprint4_contract
def test_rnf_s4_group_can_disable_template_learning_suggestions(
    db, make_user, make_group
):
    learning = learning_service()
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    group.template_learning_enabled = False
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    add_item_to_execution(db, execution, "Item recorrente", 1)
    finalize_execution(db, execution)

    assert learning.get_template_suggestions(db, execution) == []
    assert learning.analyze_template_history(db, template).is_empty()
