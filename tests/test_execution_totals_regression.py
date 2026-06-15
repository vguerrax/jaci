import asyncio
from datetime import datetime, timezone

from starlette.requests import Request

from app.models.enums import RecurrenceType
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
