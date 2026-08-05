import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from starlette.requests import Request

from app.models import Execution, ExecutionItem
from app.models.enums import ExecutionStatus, RecurrenceType
from app.routers import executions as execution_routes
from app.services.execution_service import (
    complete_item,
    create_execution_from_template,
    incomplete_item,
)
from app.services.template_service import add_item_to_template, create_template


def make_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
        }
    )


def test_item_mutation_fragment_refreshes_sidebar_with_current_total(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    add_item_to_template(db, template, "Arroz", 1)
    add_item_to_template(db, template, "Leite", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    complete_item(db, execution.items[0], 1, 10)
    complete_item(db, execution.items[1], 1, 2.28)
    incomplete_item(db, execution.items[1])

    response = asyncio.run(
        execution_routes._get_items_fragment(
            make_request(), execution.id, db, user, group
        )
    )
    body = response.body.decode()

    assert 'id="sidebar-container" hx-swap-oob="innerHTML"' in body
    assert "R$ 10.00" in body
    assert "R$ 12.28" not in body


def test_total_spent_matches_sum_of_visible_item_totals(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Feira", RecurrenceType.weekly)
    add_item_to_template(db, template, "Tomate", 1)
    add_item_to_template(db, template, "Batata", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    complete_item(db, execution.items[0], 0.333, 1)
    complete_item(db, execution.items[1], 0.333, 1)

    visible_sum = round(sum(item.total_price for item in execution.items), 2)
    totals = execution_routes.get_execution_totals(db, execution.id)

    assert totals["total_spent"] == visible_sum


def test_add_item_route_persists_purchase_before_totals_and_broadcast(
    db, make_user, make_group, monkeypatch
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        budget=20,
        created_by=user.id,
    )
    db.add(execution)
    db.commit()
    events = []

    async def fake_broadcast(execution_id, event, data, exclude=None):
        stored = db.scalar(
            select(ExecutionItem).where(
                ExecutionItem.execution_id == execution_id,
                ExecutionItem.name == "Banana",
            )
        )
        assert stored is not None
        assert stored.is_completed is True
        assert stored.total_price == 18
        events.append((event, data))

    async def fake_fragment(*args, **kwargs):
        totals = execution_routes.get_execution_totals(db, execution.id)
        assert totals == {
            "total_items": 1,
            "completed_items": 1,
            "remaining_items": 0,
            "total_spent": 18,
        }
        return "fragment"

    monkeypatch.setattr(execution_routes.manager, "broadcast", fake_broadcast)
    monkeypatch.setattr(execution_routes, "_get_items_fragment", fake_fragment)

    response = asyncio.run(
        execution_routes.handle_add_item(
            request=make_request(),
            execution_id=execution.id,
            name="Banana",
            planned_quantity=3,
            unit_price=6,
            category_id=None,
            notes="Prata",
            db=db,
            user=user,
            active_group=group,
        )
    )

    assert response == "fragment"
    assert [event for event, _ in events] == ["item_added", "budget_alert"]
    assert events[0][1]["total_price"] == 18


def test_execution_add_item_htmx_error_stays_in_modal_without_mutation(
    db, make_user, make_group
):
    user = make_user("ana-modal-error@example.com")
    group = make_group(owner=user)
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        created_by=user.id,
    )
    db.add(execution)
    db.commit()
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": f"/executions/{execution.id}/items/add",
            "headers": [(b"hx-request", b"true")],
        }
    )

    response = asyncio.run(
        execution_routes.handle_add_item(
            request=request,
            execution_id=execution.id,
            name="   ",
            planned_quantity=1,
            unit_price=5,
            category_id=0,
            notes=None,
            db=db,
            user=user,
            active_group=group,
        )
    )

    assert response.status_code == 200
    assert response.headers["hx-retarget"] == "#executionItemAddFeedback"
    assert response.headers["x-jaci-item-add-error"] == "true"
    assert "O nome do item" in response.body.decode()
    assert execution.items == []
