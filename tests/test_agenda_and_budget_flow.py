from datetime import date, datetime, timezone

import pytest

from app.models.enums import ExecutionStatus
from app.services.agenda_service import build_calendar_data
from app.services.execution_service import check_budget_alerts, create_execution_standalone


def test_calendar_lists_group_executions_and_prioritizes_in_progress_status(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    scheduled = create_execution_standalone(
        db, group, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    in_progress = create_execution_standalone(
        db, group, datetime(2026, 6, 15, 18, tzinfo=timezone.utc), user
    )
    in_progress.status = ExecutionStatus.in_progress
    db.commit()

    calendar = build_calendar_data(db, group.id, 2026, 6, date(2026, 6, 15))
    day = next(
        item
        for week in calendar["weeks"]
        for item in week
        if item and item["day"] == 15
    )

    assert scheduled.id != in_progress.id
    assert day["count"] == 2
    assert day["indicator"] == "in_progress"
    assert day["is_today"] is True


@pytest.mark.parametrize(
    ("spent", "expected_level"),
    [(79, None), (80, "info"), (95, "warning"), (100, "danger"), (120, "danger")],
)
def test_budget_alert_thresholds(spent, expected_level):
    alerts = check_budget_alerts(spent, 100)

    assert (alerts[0]["level"] if alerts else None) == expected_level

