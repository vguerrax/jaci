import asyncio
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.models import Execution, ExecutionItem
from app.models.enums import ExecutionStatus, RecurrenceType
from app.routers.offline import offline_snapshot
from app.services.offline_cache_service import build_offline_snapshot
from app.services.template_service import add_item_to_template, create_template


def test_offline_snapshot_contains_essential_read_only_data(
    db, make_user, make_group, make_category
):
    user = make_user("ana@example.com")
    group = make_group(owner=user)
    category = make_category(group, "Mantimentos")
    template = create_template(db, group, "Mensal", RecurrenceType.monthly, 500)
    item = add_item_to_template(db, template, "Arroz", 2, category.id)
    execution = Execution(
        group_id=group.id,
        template_id=template.id,
        scheduled_date=datetime(2026, 6, 15, tzinfo=timezone.utc),
        status=ExecutionStatus.in_progress,
        created_by=user.id,
    )
    db.add(execution)
    db.flush()
    db.add(
        ExecutionItem(
            execution_id=execution.id,
            name="Arroz",
            category_id=category.id,
            planned_quantity=2,
        )
    )
    db.commit()

    snapshot = build_offline_snapshot(db, user)

    assert snapshot["schema_version"] == 1
    assert snapshot["groups"] == [
        {
            "id": group.id,
            "name": "Casa",
            "owner_id": user.id,
            "uncategorized_first": False,
            "created_at": snapshot["groups"][0]["created_at"],
        }
    ]
    assert snapshot["categories"][0]["name"] == "Mantimentos"
    assert snapshot["templates"][0]["recurrence"] == "monthly"
    assert snapshot["template_items"][0]["id"] == item.id
    assert snapshot["executions"][0]["status"] == "in_progress"
    assert snapshot["execution_items"][0]["name"] == "Arroz"


def test_offline_snapshot_is_scoped_to_user_groups(db, make_user, make_group):
    user = make_user("ana@example.com")
    group = make_group("Casa", owner=user)
    other_group = make_group("Outra")
    create_template(db, group, "Minha lista", RecurrenceType.monthly)
    create_template(db, other_group, "Lista alheia", RecurrenceType.monthly)

    snapshot = build_offline_snapshot(db, user)

    assert [group["name"] for group in snapshot["groups"]] == ["Casa"]
    assert [template["name"] for template in snapshot["templates"]] == ["Minha lista"]


def test_offline_snapshot_requires_authentication(db):
    with pytest.raises(HTTPException) as error:
        asyncio.run(offline_snapshot(db=db, user=None))

    assert error.value.status_code == 401


def test_offline_cache_frontend_uses_indexeddb_and_read_only_snapshot():
    script = Path("app/static/js/offline-cache.js").read_text()

    assert "indexedDB.open" in script
    assert "'indexedDB' in window" in script
    assert "jaci-offline-cache" in script
    assert "'groups'" in script
    assert "'categories'" in script
    assert "'templates'" in script
    assert "'executions'" in script
    assert "fetch(SNAPSHOT_URL" in script
    assert "credentials: 'same-origin'" in script
    assert "window.addEventListener('online'" in script
    assert "indexedDB.deleteDatabase" in script
    assert "window.location.pathname === '/auth/logout'" in script
    assert "Alterações offline ainda não são suportadas" not in script


def test_base_template_exposes_offline_cache_panel():
    base = Path("app/templates/base.html").read_text()

    assert 'id="offline-cache-panel"' in base
    assert 'id="offline-cache-summary"' in base
    assert "Consulta local somente leitura" in base
    assert "/static/js/offline-cache.js" in base
