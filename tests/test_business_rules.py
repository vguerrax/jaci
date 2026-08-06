import asyncio
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from starlette.requests import Request

from app.models import Execution, ExecutionItem
from app.models.enums import ExecutionStatus, RecurrenceType
from app.routers import executions as execution_routes
from app.services.agenda_service import generate_next_execution, reschedule_execution
from app.services.execution_service import (
    add_item_to_execution,
    complete_item,
    create_execution_from_template,
    finalize_execution,
    incomplete_item,
    remove_item_from_execution,
    start_execution,
    update_execution_item,
)
from app.services.template_service import (
    add_item_to_template,
    create_template,
    update_template_item,
)


def make_completed_execution(db, user, group):
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    add_item_to_template(db, template, "Arroz", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    item = execution.items[0]
    finalize_execution(db, execution, discard_pending=False)
    return execution, item


@pytest.mark.parametrize(
    "mutation",
    [
        lambda db, execution, item: start_execution(db, execution),
        lambda db, execution, item: complete_item(db, item, 1, 10),
        lambda db, execution, item: incomplete_item(db, item),
        lambda db, execution, item: add_item_to_execution(db, execution, "Feijão"),
        lambda db, execution, item: remove_item_from_execution(db, item),
        lambda db, execution, item: update_execution_item(
            db, item, "Arroz integral", 2, None
        ),
        lambda db, execution, item: reschedule_execution(
            db, execution, datetime(2026, 6, 20, tzinfo=timezone.utc)
        ),
    ],
)
def test_rn02_completed_execution_is_immutable(
    db, make_user, make_group, mutation
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution, item = make_completed_execution(db, user, group)

    with pytest.raises(ValueError, match="finalizada"):
        mutation(db, execution, item)


def test_rn03_recurrence_is_only_generated_after_completion(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Semanal", RecurrenceType.weekly)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )

    assert generate_next_execution(db, execution, user) is None


def test_rn08_execution_edits_never_modify_template_items(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    template_item = add_item_to_template(db, template, "Arroz", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )

    update_execution_item(
        db, execution.items[0], "Arroz", 2, None, "Comprar promoção"
    )
    db.refresh(template_item)

    assert template_item.name == "Arroz"
    assert template_item.planned_quantity == 1


def test_linked_execution_item_rejects_rename_without_partial_update(
    db, make_user, make_group, make_category
):
    user = make_user("ana-linked@example.com")
    group = make_group(owner=user)
    original_category = make_category(group, "Frutas")
    other_category = make_category(group, "Hortifruti")
    template = create_template(db, group, "Feira", RecurrenceType.weekly)
    add_item_to_template(db, template, "Maçã", 1, original_category.id)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    item = execution.items[0]
    original_version = item.version

    with pytest.raises(ValueError, match="vinculado à lista"):
        update_execution_item(
            db,
            item,
            "Manga",
            3,
            other_category.id,
            "Produto diferente",
        )

    db.refresh(item)
    assert item.name == "Maçã"
    assert item.planned_quantity == 1
    assert item.category_id == original_category.id
    assert item.notes is None
    assert item.version == original_version


def test_linked_execution_item_updates_other_fields_with_current_name(
    db, make_user, make_group, make_category
):
    user = make_user("ana-linked-fields@example.com")
    group = make_group(owner=user)
    category = make_category(group, "Hortifruti")
    template = create_template(db, group, "Feira", RecurrenceType.weekly)
    add_item_to_template(db, template, "Maçã", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    item = execution.items[0]
    original_version = item.version

    updated = update_execution_item(
        db,
        item,
        "Maçã",
        2,
        category.id,
        "Escolher maduras",
    )

    assert updated.name == "Maçã"
    assert updated.planned_quantity == 2
    assert updated.category_id == category.id
    assert updated.notes == "Escolher maduras"
    assert updated.version == original_version + 1


def test_unlinked_execution_item_remains_renameable(db, make_user, make_group):
    user = make_user("ana-unlinked@example.com")
    group = make_group(owner=user)
    execution = Execution(
        group_id=group.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.scheduled,
        created_by=user.id,
    )
    db.add(execution)
    db.flush()
    item = ExecutionItem(
        execution_id=execution.id,
        name="Maçã",
        planned_quantity=1,
    )
    db.add(item)
    db.commit()

    updated = update_execution_item(db, item, "Manga", 1, None)

    assert updated.template_item_id is None
    assert updated.name == "Manga"


def test_rn09_foreign_category_is_rejected_when_items_are_edited(
    db, make_user, make_group, make_category
):
    user = make_user("ana@example.com")
    own_group = make_group("Casa", owner=user)
    other_group = make_group("Outra")
    foreign_category = make_category(other_group)
    template = create_template(db, own_group, "Mensal", RecurrenceType.monthly)
    template_item = add_item_to_template(db, template, "Arroz", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )

    with pytest.raises(ValueError, match="grupo do template"):
        update_template_item(db, template_item, "Arroz", 1, foreign_category.id)
    with pytest.raises(ValueError, match="grupo da execução"):
        update_execution_item(
            db, execution.items[0], "Arroz", 1, foreign_category.id
        )


def test_rn12_websocket_failure_does_not_undo_persisted_api_mutation(
    db, make_user, make_group, monkeypatch
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    add_item_to_template(db, template, "Arroz", 1)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )
    item = execution.items[0]

    async def failing_broadcast(*args, **kwargs):
        raise ConnectionError("WebSocket indisponível")

    monkeypatch.setattr(execution_routes.manager, "broadcast", failing_broadcast)
    request = Request({"type": "http", "method": "POST", "path": "/"})

    with pytest.raises(ConnectionError, match="WebSocket indisponível"):
        asyncio.run(
            execution_routes.handle_complete_item(
                request=request,
                execution_id=execution.id,
                item_id=item.id,
                purchased_quantity=2,
                unit_price=10,
                location=None,
                notes=None,
                version=item.version,
                db=db,
                user=user,
                active_group=group,
            )
        )

    db.expire_all()
    stored = db.scalar(select(ExecutionItem).where(ExecutionItem.id == item.id))
    assert stored.is_completed is True
    assert stored.purchased_quantity == 2
    assert stored.unit_price == 10
