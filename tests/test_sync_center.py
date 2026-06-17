import asyncio
from pathlib import Path

from starlette.requests import Request

from app.routers.sync_center import sync_center


def make_request(path: str = "/sync") -> Request:
    return Request({"type": "http", "method": "GET", "path": path})


def test_sync_center_requires_authentication(db):
    response = asyncio.run(sync_center(make_request(), db=db, user=None, active_group=None))

    assert response.status_code == 303
    assert response.headers["location"] == "/auth/login"


def test_sync_center_renders_local_queue_management_shell(db, make_user, make_group):
    user = make_user("ana@example.com")
    group = make_group(owner=user)

    response = asyncio.run(sync_center(make_request(), db=db, user=user, active_group=group))
    body = response.body.decode()

    assert "Central de sincronização" in body
    assert "Alterações offline" in body
    assert "data-sync-center" in body
    assert "data-sync-operation-list" in body
    assert "data-sync-filter=\"pending\"" in body
    assert "data-sync-filter=\"failed\"" in body
    assert "data-sync-filter=\"conflict\"" in body
    assert "data-sync-center-sync-now" in body
    assert "Histórico de conflitos" in body
    assert "data-sync-audit-list" in body
    assert "data-sync-audit-refresh" in body


def test_sync_center_is_available_from_navigation():
    base = Path("app/templates/base.html").read_text()

    assert '<a class="dropdown-item" href="/sync">Sincronização</a>' in base
    assert "active_page == 'sync'" not in base


def test_sync_center_frontend_reads_queue_and_resolves_conflicts():
    script = Path("app/static/js/offline-cache.js").read_text()
    styles = Path("app/static/css/jaci-theme.css").read_text()

    assert "data-sync-center" in script
    assert "renderSyncCenter" in script
    assert "classifyOperation" in script
    assert "entityLabel" in script
    assert "fieldLabel" in script
    assert "fieldLabelForPayload" in script
    assert "orderedPayloadEntries" in script
    assert "operationTypeLabel" in script
    assert "resolutionLabel" in script
    assert "Valor unitário" in script
    assert "Quantidade comprada" in script
    assert "Item da compra" in script
    assert "Alterar item da compra" in script
    assert "Servidor mantido" in script
    assert "Alteração local reenviada" in script
    assert "user_name" in script
    assert "if (key === 'id' && payload?.execution_id) return 'Item';" in script
    assert "isConflictOperation" in script
    assert "buildConflict" in script
    assert "response.status === 409" in script
    assert "resolveOperation" in script
    assert "SYNC_CONFLICTS_URL" in script
    assert "recordConflictResolution" in script
    assert "renderConflictAuditHistory" in script
    assert "data-sync-audit-list" in script
    assert "data-sync-audit-refresh" in script
    assert "discard_local" in script
    assert "retry_local" in script
    assert "requires_manual_intervention: false" in script
    assert "await deleteRecord(db, 'pending_operations', operationId)" in script
    assert "if (operation.requires_manual_intervention || isConflictOperation(operation))" in script
    assert ".sync-center-stats" in styles
    assert ".sync-operation-conflict" in styles
    assert ".sync-audit-card" in styles
