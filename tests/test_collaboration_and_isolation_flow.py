import asyncio
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from starlette.requests import Request

from app.models import ExecutionItem
from app.models.enums import RecurrenceType
from app.routers import executions as execution_routes
from app.services.category_service import get_category_by_id
from app.services.execution_service import (
    add_item_to_execution,
    create_execution_from_template,
    get_execution_by_id,
)
from app.services.template_service import (
    add_item_to_template,
    create_template,
    get_template_by_id,
)


def test_group_data_is_only_visible_to_members(
    db, make_user, make_group, make_category
):
    member = make_user("membro@example.com")
    outsider = make_user("fora@example.com")
    group = make_group(owner=member)
    category = make_category(group)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), member
    )

    assert get_template_by_id(db, template.id, member) is not None
    assert get_execution_by_id(db, execution.id, member) is not None
    assert get_category_by_id(db, category.id, member) is not None
    assert get_template_by_id(db, template.id, outsider) is None
    assert get_execution_by_id(db, execution.id, outsider) is None
    assert get_category_by_id(db, category.id, outsider) is None


def test_category_ids_from_another_group_are_rejected(
    db, make_user, make_group, make_category
):
    user = make_user("ana@example.com")
    own_group = make_group("Casa", owner=user)
    other_group = make_group("Outra")
    foreign_category = make_category(other_group)
    template = create_template(db, own_group, "Mensal", RecurrenceType.monthly)
    execution = create_execution_from_template(
        db, template, datetime(2026, 6, 15, tzinfo=timezone.utc), user
    )

    with pytest.raises(ValueError, match="grupo do template"):
        add_item_to_template(db, template, "Arroz", 1, foreign_category.id)
    with pytest.raises(ValueError, match="grupo da execução"):
        add_item_to_execution(db, execution, "Arroz", 1, foreign_category.id)


def test_stale_item_version_fails_explicitly_without_overwriting(
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
    item.name = "Arroz atualizado"
    item.version = 2
    db.commit()

    events = []

    async def fake_broadcast(execution_id, event, data, exclude=None):
        events.append((event, data))

    async def fake_fragment(request, execution_id, db, user, active_group):
        return "conflict"

    monkeypatch.setattr(execution_routes.manager, "broadcast", fake_broadcast)
    monkeypatch.setattr(execution_routes, "_get_items_fragment", fake_fragment)
    request = Request({"type": "http", "method": "POST", "path": "/"})

    response = asyncio.run(
        execution_routes.handle_update_item(
            request=request,
            execution_id=execution.id,
            item_id=item.id,
            name="Sobrescrita silenciosa",
            planned_quantity=9,
            category_id=None,
            notes=None,
            version=1,
            db=db,
            user=user,
            active_group=group,
        )
    )

    db.expire_all()
    stored = db.scalar(select(ExecutionItem).where(ExecutionItem.id == item.id))
    assert response == "conflict"
    assert stored.name == "Arroz atualizado"
    assert stored.version == 2
    assert events == [
        (
            "version_conflict",
            {
                "item_id": item.id,
                "message": "Item 'Arroz atualizado' foi alterado por outro usuário.",
            },
        )
    ]
