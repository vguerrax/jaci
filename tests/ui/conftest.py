import os

import pytest


def pytest_collection_modifyitems(items):
    if os.environ.get('JACI_RUN_PLAYWRIGHT') != '1':
        for item in items:
            if '/ui/' in str(item.path):
                item.add_marker(pytest.mark.skip(reason='Execute pelo runner UI isolado.'))


@pytest.fixture(scope='session')
def browser_context_args(browser_context_args):
    return {**browser_context_args, 'viewport':{'width':390,'height':844},
            'locale':'pt-BR','timezone_id':'America/Sao_Paulo'}


@pytest.fixture(autouse=True)
def only_synthetic_environment():
    if os.environ.get('JACI_RUN_PLAYWRIGHT') != '1':
        pytest.skip('Use o runner UI.')
    from app.config import get_settings
    from app.testing_environment import validate_database
    settings=get_settings()
    assert settings.app_env=='test' and settings.auth_mock
    validate_database(settings.database_url)


@pytest.fixture
def ui_purchase():
    from tests.ui.factories.shopping import create_purchase
    return create_purchase()


@pytest.fixture(autouse=True)
def pinned_browser_assets(context):
    from tests.ui.helpers.assets import install_assets
    install_assets(context)
