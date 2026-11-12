from playwright.sync_api import expect

from tests.ui.pages.shopping import BasePage


class PasswordPage(BasePage):
    def request_link(self, email="owner@example.com"):
        self.goto_path("/auth/forgot-password")
        self.page.get_by_label("E-mail", exact=True).fill(email)
        self.page.get_by_role("button", name="Enviar link de recuperação").click()
        expect(self.page.get_by_text("Se o e-mail estiver cadastrado, você receberá as instruções para redefinir a senha.")).to_be_visible()

    def open_link(self, provider):
        link = provider.get("/_tests/outbox").json()[-1]["url"]
        self.page.goto(link)
        assert self.page.url.endswith("/auth/reset-password")
        expect(self.page.get_by_label("Nova senha", exact=True)).to_be_visible()

    def reset_password(self, password):
        self.page.get_by_label("Nova senha", exact=True).fill(password)
        self.page.get_by_label("Confirmar nova senha", exact=True).fill(password)
        self.page.get_by_role("button", name="Redefinir senha", exact=True).click()
        expect(self.page.get_by_text("Sua senha foi atualizada. Entre novamente.")).to_be_visible()

    def change_password(self, current_password, new_password):
        self.goto_path("/auth/profile")
        form = self.page.locator('form[action="/auth/profile/password"]')
        form.get_by_label("Senha atual", exact=True).fill(current_password)
        form.get_by_label("Nova senha", exact=True).fill(new_password)
        form.get_by_label("Confirmar nova senha", exact=True).fill(new_password)
        form.get_by_role("button", name="Alterar senha", exact=True).click()
