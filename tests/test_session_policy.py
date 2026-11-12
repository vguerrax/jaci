"""BL-0019: contratos escritos antes do guard; não executados pelo agente."""
from datetime import datetime, timedelta, timezone

import pytest
from app.services.session_policy import deadline, is_active, internal_return_url

NOW = datetime(2026, 11, 10, tzinfo=timezone.utc)


def test_exact_idle_boundary_and_incoherent_clock():
    last = NOW - timedelta(hours=8)
    assert not is_active(last, None, NOW)
    assert is_active(last + timedelta(microseconds=1), None, NOW)
    assert not is_active(NOW + timedelta(seconds=1), None, NOW)
    assert not is_active(NOW, NOW, NOW)
    assert deadline(NOW) == NOW + timedelta(hours=8)


@pytest.mark.parametrize('value', ['https://evil.invalid/', '//evil.invalid/', '/\\evil',
                                   '/%2fexample.invalid', '/auth/logout', '/api/offline/snapshot',
                                   '/executions/1/start', '/x\r\ny'])
def test_return_rejects_external_auth_technical_or_command(value):
    assert internal_return_url(value) == '/'


def test_return_preserves_safe_page_query_and_removes_fragment():
    assert internal_return_url('/agenda?view=month#day') == '/agenda?view=month'
