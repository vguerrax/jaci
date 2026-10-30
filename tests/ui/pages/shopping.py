import os
from playwright.sync_api import expect


class BasePage:
    def __init__(self,page):
        self.page=page

    def goto_path(self,path):
        self.page.goto(os.environ['PLAYWRIGHT_BASE_URL']+path)


class LoginPage(BasePage):
    def login(self,email='owner@example.com',password='jaci-test-only'):
        self.goto_path('/auth/login')
        self.page.locator('form[action="/auth/password-login"] [name=email]').fill(email)
        self.page.locator('form[action="/auth/password-login"] [name=password]').fill(password)
        self.page.locator('form[action="/auth/password-login"] button[type=submit]').click()
        self.page.wait_for_url(os.environ['PLAYWRIGHT_BASE_URL']+'/')
        expect(self.page.get_by_text('Ambiente de testes — Autenticação simulada')).to_be_visible()


class PurchasePage(BasePage):
    def open(self,execution_id):
        self.goto_path(f'/executions/{execution_id}')
        self.page.wait_for_function('Boolean(window.JaciOfflineCache)')
        self.page.evaluate('window.JaciOfflineCache.refresh()')

    def complete(self,item_id,quantity='2',price='5.50'):
        self.page.locator(f'[data-offline-complete-item][data-item-id="{item_id}"]').click()
        modal=self.page.locator('.modal.show')
        expect(modal).to_be_visible()
        modal.locator('[name=purchased_quantity]').fill(quantity)
        modal.locator('[name=unit_price]').fill(price)
        modal.locator('button[type=submit]').click()
        expect(modal).not_to_be_visible()

    def expect_linked_name_read_only(self,item_id):
        self.page.locator(f'[data-offline-edit-item][data-item-id="{item_id}"]').click()
        modal=self.page.locator('.modal.show')
        expect(modal.locator('[name=name]')).to_have_attribute('readonly','')
        modal.get_by_role('button',name='Cancelar').click()


class TemplatePage(BasePage):
    def create(self,name):
        self.goto_path('/templates/new')
        self.page.locator('#name').fill(name)
        self.page.locator('#recurrence').select_option('weekly')
        self.page.locator('#budget').fill('100')
        self.page.get_by_role('button',name='Criar lista').click()
        self.page.wait_for_url('**/templates/*')
        return int(self.page.url.rstrip('/').split('/')[-1])

    def add_item(self,name):
        self.page.locator('[data-item-add-trigger]').click()
        modal=self.page.locator('[data-item-add-modal]')
        modal.locator('[name=name]').fill(name)
        modal.locator('[name=planned_quantity]').fill('2')
        modal.locator('button[type=submit]').click()
        expect(modal).not_to_be_visible()
        expect(self.page.get_by_text(name,exact=True)).to_be_visible()

    def create_execution(self,template_id):
        self.goto_path(f'/executions/new?template_id={template_id}')
        self.page.get_by_role('button',name='Criar compra').click()
        self.page.wait_for_url('**/executions/*')
        return int(self.page.url.rstrip('/').split('/')[-1])
