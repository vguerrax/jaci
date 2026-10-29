"""Seed idempotente permitido exclusivamente no banco sintético marcado."""
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import select

from app.config import get_settings
from app.testing_environment import validate_database

ACCOUNTS = ('owner', 'member', 'outsider')


def seed() -> None:
    settings = get_settings()
    if settings.app_env != 'test' or not settings.auth_mock:
        raise ValueError('Seed exige ambiente isolado com AUTH_MOCK.')
    validate_database(settings.database_url)
    from app.database import SessionLocal
    from app.models import User, Group, group_members, Category

    with SessionLocal() as db:
        users = {}
        for name in ACCOUNTS:
            email = f'{name}@example.com'
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                user = User(email=email, name=name.title(), is_profile_complete=True,
                            tupa_user_id=str(uuid5(NAMESPACE_URL, 'jaci-test:'+email)))
                db.add(user)
                db.flush()
            users[name] = user
        for title, owner, members in [('Casa A','owner',('owner','member')),
                                      ('Casa B','outsider',('outsider',))]:
            group = db.scalar(select(Group).where(Group.name==title, Group.owner_id==users[owner].id))
            if group is None:
                group = Group(name=title, owner_id=users[owner].id)
                db.add(group)
                db.flush()
                db.add(Category(name='Mantimentos', group_id=group.id, sort_order=0))
            for member in members:
                exists = db.scalar(select(group_members.c.user_id).where(
                    group_members.c.group_id==group.id, group_members.c.user_id==users[member].id))
                if exists is None:
                    db.execute(group_members.insert().values(group_id=group.id,user_id=users[member].id))
        db.commit()


if __name__ == '__main__':
    seed()
