"""Adaptadores de sessão. A integração real D-01 continua fechada, sem API inventada."""
from app.config import get_settings
from app.services.session_policy import SessionExpired, SessionUnavailable


class ProviderUnavailable(SessionUnavailable):
    pass


class TupaSessionProvider:
    name = 'tupa'

    def __init__(self, guard_settings=None):
        self.settings = guard_settings

    def validate(self, tokens):
        # Assinatura JWKS não confirma revogação. Não chamar endpoint não publicado
        # e não autorizar silenciosamente só porque um access ainda não venceu.
        raise ProviderUnavailable('Contrato D-01 de validade revogável ainda não disponível.')

    def refresh(self, refresh_token):
        raise ProviderUnavailable('Integração real depende do contrato D-01 aprovado.')

    def logout(self, access_token):
        raise ProviderUnavailable('Propagação remota depende da integração D-01.')


class MockSessionProvider:
    name = 'mock'

    def validate(self, tokens):
        from app.services.test_auth_service import decode_access_token
        claims = decode_access_token(tokens['access_token'])
        if claims is None:
            raise SessionExpired('session_revoked')
        return claims

    def refresh(self, refresh_token):
        from app.services.test_auth_service import refresh
        from app.services.tupa_auth_service import TupaError
        try:
            return refresh(refresh_token)
        except TupaError as exc:
            if exc.status_code == 401:
                raise SessionExpired('session_revoked') from None
            raise ProviderUnavailable() from None

    def logout(self, access_token):
        from app.services.test_auth_service import logout
        logout(access_token)


def provider_for(settings=None):
    settings = settings or get_settings()
    return MockSessionProvider() if settings.auth_mock and settings.app_env == 'test' else TupaSessionProvider(settings)
