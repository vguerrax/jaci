"""Contratos TDD da Sprint 4: aprendizado contínuo dos templates."""

import asyncio
from datetime import datetime, timezone
from importlib import import_module
from urllib.parse import urlencode

from starlette.requests import Request

from app.routers import executions as execution_routes
from app.models.enums import ExecutionStatus, RecurrenceType
from app.services.execution_service import (
    add_item_to_execution,
    complete_item,
    create_execution_from_template,
    create_execution_standalone,
    finalize_execution,
)
from app.services.group_service import update_group_settings
from app.services.template_service import add_item_to_template, create_template


def learning_service():
    return import_module("app.services.template_learning_service")


def make_form_request(data: dict | list[tuple[str, str]]) -> Request:
    body = urlencode(data, doseq=True).encode("ascii")
    sent = False

    async def receive():
        nonlocal sent
        if sent:
            return {"type": "http.request", "body": b"", "more_body": False}
        sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/",
            "headers": [(b"content-type", b"application/x-www-form-urlencoded")],
        },
        receive,
    )
    request.state.unread_count = 0
    return request


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


def test_bl030_close_flow_applies_selected_new_item_suggestion(
    db, make_user, make_group, make_category, monkeypatch
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    category = make_category(group, "Mantimentos")
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    runtime_item = add_item_to_execution(db, execution, "Feijão", 2)

    async def fake_broadcast(*args, **kwargs):
        return None

    monkeypatch.setattr(execution_routes.manager, "broadcast", fake_broadcast)
    suggestion_id = f"new_item:{runtime_item.id}"
    request = make_form_request(
        [
            ("action", "discard"),
            ("template_learning_present", suggestion_id),
            ("template_learning_selected", suggestion_id),
            (f"category_id_{suggestion_id}", str(category.id)),
            (f"planned_quantity_{suggestion_id}", "3"),
        ]
    )

    response = asyncio.run(
        execution_routes.handle_close_execution(
            request=request,
            execution_id=execution.id,
            action="discard",
            new_date=None,
            db=db,
            user=user,
        )
    )

    db.refresh(template)
    assert response.status_code == 303
    assert [(item.name, item.planned_quantity, item.category_id) for item in template.items] == [
        ("Feijão", 3, category.id)
    ]


def test_bl030_close_page_exposes_template_learning_controls():
    template = open("app/templates/pages/executions/close_pending.html", encoding="utf-8").read()

    assert "learning_suggestions" in template
    assert "history_suggestions.quantity" in template
    assert "history_suggestions.notes" in template
    assert "history_suggestions.budget" in template
    assert 'name="template_learning_present"' in template
    assert 'name="template_learning_selected"' in template
    assert "planned_quantity_{{ suggestion.suggestion_id }}" in template
    assert "category_id_{{ suggestion.suggestion_id }}" in template
    assert "suggested_budget_{{ suggestion.suggestion_id }}" in template
    assert "Atualizar orçamento da lista" in template
    assert "As alterações afetam compras futuras." in template


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
            "suggestion_id": f"quantity:{template_item.id}:3",
            "type": "quantity",
            "template_item_id": template_item.id,
            "name": "Banana",
            "current_quantity": 1,
            "suggested_quantity": 3,
            "sample_size": 3,
            "explanation": "Comprado 3x em 3 execuções recentes.",
        }
    ]


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
            "suggestion_id": f"notes:{template_item.id}:Comprar sem lactose",
            "type": "notes",
            "template_item_id": template_item.id,
            "name": "Leite",
            "current_notes": None,
            "suggested_notes": "Comprar sem lactose",
            "sample_size": 3,
            "explanation": "Observação repetida em 3 execuções recentes.",
        }
    ]


def test_bl034_accepts_or_rejects_note_suggestions_without_representing_ignored_ones(
    db, make_user, make_group
):
    learning = learning_service()
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    accepted_item = add_item_to_template(db, template, "Leite", 1)
    ignored_item = add_item_to_template(db, template, "Café", 1)
    execution = None
    for day in [1, 8, 15]:
        execution = create_execution_from_template(
            db, template, datetime(2026, 6, day, tzinfo=timezone.utc), user
        )
        execution.items[0].notes = "Sem lactose"
        execution.items[1].notes = "Moagem grossa"
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

    suggestions = learning.analyze_template_history(db, template, execution)

    assert accepted_item.notes == "Sem lactose"
    assert all(
        suggestion.get("template_item_id") != ignored_item.id
        for suggestion in suggestions.notes
    )


def test_bl075_budget_suggestion_uses_median_from_completed_template_executions(
    db, make_user, make_group
):
    learning = learning_service()
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly, budget=500)
    budgets = [780, 800, 900]
    for index, budget in enumerate(budgets, start=1):
        execution = create_execution_from_template(
            db,
            template,
            datetime(2026, 6, index, tzinfo=timezone.utc),
            user,
            budget=budget,
        )
        finalize_execution(db, execution)

    suggestions = learning.analyze_template_history(db, template)

    assert suggestions.budget == [
        {
            "suggestion_id": f"budget:{template.id}:800",
            "type": "budget",
            "template_id": template.id,
            "current_budget": 500,
            "suggested_budget": 800,
            "sample_size": 3,
            "explanation": "Mediana de R$ 800.00 em 3 execuções finalizadas recentes.",
        }
    ]
    assert template.budget == 500


def test_bl075_budget_learning_ignores_standalone_and_unfinished_executions(
    db, make_user, make_group
):
    learning = learning_service()
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly, budget=500)

    unfinished = create_execution_from_template(
        db, template, datetime(2026, 6, 1, tzinfo=timezone.utc), user, budget=900
    )
    standalone = create_execution_standalone(
        db, group, datetime(2026, 6, 2, tzinfo=timezone.utc), user, budget=900
    )
    finalize_execution(db, standalone)

    suggestions = learning.analyze_template_history(db, template)

    assert unfinished.status == ExecutionStatus.scheduled
    assert suggestions.budget == []


def test_bl076_accepts_budget_suggestion_only_for_future_executions(
    db, make_user, make_group
):
    learning = learning_service()
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly, budget=500)
    existing_execution = create_execution_from_template(
        db, template, datetime(2026, 6, 1, tzinfo=timezone.utc), user
    )

    learning.apply_template_suggestions(
        db,
        template,
        [{"type": "budget", "template_id": template.id, "suggested_budget": 800}],
    )
    next_execution = create_execution_from_template(
        db, template, datetime(2026, 7, 1, tzinfo=timezone.utc), user
    )

    assert template.budget == 800
    assert existing_execution.budget == 500
    assert next_execution.budget == 800


def test_bl076_rejected_budget_suggestion_is_not_represented_for_same_execution(
    db, make_user, make_group
):
    learning = learning_service()
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly, budget=500)
    execution = None
    for index, budget in enumerate([780, 800, 900], start=1):
        execution = create_execution_from_template(
            db,
            template,
            datetime(2026, 6, index, tzinfo=timezone.utc),
            user,
            budget=budget,
        )
        finalize_execution(db, execution)

    learning.dismiss_template_suggestions(
        db,
        execution,
        [{"type": "budget", "template_id": template.id, "suggested_budget": 800}],
    )

    suggestions = learning.analyze_template_history(db, template, execution)

    assert suggestions.budget == []


def test_bl076_close_flow_accepts_or_rejects_budget_suggestion(
    db, make_user, make_group, monkeypatch
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly, budget=500)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 1, tzinfo=timezone.utc), user, budget=800
    )

    async def fake_broadcast(*args, **kwargs):
        return None

    monkeypatch.setattr(execution_routes.manager, "broadcast", fake_broadcast)
    suggestion_id = f"budget:{template.id}:800"
    request = make_form_request(
        [
            ("action", "discard"),
            ("template_learning_present", suggestion_id),
            ("template_learning_selected", suggestion_id),
            (f"suggested_budget_{suggestion_id}", "800"),
        ]
    )

    response = asyncio.run(
        execution_routes.handle_close_execution(
            request=request,
            execution_id=execution.id,
            action="discard",
            new_date=None,
            db=db,
            user=user,
        )
    )

    db.refresh(template)
    assert response.status_code == 303
    assert template.budget == 800


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


def test_rnf_s4_group_owner_can_disable_template_learning_setting(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)

    result = update_group_settings(
        db,
        group,
        "Casa",
        user,
        template_learning_enabled=False,
    )

    assert result == {"success": True, "message": "Configurações do grupo atualizadas."}
    assert group.name == "Casa"
    assert group.template_learning_enabled is False


def test_rnf_s4_group_detail_exposes_template_learning_setting():
    template = open("app/templates/pages/groups/detail.html", encoding="utf-8").read()

    assert 'name="template_learning_enabled"' in template
    assert "Sugerir melhorias nos templates" in template
    assert "Aprendizado dos templates" in template
