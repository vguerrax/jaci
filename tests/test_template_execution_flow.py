import asyncio
from datetime import datetime, timezone

import pytest
from starlette.requests import Request

from app.models import Execution, TemplateItem
from app.models.enums import ExecutionStatus, RecurrenceType
from app.routers import executions as execution_routes
from app.routers import templates as template_routes
from app.services.execution_service import (
    add_item_to_execution,
    complete_item,
    create_execution_from_template,
    get_execution_totals,
    remove_item_from_execution,
    start_execution,
)
from app.services.template_service import (
    add_item_to_template,
    create_template,
    update_template_item,
)


def make_template_item_request(*, htmx: bool) -> Request:
    headers = [(b"hx-request", b"true")] if htmx else []
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/templates/1/items/add",
            "headers": headers,
        }
    )
    request.state.unread_count = 0
    return request


def make_execution_item_request() -> Request:
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/executions/1/items/1/edit-form",
            "headers": [(b"hx-request", b"true")],
        }
    )
    request.state.unread_count = 0
    return request


def test_template_add_item_htmx_returns_only_the_updated_items_fragment(
    db, make_user, make_group
):
    user = make_user("ana-fragment@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Feira", RecurrenceType.weekly)

    response = asyncio.run(
        template_routes.handle_add_item(
            request=make_template_item_request(htmx=True),
            template_id=template.id,
            name="Banana",
            planned_quantity=2,
            category_id=None,
            db=db,
            user=user,
            active_group=group,
        )
    )

    body = response.body.decode()
    assert response.status_code == 200
    assert "Banana" in body
    assert "data-item-filter-row" in body
    assert "<!DOCTYPE html>" not in body
    assert "data-item-add-modal" not in body


def test_linked_execution_item_edit_form_keeps_name_read_only(
    db, make_user, make_group
):
    user = make_user("ana-linked-form@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Feira", RecurrenceType.weekly)
    add_item_to_template(db, template, "Maçã", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    item = execution.items[0]

    response = asyncio.run(
        execution_routes.edit_item_form(
            request=make_execution_item_request(),
            execution_id=execution.id,
            item_id=item.id,
            db=db,
            user=user,
            active_group=group,
        )
    )

    body = response.body.decode()
    assert response.status_code == 200
    assert 'name="name" value="Maçã" required readonly' in body
    assert "Para comprar outro produto, remova este item e adicione o correto." in body


def test_unlinked_execution_item_edit_form_keeps_name_editable(
    db, make_user, make_group
):
    user = make_user("ana-unlinked-form@example.com")
    group = make_group(owner=user)
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.scheduled,
        created_by=user.id,
    )
    db.add(execution)
    db.flush()
    item = add_item_to_execution(db, execution, "Maçã")

    response = asyncio.run(
        execution_routes.edit_item_form(
            request=make_execution_item_request(),
            execution_id=execution.id,
            item_id=item.id,
            db=db,
            user=user,
            active_group=group,
        )
    )

    body = response.body.decode()
    name_input = body.split('name="name"', 1)[1].split(">", 1)[0]
    assert response.status_code == 200
    assert "readonly" not in name_input
    assert "Para comprar outro produto" not in body


def test_template_add_item_without_htmx_keeps_post_redirect_fallback(
    db, make_user, make_group
):
    user = make_user("ana-fallback@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Feira", RecurrenceType.weekly)

    response = asyncio.run(
        template_routes.handle_add_item(
            request=make_template_item_request(htmx=False),
            template_id=template.id,
            name="Banana",
            planned_quantity=2,
            category_id=None,
            db=db,
            user=user,
            active_group=group,
        )
    )

    assert response.status_code == 303
    assert response.headers["location"] == f"/templates/{template.id}"


def test_template_add_item_htmx_error_retargets_modal_feedback_without_mutation(
    db, make_user, make_group
):
    user = make_user("ana-error@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Feira", RecurrenceType.weekly)

    response = asyncio.run(
        template_routes.handle_add_item(
            request=make_template_item_request(htmx=True),
            template_id=template.id,
            name="   ",
            planned_quantity=2,
            category_id=0,
            db=db,
            user=user,
            active_group=group,
        )
    )

    assert response.status_code == 200
    assert response.headers["hx-retarget"] == "#templateItemAddFeedback"
    assert response.headers["x-jaci-item-add-error"] == "true"
    assert "O nome do item" in response.body.decode()
    assert template.items == []


def test_template_detail_renders_modal_and_fragment_as_a_complete_page(
    db, make_user, make_group
):
    user = make_user("ana-detail@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Feira", RecurrenceType.weekly)
    add_item_to_template(db, template, "Banana", 2)

    response = asyncio.run(
        template_routes.template_detail(
            request=make_template_item_request(htmx=False),
            template_id=template.id,
            db=db,
            user=user,
            active_group=group,
        )
    )

    body = response.body.decode()
    assert response.status_code == 200
    assert body.count("data-item-add-form") == 1
    assert 'id="template-items-container"' in body
    assert "Banana" in body


def test_execution_is_a_snapshot_and_template_changes_only_affect_future_runs(
    db, make_user, make_group, make_category
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    category = make_category(group)
    template = create_template(db, group, "Feira", RecurrenceType.weekly, budget=200)
    template_item = add_item_to_template(db, template, "Banana", 2, category.id)

    first = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    update_template_item(db, template_item, "Banana prata", 4, category.id)
    second = create_execution_from_template(
        db, template, datetime(2026, 6, 22, tzinfo=timezone.utc), user
    )

    assert first.budget == 200
    assert [(item.name, item.planned_quantity) for item in first.items] == [("Banana", 2)]
    assert first.items[0].template_item_id == template_item.id
    assert [(item.name, item.planned_quantity) for item in second.items] == [
        ("Banana prata", 4)
    ]


def test_template_notes_are_copied_without_linking_future_execution_edits(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    template_item = add_item_to_template(
        db, template, "Arroz", 1, notes="Preferir pacote de 5kg"
    )
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )

    execution.items[0].notes = "Marca indisponível"
    db.commit()
    db.refresh(template_item)

    assert execution.items[0].notes == "Marca indisponível"
    assert template_item.notes == "Preferir pacote de 5kg"


def test_execution_budget_can_override_template_budget(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly, budget=500)

    execution = create_execution_from_template(
        db,
        template,
        datetime(2026, 6, 15, tzinfo=timezone.utc),
        user,
        budget=650,
    )

    assert execution.budget == 650
    assert template.budget == 500


def test_purchase_flow_tracks_values_and_does_not_add_runtime_items_to_template(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    add_item_to_template(db, template, "Arroz", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )

    start_execution(db, execution)
    complete_item(db, execution.items[0], 2, 12.50, location="Mercado")
    added = add_item_to_execution(db, execution, "Sabão", 3, unit_price=5)

    totals = get_execution_totals(db, execution.id)
    db.refresh(template)

    assert execution.status == ExecutionStatus.in_progress
    assert execution.current_location == "Mercado"
    assert totals == {
        "total_items": 2,
        "completed_items": 2,
        "remaining_items": 0,
        "total_spent": 40.0,
    }
    assert added.name == "Sabão"
    assert added.planned_quantity == 3
    assert added.purchased_quantity == 3
    assert added.unit_price == 5
    assert added.is_completed is True
    assert added.version == 1
    assert added.template_item_id is None
    assert [item.name for item in template.items] == ["Arroz"]


def test_scheduled_execution_adds_pending_item_without_financial_data(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )

    item = add_item_to_execution(db, execution, "Feijão", 2)

    assert item.planned_quantity == 2
    assert item.purchased_quantity is None
    assert item.unit_price is None
    assert item.is_completed is False


@pytest.mark.parametrize("unit_price", [None, 0, -1])
def test_in_progress_execution_requires_positive_unit_price_for_new_item(
    db, make_user, make_group, unit_price
):
    user = make_user(f"ana-{unit_price}@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    start_execution(db, execution)

    with pytest.raises(ValueError, match="Valor unitário"):
        add_item_to_execution(
            db,
            execution,
            "Feijão",
            2,
            unit_price=unit_price,
        )

    assert execution.items == []


def test_cancelled_execution_rejects_new_item(db, make_user, make_group):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    execution.status = ExecutionStatus.cancelled
    db.commit()

    with pytest.raises(ValueError, match="cancelada"):
        add_item_to_execution(db, execution, "Feijão", 1, unit_price=8)

    assert execution.items == []


def test_completed_item_cannot_be_removed(db, make_user, make_group):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    add_item_to_template(db, template, "Arroz", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    complete_item(db, execution.items[0], 1, 10)

    with pytest.raises(ValueError, match="item já concluído"):
        remove_item_from_execution(db, execution.items[0])
