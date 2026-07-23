from datetime import datetime, timezone

import pytest

from app.models import TemplateItem
from app.models.enums import ExecutionStatus, RecurrenceType
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
    added = add_item_to_execution(db, execution, "Sabão", 3)

    totals = get_execution_totals(db, execution.id)
    db.refresh(template)

    assert execution.status == ExecutionStatus.in_progress
    assert execution.current_location == "Mercado"
    assert totals == {
        "total_items": 2,
        "completed_items": 1,
        "remaining_items": 1,
        "total_spent": 25.0,
    }
    assert added.name == "Sabão"
    assert added.template_item_id is None
    assert [item.name for item in template.items] == ["Arroz"]


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
