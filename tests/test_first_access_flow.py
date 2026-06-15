import asyncio

from sqlalchemy import select

from app.models import Category, Group
from app.models.category import DEFAULT_CATEGORIES
from app.services import group_service
from app.services.auth_service import get_or_create_tupa_user


def test_first_access_creates_default_home_and_categories(db):
    user = get_or_create_tupa_user(db, "tupa-user-1", "PESSOA@EXAMPLE.COM")

    group = db.scalar(select(Group).where(Group.owner_id == user.id))
    categories = db.scalars(
        select(Category)
        .where(Category.group_id == group.id)
        .order_by(Category.sort_order)
    ).all()

    assert user.email == "pessoa@example.com"
    assert group.name == "Minha Casa"
    assert user in group.members
    assert [category.name for category in categories] == [
        category["name"] for category in DEFAULT_CATEGORIES
    ]


def test_repeated_login_does_not_duplicate_default_home(db):
    first = get_or_create_tupa_user(db, "tupa-user-1", "pessoa@example.com")
    second = get_or_create_tupa_user(db, "tupa-user-1", "pessoa@example.com")

    assert first.id == second.id
    assert len(db.scalars(select(Group).where(Group.owner_id == first.id)).all()) == 1


def test_member_can_be_invited_to_the_group(db, make_user, make_group, monkeypatch):
    owner = make_user("ana@example.com")
    group = make_group(owner=owner)
    sent_messages = []

    monkeypatch.setattr(group_service, "create_magic_token", lambda email: "token")

    async def fake_send_magic_link(**message):
        sent_messages.append(message)
        return True

    monkeypatch.setattr(group_service, "send_magic_link", fake_send_magic_link)

    result = asyncio.run(
        group_service.invite_member(db, group, "FAMILIA@EXAMPLE.COM", owner)
    )

    assert result["success"] is True
    assert sent_messages == [
        {
            "email": "familia@example.com",
            "token": "token",
            "group_id": group.id,
            "group_name": group.name,
            "invited_by": owner.email,
        }
    ]
