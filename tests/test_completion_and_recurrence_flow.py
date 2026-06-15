from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.models import Execution, ExecutionItem
from app.models.enums import ExecutionStatus, RecurrenceType
from app.services.agenda_service import (
    calculate_next_date,
    generate_next_execution,
    reschedule_execution,
)
from app.services.execution_service import (
    complete_item,
    create_execution_from_pending,
    create_execution_from_template,
    create_execution_standalone,
    finalize_execution,
    get_pending_items,
)
from app.services.template_service import add_item_to_template, create_template


@pytest.mark.parametrize(
    ("current", "recurrence", "expected"),
    [
        (datetime(2026, 6, 15), RecurrenceType.daily, datetime(2026, 6, 16)),
        (datetime(2026, 6, 15), RecurrenceType.weekly, datetime(2026, 6, 22)),
        (datetime(2026, 6, 15), RecurrenceType.biweekly, datetime(2026, 6, 30)),
        (datetime(2026, 1, 31), RecurrenceType.monthly, datetime(2026, 2, 28)),
        (datetime(2024, 2, 29), RecurrenceType.yearly, datetime(2025, 2, 28)),
    ],
)
def test_supported_recurrences_calculate_the_next_cycle(
    current, recurrence, expected
):
    assert calculate_next_date(current, recurrence) == expected


def test_pending_items_can_be_carried_to_a_new_standalone_execution(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Semanal", RecurrenceType.weekly)
    add_item_to_template(db, template, "Arroz", 1)
    add_item_to_template(db, template, "Feijão", 2)
    original = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    complete_item(db, original.items[0], 1, 10)

    carried = get_pending_items(db, original.id)
    next_execution = create_execution_from_pending(
        db, original, carried, datetime(2026, 6, 16, tzinfo=timezone.utc)
    )
    finalize_execution(db, original, discard_pending=False)

    assert original.status == ExecutionStatus.completed
    assert next_execution.is_standalone is True
    assert [item.name for item in next_execution.items] == ["Feijão"]
    assert carried[0].is_deleted is True


def test_discarded_pending_items_remain_as_soft_deleted_history(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = create_execution_standalone(
        db, group, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    pending = ExecutionItem(execution_id=execution.id, name="Leite")
    db.add(pending)
    db.commit()

    finalize_execution(db, execution, discard_pending=True)

    stored = db.scalar(select(ExecutionItem).where(ExecutionItem.id == pending.id))
    assert stored is not None
    assert stored.is_deleted is True
    assert get_pending_items(db, execution.id) == []


def test_next_cycle_uses_completion_date_and_not_rescheduled_date(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Semanal", RecurrenceType.weekly)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 1, tzinfo=timezone.utc), user
    )
    reschedule_execution(db, execution, datetime(2026, 6, 10, tzinfo=timezone.utc))
    execution.finished_at = datetime(2026, 6, 12, tzinfo=timezone.utc)
    execution.status = ExecutionStatus.completed
    db.commit()

    next_execution = generate_next_execution(db, execution, user)

    assert next_execution.scheduled_date.date() == datetime(2026, 6, 19).date()


def test_standalone_execution_never_generates_recurrence(db, make_user, make_group):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = create_execution_standalone(
        db, group, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )

    assert generate_next_execution(db, execution, user) is None


def test_in_progress_execution_cannot_be_rescheduled(db, make_user, make_group):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = create_execution_standalone(
        db, group, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    execution.status = ExecutionStatus.in_progress
    db.commit()

    try:
        reschedule_execution(db, execution, datetime(2026, 6, 20, tzinfo=timezone.utc))
    except ValueError as exc:
        assert "em andamento" in str(exc)
    else:
        raise AssertionError("Execução em andamento foi reagendada")
