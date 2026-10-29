import os
import pytest

PLAYWRIGHT_SKIP_MARK = pytest.mark.skipif(
    os.environ.get('JACI_RUN_PLAYWRIGHT') != '1',
    reason='Use ENV_FILE=.env.test bash scripts/run_ui_tests.sh',
)
