import os
from playwright.sync_api import expect
from tests.ui.helpers.playwright import PLAYWRIGHT_SKIP_MARK
from tests.ui.pages.shopping import LoginPage,PurchasePage,TemplatePage
from tests.ui.helpers.data import ui_db_session

pytestmark=PLAYWRIGHT_SKIP_MARK


def test_login_logout_mobile(page):
    LoginPage(page).login()
    page.goto(os.environ['PLAYWRIGHT_BASE_URL']+'/auth/logout')
    response=page.request.get(os.environ['PLAYWRIGHT_BASE_URL']+'/api/offline/snapshot')
    assert response.status==401


def test_purchase_protects_linked_name_and_persists_total(page,ui_purchase):
    LoginPage(page).login()
    purchase=PurchasePage(page)
    purchase.open(ui_purchase['execution'])
    purchase.expect_linked_name_read_only(ui_purchase['item'])
    purchase.complete(ui_purchase['item'])
    page.wait_for_function('Number(localStorage.getItem("jaci_pending_changes") || 0) === 0')
    from app.models import ExecutionItem
    with ui_db_session() as db:
        item=db.get(ExecutionItem,ui_purchase['item'])
        assert item.is_completed and item.purchased_quantity==2 and item.unit_price==5.5
        assert item.name==ui_purchase['name']


def test_outsider_cannot_open_other_group_purchase(page,ui_purchase):
    LoginPage(page).login('outsider@example.com')
    page.goto(os.environ['PLAYWRIGHT_BASE_URL']+f'/executions/{ui_purchase["execution"]}')
    expect(page.get_by_text(ui_purchase['name'],exact=True)).to_have_count(0)
    assert str(ui_purchase['execution']) not in [str(e['id']) for e in
        page.request.get(os.environ['PLAYWRIGHT_BASE_URL']+'/api/offline/snapshot').json()['executions']]


def test_desktop_navigation(page):
    page.set_viewport_size({'width':1280,'height':800})
    LoginPage(page).login()
    page.goto(os.environ['PLAYWRIGHT_BASE_URL']+'/templates')
    expect(page.locator('a[href="/templates/new"]')).to_be_visible()


def test_create_template_execution_snapshot(page):
    from tests.ui.helpers.data import unique_ui_name
    from app.models import TemplateItem,ExecutionItem
    from sqlalchemy import select
    LoginPage(page).login()
    template=TemplatePage(page)
    template_id=template.create(unique_ui_name('Lista navegador'))
    name=unique_ui_name('Feijao')
    template.add_item(name)
    execution_id=template.create_execution(template_id)
    expect(page.get_by_text(name,exact=True)).to_be_visible()
    with ui_db_session() as db:
        original=db.scalar(select(TemplateItem).where(TemplateItem.template_id==template_id))
        original.name='Produto futuro'
        db.commit()
        snapshot=db.scalar(select(ExecutionItem).where(ExecutionItem.execution_id==execution_id))
        assert snapshot.name==name


def test_standalone_item_remains_renameable(page):
    from tests.ui.factories.shopping import create_purchase
    purchase=create_purchase(started=False,extra_item=True)
    LoginPage(page).login()
    PurchasePage(page).open(purchase['execution'])
    page.locator(f'[data-offline-edit-item][data-item-id="{purchase["extra"]}"]').click()
    modal=page.locator('.modal.show')
    expect(modal.locator('[name=name]')).to_be_editable()
    modal.locator('[name=name]').fill('Produto avulso alterado')
    modal.locator('button[type=submit]').click()
    expect(modal).not_to_be_visible()
    expect(page.get_by_text('Produto avulso alterado',exact=True)).to_be_visible()


def test_finishing_purchase_incorporates_only_selected_item(page):
    from tests.ui.factories.shopping import create_purchase
    from app.models import ExecutionItem,Execution
    from app.services.execution_service import complete_item
    purchase=create_purchase(extra_item=True)
    with ui_db_session() as db:
        complete_item(db,db.get(ExecutionItem,purchase['item']),2,5)
        complete_item(db,db.get(ExecutionItem,purchase['extra']),1,3)
    LoginPage(page).login()
    page.goto(os.environ['PLAYWRIGHT_BASE_URL']+f'/executions/{purchase["execution"]}/close')
    page.locator('[name=template_learning_selected][value^="new_item:"]').check()
    page.locator('button[name=action][value=discard]').click()
    page.wait_for_url('**/executions/*')
    with ui_db_session() as db:
        source=db.get(ExecutionItem,purchase['extra'])
        assert source.template_item_id is not None
        assert source.unit_price==3 and source.purchased_quantity==1
        assert db.get(Execution,purchase['execution']).status=='completed'


def test_offline_queue_survives_reload_and_reconnects_once(page,context,ui_purchase):
    from app.models import ExecutionItem
    LoginPage(page).login()
    purchase=PurchasePage(page)
    purchase.open(ui_purchase['execution'])
    page.evaluate('navigator.serviceWorker.ready')
    page.wait_for_function('Boolean(navigator.serviceWorker.controller)')
    page.reload()
    page.wait_for_function('Boolean(window.JaciOfflineCache)')
    page.evaluate('window.JaciOfflineCache.refresh()')
    context.set_offline(True)
    purchase.complete(ui_purchase['item'])
    page.wait_for_function('localStorage.getItem("jaci_pending_changes")==="1"')
    page.reload()
    page.wait_for_function('Boolean(window.JaciOfflineCache)')
    assert len(page.evaluate('window.JaciOfflineCache.read()')['pending_operations'])==1
    context.set_offline(False)
    page.evaluate('window.JaciOfflineCache.syncNow({manual:true})')
    page.wait_for_function('localStorage.getItem("jaci_pending_changes")==="0"')
    with ui_db_session() as db:
        item=db.get(ExecutionItem,ui_purchase['item'])
        assert item.is_completed and item.version==2
        assert item.purchased_quantity==2 and item.unit_price==5.5


def test_concurrent_purchase_requires_explicit_conflict_resolution(page,browser,ui_purchase):
    LoginPage(page).login()
    first=PurchasePage(page)
    first.open(ui_purchase['execution'])
    second_context=browser.new_context(viewport={'width':390,'height':844})
    try:
        from tests.ui.helpers.assets import install_assets
        install_assets(second_context)
        second=second_context.new_page()
        LoginPage(second).login('member@example.com')
        other=PurchasePage(second)
        other.open(ui_purchase['execution'])
        second_context.set_offline(True)
        other.complete(ui_purchase['item'],price='7.00')
        second.wait_for_function('localStorage.getItem("jaci_pending_changes")==="1"')
        queued=second.evaluate('window.JaciOfflineCache.read()')['pending_operations']
        assert queued[0]['payload']['version']==1
        first.complete(ui_purchase['item'])
        page.wait_for_function('localStorage.getItem("jaci_pending_changes")==="0"')
        second.evaluate("() => {\n            window.__testConflict = new Promise((resolve,reject) => {\n                const timeout=setTimeout(() => reject(new Error('Conflito não sinalizado')),30000);\n                window.addEventListener('jaci:sync-error',() => {\n                    clearTimeout(timeout); resolve(true);\n                },{once:true});\n            });\n        }")
        second_context.set_offline(False)
        second.evaluate('window.JaciOfflineCache.syncNow({manual:true})')
        second.evaluate('window.__testConflict')
        state=second.evaluate('window.JaciOfflineCache.read()')
        pending=state['pending_operations']
        assert pending and pending[0]['status']=='conflict', [
            {key:op.get(key) for key in ('status','error_message','conflict','payload')}
            for op in pending]
        second.goto(os.environ['PLAYWRIGHT_BASE_URL']+'/sync')
        second.locator('[data-sync-resolve="discard_local"]').click()
        second.wait_for_function('localStorage.getItem("jaci_pending_changes")==="0"')
        from app.models import ExecutionItem
        with ui_db_session() as db:
            item=db.get(ExecutionItem,ui_purchase['item'])
            assert item.unit_price==5.5
    finally:
        second_context.close()
