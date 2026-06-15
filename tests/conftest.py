from collections.abc import Iterator
from datetime import datetime, timezone
import os

os.environ["DEBUG"] = "false"
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Category, Group, User, group_members


@pytest.fixture
def db() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def make_user(db: Session):
    def factory(email: str, name: str | None = None) -> User:
        user = User(
            email=email,
            name=name or email.split("@")[0],
            is_profile_complete=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    return factory


@pytest.fixture
def make_group(db: Session, make_user):
    def factory(
        name: str = "Casa",
        owner: User | None = None,
        members: list[User] | None = None,
    ) -> Group:
        owner = owner or make_user(f"{name.lower()}@example.com")
        group = Group(name=name, owner_id=owner.id)
        db.add(group)
        db.flush()

        unique_members = {member.id: member for member in [owner, *(members or [])]}
        for member in unique_members.values():
            db.execute(
                group_members.insert().values(
                    user_id=member.id,
                    group_id=group.id,
                    joined_at=datetime.now(timezone.utc),
                )
            )

        db.commit()
        db.refresh(group)
        return group

    return factory


@pytest.fixture
def make_category(db: Session):
    def factory(group: Group, name: str = "Mantimentos") -> Category:
        category = Category(name=name, group_id=group.id, sort_order=0)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    return factory
