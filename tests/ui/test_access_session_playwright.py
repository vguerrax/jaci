import os
from datetime import timedelta

import pytest
from playwright.sync_api import expect
from sqlalchemy import update

from app.models.access_session import AccessSession
from app.services.session_policy import utc_now
from tests.ui.helpers.data import ui_db_session
from tests.ui.helpers.playwright import PLAYWRIGHT_SKIP_MARK
from tests.ui.pages.shopping import LoginPage, PurchasePage

pytestmark = [
    PLAYWRIGHT_SKIP_MARK,
    pytest.mark.skipif(
        os.environ.get("JACI_UI_SESSION_GUARD") != "1",
        reason="Cenário da sessão persistida no runner UI isolado.",
    ),
]


def test_expired_session_preserves_purchase_for_original_account(page, context, ui_purchase):
    login = LoginPage(page)
    login.login()
    purchase = PurchasePage(page)
    purchase.open(ui_purchase["execution"])
    page.evaluate("navigator.serviceWorker.ready")
    page.wait_for_function("Boolean(navigator.serviceWorker.controller)")
    page.reload()
    page.evaluate("window.JaciOfflineCache.refresh()")
    original_owner = page.evaluate("window.JaciSession.owner")

    context.set_offline(True)
    purchase.complete(ui_purchase["item"])
    page.wait_for_function(
        "() => localStorage.getItem('jaci_pending_changes-' + window.JaciSession.owner) === '1'"
    )
    page.reload()
    page.wait_for_function("Boolean(window.JaciOfflineCache)")
    assert len(page.evaluate("window.JaciOfflineCache.read()")["pending_operations"]) == 1

    with ui_db_session() as db:
        now = utc_now()
        db.execute(update(AccessSession).values(
            authenticated_at=now - timedelta(hours=9),
            last_activity_at=now - timedelta(hours=8),
            expires_at=now,
        ))
        db.commit()

    context.set_offline(False)
    page.wait_for_function("Boolean(document.querySelector('#session-login-required:not([hidden])'))")
    expect(page.get_by_role("link", name="Entre novamente para sincronizar suas alterações.")).to_be_visible()
    assert len(page.evaluate("window.JaciOfflineCache.read()")["pending_operations"]) == 1

    login.login("outsider@example.com")
    assert page.evaluate("window.JaciSession.owner") != original_owner
    assert page.evaluate("window.JaciOfflineCache.read()")["pending_operations"] == []
    login.login()
    page.wait_for_function(
        "() => localStorage.getItem('jaci_pending_changes-' + window.JaciSession.owner) === '0'"
    )
    from app.models import ExecutionItem
    with ui_db_session() as db:
        item = db.get(ExecutionItem, ui_purchase["item"])
        assert item.is_completed and item.version == 2


def test_first_visit_opens_login_without_expiration_warning(page):
    LoginPage(page).goto_path("/")
    expect(page.locator('form[action="/auth/password-login"]')).to_be_visible()
    expect(page.get_by_text("Sua sessão terminou. Entre novamente para continuar.", exact=True)).to_have_count(0)
    assert "expired=" not in page.url
