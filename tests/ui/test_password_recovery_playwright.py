import os

import pytest
from playwright.sync_api import expect

from tests.helpers.tupa_password_stub import INITIAL_PASSWORD
from tests.ui.fixtures.passwords import password_account
from tests.ui.helpers.playwright import PLAYWRIGHT_SKIP_MARK
from tests.ui.pages.passwords import PasswordPage
from tests.ui.pages.shopping import LoginPage, PurchasePage

pytestmark = [
    PLAYWRIGHT_SKIP_MARK,
    pytest.mark.skipif(os.environ.get("JACI_UI_PASSWORD_FLOWS") != "1",
                       reason="Use o provedor sintético de senha do runner UI."),
]


def test_recover_account_from_synthetic_email_and_login_with_new_password(page, password_account):
    flow = PasswordPage(page)
    flow.request_link()
    flow.open_link(password_account)
    flow.reset_password("new-secret-password")
    LoginPage(page).submit(password=INITIAL_PASSWORD)
    expect(page.get_by_text("E-mail ou senha incorretos.")).to_be_visible()
    LoginPage(page).login(password="new-secret-password")


def test_change_password_ends_second_device_and_preserves_offline_queue(
    page, context, browser, password_account, ui_purchase,
):
    LoginPage(page).login()
    purchase = PurchasePage(page)
    purchase.open(ui_purchase["execution"])
    page.evaluate("window.JaciOfflineCache.refresh()")
    context.set_offline(True)
    purchase.complete(ui_purchase["item"])
    page.wait_for_function("localStorage.getItem('jaci_pending_changes-'+window.JaciSession.owner)==='1'")

    other_context = browser.new_context(viewport={"width": 390, "height": 844})
    try:
        from tests.ui.helpers.assets import install_assets
        install_assets(other_context)
        other = other_context.new_page()
        LoginPage(other).login()
        page.route("**/api/offline/operations/**", lambda route: route.abort())
        context.set_offline(False)

        flow = PasswordPage(page)
        flow.change_password("wrong-password", "new-secret-password")
        expect(page.get_by_text("A senha atual está incorreta.")).to_be_visible()
        flow.change_password(INITIAL_PASSWORD, "new-secret-password")
        expect(page.get_by_text("Sua senha foi atualizada. Entre novamente.")).to_be_visible()

        LoginPage(other).goto_path("/auth/profile")
        expect(other.get_by_text("Sua sessão terminou. Entre novamente para continuar.")).to_be_visible()
        LoginPage(page).login(password="new-secret-password")
        assert len(page.evaluate("window.JaciOfflineCache.read()")["pending_operations"]) == 1
        page.unroute("**/api/offline/operations/**")
        page.evaluate("window.JaciOfflineCache.syncNow({manual:true})")
        page.wait_for_function("localStorage.getItem('jaci_pending_changes-'+window.JaciSession.owner)==='0'")
    finally:
        other_context.close()


def test_desktop_password_recovery_works_without_javascript(browser, password_account):
    from tests.ui.helpers.assets import install_assets
    context = browser.new_context(java_script_enabled=False, viewport={'width':1440, 'height':900})
    try:
        install_assets(context)
        flow = PasswordPage(context.new_page())
        flow.request_link()
        flow.open_link(password_account)
        flow.reset_password('desktop-secret-password')
    finally:
        context.close()
