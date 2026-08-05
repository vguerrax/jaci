import asyncio
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from starlette.requests import Request

from app.models import Notification
from app.models.execution import Execution
from app.models.enums import ExecutionStatus, RecurrenceType
from app.routers import executions as execution_routes
from app.services.execution_service import (
    create_execution_from_template,
    create_execution_standalone,
    get_execution_display_name,
    update_scheduled_execution,
)
from app.services.offline_cache_service import build_offline_snapshot
from app.services.template_service import add_item_to_template, create_template
from app.utils.datetime import to_local


def make_request() -> Request:
    request = Request({"type": "http", "method": "POST", "path": "/"})
    request.state.unread_count = 0
    return request


def test_standalone_execution_can_be_created_with_normalized_name(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)

    execution = create_execution_standalone(
        db,
        group,
        datetime(2026, 6, 15, tzinfo=timezone.utc),
        user,
        name="  Feira de sábado  ",
    )

    assert execution.template_id is None
    assert execution.name == "Feira de sábado"
    assert get_execution_display_name(execution) == "Feira de sábado"


@pytest.mark.parametrize("name", [None, "", "   "])
def test_standalone_execution_name_uses_legacy_fallback(
    db, make_user, make_group, name
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)

    execution = create_execution_standalone(
        db,
        group,
        datetime(2026, 6, 15, tzinfo=timezone.utc),
        user,
        name=name,
    )

    assert execution.name == "Compra Avulsa"


def test_standalone_execution_name_over_limit_fails_without_persistence(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)

    with pytest.raises(ValueError, match="no máximo 150 caracteres"):
        create_execution_standalone(
            db,
            group,
            datetime(2026, 6, 15, tzinfo=timezone.utc),
            user,
            name="A" * 151,
        )

    assert db.scalars(select(Execution)).all() == []


def test_standalone_scheduled_execution_can_edit_name_date_and_budget(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = create_execution_standalone(
        db,
        group,
        datetime(2026, 6, 15, tzinfo=timezone.utc),
        user,
    )

    update_scheduled_execution(
        db,
        execution,
        "Compra do fim de semana",
        datetime(2026, 6, 20, tzinfo=timezone.utc),
        850,
    )

    assert execution.name == "Compra do fim de semana"
    assert execution.scheduled_date.date() == datetime(2026, 6, 20).date()
    assert execution.budget == 850


def test_template_execution_can_edit_date_and_budget_without_renaming(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(
        db,
        group,
        "Compra Mensal",
        RecurrenceType.monthly,
        budget=500,
    )
    add_item_to_template(db, template, "Arroz", 1)
    execution = create_execution_from_template(
        db,
        template,
        datetime(2026, 6, 15, tzinfo=timezone.utc),
        user,
    )

    update_scheduled_execution(
        db,
        execution,
        "Compra Mensal",
        datetime(2026, 6, 20, tzinfo=timezone.utc),
        850,
    )

    db.refresh(template)
    assert execution.name == "Compra Mensal"
    assert get_execution_display_name(execution) == "Compra Mensal"
    assert execution.scheduled_date.date() == datetime(2026, 6, 20).date()
    assert execution.budget == 850
    assert template.name == "Compra Mensal"
    assert template.budget == 500
    assert template.recurrence == RecurrenceType.monthly


@pytest.mark.parametrize("is_standalone", [False, True])
def test_template_execution_cannot_be_renamed_without_partial_update(
    db, make_user, make_group, is_standalone
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(
        db,
        group,
        "Compra Mensal",
        RecurrenceType.monthly,
        budget=500,
    )
    execution = create_execution_from_template(
        db,
        template,
        datetime(2026, 6, 15, tzinfo=timezone.utc),
        user,
        is_standalone=is_standalone,
    )

    with pytest.raises(ValueError, match="Apenas compras avulsas sem lista"):
        update_scheduled_execution(
            db,
            execution,
            "Nome adulterado",
            datetime(2026, 6, 20, tzinfo=timezone.utc),
            850,
        )

    db.refresh(execution)
    assert execution.name == "Compra Mensal"
    assert execution.scheduled_date.date() == datetime(2026, 6, 15).date()
    assert execution.budget == 500


def test_historical_template_execution_name_is_preserved_but_locked(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)
    execution = create_execution_from_template(
        db,
        template,
        datetime(2026, 6, 15, tzinfo=timezone.utc),
        user,
    )
    execution.name = "Nome histórico"
    db.commit()

    update_scheduled_execution(
        db,
        execution,
        "Nome histórico",
        datetime(2026, 6, 20, tzinfo=timezone.utc),
        700,
    )

    assert execution.name == "Nome histórico"
    assert template.name == "Mensal"
    assert execution.scheduled_date.date() == datetime(2026, 6, 20).date()
    assert execution.budget == 700


@pytest.mark.parametrize(
    "status",
    [ExecutionStatus.in_progress, ExecutionStatus.completed, ExecutionStatus.cancelled],
)
def test_non_scheduled_execution_cannot_be_edited(db, make_user, make_group, status):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = create_execution_from_template(
        db,
        create_template(db, group, "Semanal", RecurrenceType.weekly),
        datetime(2026, 6, 15, tzinfo=timezone.utc),
        user,
    )
    execution.status = status
    db.commit()

    with pytest.raises(ValueError, match="Apenas execuções agendadas"):
        update_scheduled_execution(
            db,
            execution,
            "Não deve salvar",
            datetime(2026, 6, 20, tzinfo=timezone.utc),
            100,
        )


def test_update_execution_route_notifies_members_and_broadcasts_change(
    db, make_user, make_group, monkeypatch
):
    owner = make_user("ana@example.com", "Ana")
    member = make_user("bia@example.com", "Bia")
    group = make_group(owner=owner, members=[member])
    execution = create_execution_standalone(
        db,
        group,
        datetime(2026, 6, 15, tzinfo=timezone.utc),
        owner,
        budget=300,
        name="Compra antiga",
    )
    events = []

    async def fake_broadcast(execution_id, event, data, exclude=None):
        events.append((execution_id, event, data))

    monkeypatch.setattr(execution_routes.manager, "broadcast", fake_broadcast)

    response = asyncio.run(
        execution_routes.handle_update_execution(
            execution_id=execution.id,
            name="Compra do Mês",
            scheduled_date="2026-06-30",
            budget="850.50",
            db=db,
            user=owner,
        )
    )

    db.refresh(execution)
    notification = db.scalar(
        select(Notification).where(Notification.user_id == member.id)
    )
    assert response.status_code == 303
    assert response.headers["location"] == f"/executions/{execution.id}?updated=1"
    assert execution.name == "Compra do Mês"
    scheduled_local = to_local(execution.scheduled_date)
    assert scheduled_local.date().isoformat() == "2026-06-30"
    assert scheduled_local.hour == 0
    assert execution.budget == 850.50
    assert notification is not None
    assert notification.type == "execution_updated"
    assert "Compra do Mês" in notification.message
    assert events == [
        (
            execution.id,
            "execution_updated",
            {
                "execution_id": execution.id,
                "name": "Compra do Mês",
                "scheduled_date": "2026-06-30",
                "budget": 850.50,
                "user_email": owner.email,
            },
        )
    ]


def test_update_execution_route_rejects_template_rename_without_partial_update(
    db, make_user, make_group, monkeypatch
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(
        db,
        group,
        "Compra Mensal",
        RecurrenceType.monthly,
        budget=500,
    )
    execution = create_execution_from_template(
        db,
        template,
        datetime(2026, 6, 15, tzinfo=timezone.utc),
        user,
    )
    events = []

    async def fake_broadcast(execution_id, event, data, exclude=None):
        events.append((execution_id, event, data))

    monkeypatch.setattr(execution_routes.manager, "broadcast", fake_broadcast)

    response = asyncio.run(
        execution_routes.handle_update_execution(
            execution_id=execution.id,
            name="Nome adulterado",
            scheduled_date="2026-06-30",
            budget="850",
            db=db,
            user=user,
        )
    )

    db.refresh(execution)
    assert response.status_code == 303
    assert response.headers["location"] == f"/executions/{execution.id}"
    assert execution.name == "Compra Mensal"
    assert execution.scheduled_date.date().isoformat() == "2026-06-15"
    assert execution.budget == 500
    assert events == []


def test_create_execution_route_preserves_local_form_date(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    template = create_template(db, group, "Mensal", RecurrenceType.monthly)

    response = asyncio.run(
        execution_routes.handle_create_execution(
            request=make_request(),
            template_id=template.id,
            scheduled_date="2026-06-30",
            budget=None,
            is_standalone=False,
            name="Nome adulterado",
            db=db,
            user=user,
            active_group=group,
        )
    )

    db.refresh(template)
    execution = template.executions[0]
    scheduled_local = to_local(execution.scheduled_date)
    assert response.status_code == 303
    assert execution.name == "Mensal"
    assert scheduled_local.date().isoformat() == "2026-06-30"
    assert scheduled_local.hour == 0
    assert scheduled_local.minute == 0


def test_create_standalone_route_persists_custom_name(db, make_user, make_group):
    user = make_user("ana@example.com")
    group = make_group(owner=user)

    response = asyncio.run(
        execution_routes.handle_create_execution(
            request=make_request(),
            template_id=0,
            scheduled_date="2026-06-30",
            budget=250,
            is_standalone=False,
            name="  Feira de sábado  ",
            db=db,
            user=user,
            active_group=group,
        )
    )

    execution = db.scalar(select(Execution))
    assert response.status_code == 303
    assert response.headers["location"] == f"/executions/{execution.id}"
    assert execution.name == "Feira de sábado"


def test_create_standalone_route_preserves_values_on_invalid_name(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)

    response = asyncio.run(
        execution_routes.handle_create_execution(
            request=make_request(),
            template_id=0,
            scheduled_date="2026-06-30",
            budget=250,
            is_standalone=False,
            name="A" * 151,
            db=db,
            user=user,
            active_group=group,
        )
    )

    body = response.body.decode()
    assert response.status_code == 400
    assert "Nome da execução deve ter no máximo 150 caracteres." in body
    assert "A" * 151 in body
    assert 'value="2026-06-30"' in body
    assert 'value="250"' in body
    assert db.scalars(select(Execution)).all() == []


def test_offline_snapshot_contains_edited_standalone_execution_name(
    db, make_user, make_group
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    execution = create_execution_standalone(
        db,
        group,
        datetime(2026, 6, 15, tzinfo=timezone.utc),
        user,
    )
    update_scheduled_execution(
        db,
        execution,
        "Compra Renomeada",
        datetime(2026, 6, 18, tzinfo=timezone.utc),
        None,
    )

    snapshot = build_offline_snapshot(db, user)

    assert snapshot["executions"][0]["name"] == "Compra Renomeada"
    assert snapshot["executions"][0]["scheduled_date"].startswith("2026-06-18")


def test_scheduled_execution_edit_interface_is_available_only_for_scheduled():
    creation = open("app/templates/pages/executions/create.html", encoding="utf-8").read()
    detail = open("app/templates/pages/executions/in_progress.html", encoding="utf-8").read()
    sync = open("app/static/js/execution-sync.js", encoding="utf-8").read()
    styles = open("app/static/css/jaci-theme.css", encoding="utf-8").read()

    assert "{% if execution.status == 'scheduled' %}" in detail
    assert "flex-column flex-sm-row" in detail
    assert "execution-detail-actions" in detail
    assert "Editar compra" in detail
    assert 'id="editExecutionModal"' in detail
    assert 'action="/executions/{{ execution.id }}/edit"' in detail
    assert "{% if not execution.template_id %}" in detail
    assert 'data-execution-name-readonly' in detail
    assert 'type="hidden" name="name"' in detail
    assert 'name="name"' in detail
    assert 'name="scheduled_date"' in detail
    assert 'name="budget"' in detail
    assert "Alterações salvas são sincronizadas para o grupo." in detail
    assert ".execution-detail-actions > *" in styles
    assert ".execution-detail-actions form > .btn" in styles
    assert "case 'execution_updated'" in sync
    assert "_onExecutionUpdated" in sync
    assert "{% if not template %}" in creation
    assert 'for="execution_name"' in creation
    assert 'id="execution_name" name="name"' in creation
    assert 'maxlength="150"' in creation
    assert "Nome da compra (opcional)" in creation
