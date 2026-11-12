import os

import httpx
import pytest
from sqlalchemy import select

from tests.helpers.tupa_password_stub import OWNER_SUBJECT
from tests.ui.helpers.data import ui_db_session


@pytest.fixture
def password_account():
    from app.models import User
    with httpx.Client(base_url=os.environ["JACI_PASSWORD_STUB_URL"], trust_env=False) as provider:
        provider.post("/_tests/reset").raise_for_status()
        with ui_db_session() as db:
            owner = db.scalar(select(User).where(User.email == "owner@example.com"))
            owner.tupa_user_id = OWNER_SUBJECT
            db.commit()
        yield provider
