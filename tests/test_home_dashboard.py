import asyncio
from datetime import datetime, timedelta, timezone

from starlette.requests import Request

from app.main import home
from app.models import ExecutionItem
from app.models.enums import ExecutionStatus, RecurrenceType
from app.services.execution_service import (
    complete_item,
    create_execution_from_template,
    create_execution_standalone,
)
from app.services.home_service import build_home_dashboard
from app.services.template_service import add_item_to_template, create_template


NOW = datetime(2026, 6, 15, 12, tzinfo=timezone.utc)


def make_request() -> Request:
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})
    request.state.unread_count = 0
    return request


def test_home_prioritizes_in_progress_purchase_over_scheduled_purchase(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    scheduled = create_execution_standalone(db, group, NOW + timedelta(hours=1), user)
    in_progress = create_execution_standalone(db, group, NOW + timedelta(days=2), user)
    in_progress.status = ExecutionStatus.in_progress
    db.commit()

    dashboard = build_home_dashboard(db, group.id, NOW)

    assert dashboard["priority"]["execution"].id == in_progress.id
    assert dashboard["priority"]["execution"].id != scheduled.id


def test_home_uses_next_scheduled_purchase_when_none_is_in_progress(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    later = create_execution_standalone(db, group, NOW + timedelta(days=2), user)
    next_execution = create_execution_standalone(
        db, group, NOW + timedelta(hours=2), user
    )

    dashboard = build_home_dashboard(db, group.id, NOW)

    assert dashboard["priority"]["execution"].id == next_execution.id
    assert dashboard["priority"]["execution"].id != later.id


def test_home_metrics_and_history_are_scoped_to_active_group(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group("Casa", owner=user)
    other_group = make_group("Outra")
    scheduled = create_execution_standalone(db, group, NOW + timedelta(days=1), user)
    db.add_all(
        [
            ExecutionItem(execution_id=scheduled.id, name="Arroz"),
            ExecutionItem(execution_id=scheduled.id, name="Feijão"),
        ]
    )
    completed = create_execution_standalone(db, group, NOW - timedelta(days=1), user)
    completed.status = ExecutionStatus.completed
    completed.finished_at = NOW - timedelta(days=1)
    completed_item = ExecutionItem(
        execution_id=completed.id,
        name="Leite",
        purchased_quantity=2,
        unit_price=5,
        is_completed=True,
    )
    db.add(completed_item)
    create_execution_standalone(db, other_group, NOW + timedelta(hours=1), other_group.owner)
    db.commit()

    dashboard = build_home_dashboard(db, group.id, NOW)

    assert dashboard["metrics"] == {
        "scheduled": 1,
        "in_progress": 0,
        "month_spent": 10,
        "pending_items": 2,
    }
    assert [item["execution"].id for item in dashboard["recent_history"]] == [
        completed.id
    ]


def test_home_alerts_are_limited_and_ordered_by_criticality(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly, budget=5)
    add_item_to_template(db, template, "Arroz", 1)
    in_progress = create_execution_from_template(db, template, NOW, user)
    in_progress.status = ExecutionStatus.in_progress
    complete_item(db, in_progress.items[0], 1, 10)
    create_execution_standalone(db, group, NOW + timedelta(hours=3), user)
    create_execution_standalone(db, group, NOW + timedelta(hours=4), user)

    alerts = build_home_dashboard(db, group.id, NOW)["alerts"]

    assert len(alerts) == 3
    assert [alert["level"] for alert in alerts[:2]] == ["danger", "warning"]


def test_home_recent_history_is_limited_to_three_completed_executions(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    for days_ago in range(5):
        execution = create_execution_standalone(
            db, group, NOW - timedelta(days=days_ago), user
        )
        execution.status = ExecutionStatus.completed
        execution.finished_at = NOW - timedelta(days=days_ago)
    db.commit()

    history = build_home_dashboard(db, group.id, NOW)["recent_history"]

    assert len(history) == 3
    assert [item["execution"].finished_at.date() for item in history] == [
        (NOW - timedelta(days=days)).date() for days in range(3)
    ]


def test_home_renders_one_touch_purchase_actions_and_global_sync_indicator(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = create_execution_standalone(db, group, NOW, user)
    execution.status = ExecutionStatus.in_progress
    db.commit()

    response = asyncio.run(home(make_request(), db, user, group))
    body = response.body.decode()

    assert f'href="/executions/{execution.id}"' in body
    assert "Continuar compra" in body
    assert 'href="/executions/new"' in body
    assert 'href="/templates/new"' in body
    assert 'id="sync-status"' in body
