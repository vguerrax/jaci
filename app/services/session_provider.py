"""Adaptadores da sessão local para o Tupã e para o bypass de testes."""
from app.config import get_settings
from app.services.session_policy import AccessTokenExpired, SessionExpired, SessionUnavailable


class ProviderUnavailable(SessionUnavailable):
    pass


class TupaSessionProvider:
    name = 'tupa'

    def __init__(self, guard_settings=None):
        self.settings = guard_settings or get_settings()

    def check_configuration(self):
        from urllib.parse import urlsplit
        from uuid import UUID
        try:
            base = urlsplit(self.settings.tupa_url)
            UUID(self.settings.tupa_product_id)
            if (base.scheme not in {'http', 'https'} or not base.netloc
                    or not self.settings.tupa_service_token
                    or not getattr(self.settings, 'tupa_jwt_issuer', 'tupa')):
                raise ValueError()
        except (AttributeError, TypeError, ValueError):
            raise ProviderUnavailable('Configurar a integração de sessão com o Tupã.') from None

    def _post(self, path, **kwargs):
        import httpx
        self.check_configuration()
        try:
            with httpx.Client(timeout=self.settings.tupa_timeout_seconds, trust_env=False) as client:
                return client.post(self.settings.tupa_url.rstrip('/') + path, **kwargs)
        except httpx.HTTPError:
            raise ProviderUnavailable('Tupã temporariamente indisponível.') from None

    def validate(self, tokens):
        self.check_configuration()
        import time
        from uuid import UUID
        from jose import JWTError, jwt
        try:
            access = tokens['access_token']
            claims = jwt.get_unverified_claims(access)
            header = jwt.get_unverified_header(access)
            if (header.get('alg') != 'RS256' or claims.get('type') != 'access'
                    or claims.get('iss') != getattr(self.settings, 'tupa_jwt_issuer', 'tupa')
                    or UUID(claims['product_id']) != UUID(self.settings.tupa_product_id)
                    or type(claims.get('exp')) is not int):
                raise ValueError()
            UUID(claims['sub'])
            UUID(claims['jti'])
        except (JWTError, KeyError, TypeError, ValueError, AttributeError):
            raise SessionExpired('invalid_identity') from None

        response = self._post(
            '/auth/session/validate',
            headers={'X-Service-Token': self.settings.tupa_service_token},
            json={'access_token': access},
        )
        if response.status_code != 200:
            # 401 pertence à credencial do produto, não à sessão do usuário.
            raise ProviderUnavailable('Não foi possível consultar a sessão no Tupã.')
        try:
            result = response.json()
            if not isinstance(result, dict):
                raise ValueError()
            if result.get('active') is False:
                if claims['exp'] <= time.time():
                    raise AccessTokenExpired()
                raise SessionExpired('session_revoked')
            if (result.get('active') is not True or result.get('sub') != claims['sub']
                    or result.get('product_id') != claims['product_id']
                    or type(result.get('exp')) is not int or result['exp'] != claims['exp']):
                raise ValueError()
        except (ValueError, TypeError, KeyError):
            raise ProviderUnavailable('Resposta de sessão inválida no Tupã.') from None
        if claims['exp'] <= time.time():
            raise AccessTokenExpired()
        # A consulta autenticada acima prova assinatura e validade revogável
        # deste token. Os campos locais precisam coincidir com essa resposta.
        return claims

    def refresh(self, refresh_token):
        response = self._post('/auth/refresh', json={'refresh_token': refresh_token})
        if response.status_code == 401:
            raise SessionExpired('session_revoked')
        if response.status_code != 200:
            raise ProviderUnavailable('Não foi possível renovar a sessão no Tupã.')
        try:
            tokens = response.json()
            if (not isinstance(tokens, dict)
                    or any(not isinstance(tokens.get(key), str) or not tokens[key]
                           for key in ('access_token', 'refresh_token'))
                    or type(tokens.get('expires_in')) is not int
                    or not 0 < tokens['expires_in'] <= 86400
                    or str(tokens.get('token_type', 'bearer')).lower() != 'bearer'):
                raise ValueError()
            return tokens
        except (ValueError, TypeError):
            raise ProviderUnavailable('Resposta de renovação inválida no Tupã.') from None

    def logout(self, access_token):
        response = self._post(
            '/auth/logout', headers={'Authorization': f'Bearer {access_token}'},
        )
        if response.status_code not in {200, 401}:
            raise ProviderUnavailable('Não foi possível confirmar a saída no Tupã.')


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
