from pathlib import Path


def test_sync_status_supports_all_required_states():
    script = Path("app/static/js/sync-status.js").read_text()

    assert "synced:" in script
    assert "syncing:" in script
    assert "offline:" in script
    assert "error:" in script
    assert "Sincronizado" in script
    assert "Sincronizando" in script
    assert "Offline" in script
    assert "Erro de sincronização" in script
    assert "jaci_last_sync_at" in script
    assert "jaci_pending_errors" in script
    assert "jaci_pending_conflicts" in script
    assert "Última sync:" in script
    assert "erro(s)" in script
    assert "conflito(s)" in script


def test_sync_status_changes_automatically_from_browser_and_htmx_events():
    script = Path("app/static/js/sync-status.js").read_text()

    assert "window.addEventListener('online'" in script
    assert "window.addEventListener('offline'" in script
    assert "document.body.addEventListener('htmx:beforeRequest'" in script
    assert "document.body.addEventListener('htmx:afterRequest'" in script
    assert "document.body.addEventListener('htmx:sendError'" in script
    assert "document.body.addEventListener('htmx:responseError'" in script
    assert "document.body.addEventListener('htmx:timeout'" in script


def test_sync_status_exposes_public_events_for_offline_cache():
    script = Path("app/static/js/sync-status.js").read_text()
    offline_cache = Path("app/static/js/offline-cache.js").read_text()

    assert "window.JaciSyncStatus" in script
    assert "jaci:sync-start" in script
    assert "jaci:sync-success" in script
    assert "jaci:sync-error" in script
    assert "jaci:sync-retry-scheduled" in script
    assert "new CustomEvent('jaci:sync-start')" in offline_cache
    assert "new CustomEvent('jaci:sync-success')" in offline_cache
    assert "new CustomEvent('jaci:sync-error')" in offline_cache
    assert "new CustomEvent('jaci:sync-retry-scheduled')" in offline_cache
    assert "new CustomEvent('jaci:sync-manual')" in script
    assert "window.addEventListener('jaci:sync-manual'" in offline_cache


def test_sync_status_is_visible_globally_and_styled_by_state():
    base = Path("app/templates/base.html").read_text()
    styles = Path("app/static/css/jaci-theme.css").read_text()

    assert 'id="sync-status"' in base
    assert 'data-state="synced"' in base
    assert 'data-sync-now' in base
    assert 'aria-label="Sincronizar agora"' in base
    assert 'sync-status-main' in base
    assert 'sync-status-details' in base
    assert 'sync-status-last' in base
    assert 'sync-status-errors' in base
    assert 'aria-live="polite"' in base
    assert ".sync-status.is-offline" in styles
    assert ".sync-status.is-syncing" in styles
    assert ".sync-status.is-error" in styles
    assert ".sync-status-action" in styles
    assert ".sync-status-body" in styles
    assert ".sync-status-details" in styles
    assert ".sync-status-errors" in styles
    assert ".sync-conflict-panel" in styles
    assert "animation: jaci-spin" in styles
    assert "@media (max-width: 767.98px)" in styles
    assert "top: 4.75rem;" in styles
    assert "bottom: auto;" in styles
    assert "top: 7.5rem;" in styles
    assert "--jaci-harvest" not in styles
