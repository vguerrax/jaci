from contextlib import contextmanager
from uuid import uuid4


def unique_ui_name(prefix):
    return f'{prefix}-{uuid4().hex[:12]}'


@contextmanager
def ui_db_session():
    from app.database import SessionLocal
    from app.config import get_settings
    from app.testing_environment import validate_database
    validate_database(get_settings().database_url)
    with SessionLocal() as db:
        yield db
