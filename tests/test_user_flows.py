from datetime import datetime, timezone

from app.models.enums import ExecutionStatus, RecurrenceType
from app.services.agenda_service import (
    generate_next_execution,
    get_executions_for_date,
)
from app.services.execution_service import (
    add_item_to_execution,
    complete_item,
    create_execution_from_template,
    finalize_execution,
    get_execution_totals,
    start_execution,
)
from app.services.group_service import add_member_to_group, create_group
from app.services.notification_service import (
    get_notifications,
    notify_execution_completed,
    notify_execution_started,
)
from app.services.template_service import (
    add_item_to_template,
    create_template,
    get_template_by_id,
    get_template_items_grouped,
)


def test_fl02_template_is_active_and_items_are_grouped_with_notes(
    db, make_user, make_group, make_category
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    category = make_category(group, "Mantimentos")
    template = create_template(db, group, "Mensal", RecurrenceType.monthly, 500)
    add_item_to_template(
        db,
        template,
        "Arroz",
        2,
        category.id,
        notes="Preferir pacote de 5kg",
    )

    grouped = get_template_items_grouped(db, template.id)

    assert template.is_active is True
    assert grouped[0]["category"].name == "Mantimentos"
    assert grouped[0]["items"][0].notes == "Preferir pacote de 5kg"


def test_fl03_manual_and_automatic_executions_are_available_in_agenda(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Semanal", RecurrenceType.weekly)
    add_item_to_template(db, template, "Arroz", 1)
    scheduled_date = datetime(2026, 6, 15, tzinfo=timezone.utc)

    current = create_execution_from_template(db, template, scheduled_date, user)
    assert get_executions_for_date(db, group.id, scheduled_date) == [current]

    finalize_execution(db, current)
    next_execution = generate_next_execution(db, current, user)

    assert next_execution.status == ExecutionStatus.scheduled
    assert get_executions_for_date(
        db, group.id, next_execution.scheduled_date
    ) == [next_execution]


def test_fl04_critical_purchase_flow_preserves_history(
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
    complete_item(db, execution.items[0], 2, 10)
    forgotten = add_item_to_execution(db, execution, "Feijão", unit_price=8)
    totals_before_finish = get_execution_totals(db, execution.id)
    finalize_execution(db, execution)

    assert totals_before_finish["total_spent"] == 28
    assert execution.status == ExecutionStatus.completed
    assert [(item.name, item.total_price) for item in execution.items] == [
        ("Arroz", 20),
        ("Feijão", 8),
    ]


def test_fl05_collaborative_purchase_notifies_members_and_has_single_history(
    db, make_user, make_group
):
    owner = make_user("ana@example.com", "Ana")
    member = make_user("bia@example.com", "Bia")
    group = make_group(owner=owner, members=[member])
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    add_item_to_template(db, template, "Arroz", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), owner
    )

    start_execution(db, execution)
    notify_execution_started(db, execution, owner, template.name)
    complete_item(db, execution.items[0], 1, 10)
    finalize_execution(db, execution)
    notify_execution_completed(db, execution, member, template.name, 10)

    owner_notifications = get_notifications(db, owner.id)
    member_notifications = get_notifications(db, member.id)
    assert [notification.type for notification in member_notifications] == [
        "execution_started"
    ]
    assert [notification.type for notification in owner_notifications] == [
        "execution_completed"
    ]
    assert execution.status == ExecutionStatus.completed
    assert get_execution_totals(db, execution.id)["total_spent"] == 10


def test_fl07_accepted_member_can_access_shared_templates_and_executions(
    db, make_user
):
    owner = make_user("ana@example.com")
    invited = make_user("bia@example.com")
    group = create_group(db, "Casa compartilhada", owner)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), owner
    )

    assert add_member_to_group(db, group.id, invited) is True
    assert get_template_by_id(db, template.id, invited) == template
    assert execution in invited.groups[0].executions


def test_fl08_completed_execution_remains_available_in_agenda_history(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    add_item_to_template(db, template, "Arroz", 1)
    scheduled_date = datetime(2026, 6, 15, tzinfo=timezone.utc)
    execution = create_execution_from_template(db, template, scheduled_date, user)
    complete_item(db, execution.items[0], 1, 10)
    finalize_execution(db, execution)

    history = get_executions_for_date(db, group.id, scheduled_date)

    assert history == [execution]
    assert history[0].status == ExecutionStatus.completed
    assert get_execution_totals(db, history[0].id)["total_spent"] == 10
