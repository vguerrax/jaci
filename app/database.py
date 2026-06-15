from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import get_settings

settings = get_settings()


def create_database_engine(database_url: str, echo: bool = False) -> Engine:
    """Cria engine com ajustes específicos para SQLite ou PostgreSQL."""
    url = make_url(database_url)
    options = {
        "echo": echo,
        "pool_pre_ping": True,
    }
    if url.get_backend_name() == "sqlite":
        options["connect_args"] = {"check_same_thread": False}
    return create_engine(database_url, **options)


engine = create_database_engine(settings.database_url, echo=settings.debug)


# Ativa WAL mode e busy_timeout
if engine.dialect.name == "sqlite":
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base declarativa
class Base(DeclarativeBase):
    pass


def ensure_schema_compatibility() -> None:
    """Compatibilidade temporária para bancos SQLite anteriores ao Alembic."""
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if not inspector.has_table("users"):
        return

    category_columns = {column["name"] for column in inspector.get_columns("categories")}
    group_columns = {column["name"] for column in inspector.get_columns("groups")}
    template_item_columns = {
        column["name"] for column in inspector.get_columns("template_items")
    }
    user_columns = {column["name"] for column in inspector.get_columns("users")}

    with engine.begin() as connection:
        if "tupa_user_id" not in user_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN tupa_user_id VARCHAR(36)"))
            connection.execute(
                text("CREATE UNIQUE INDEX ix_users_tupa_user_id ON users (tupa_user_id)")
            )

        if "sort_order" not in category_columns:
            connection.execute(
                text("ALTER TABLE categories ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0")
            )
            categories = connection.execute(
                text("SELECT id, group_id FROM categories ORDER BY group_id, name, id")
            ).mappings()
            current_group_id = None
            sort_order = 0
            for category in categories:
                if category["group_id"] != current_group_id:
                    current_group_id = category["group_id"]
                    sort_order = 0
                connection.execute(
                    text("UPDATE categories SET sort_order = :sort_order WHERE id = :id"),
                    {"sort_order": sort_order, "id": category["id"]},
                )
                sort_order += 1

        if "uncategorized_first" not in group_columns:
            connection.execute(
                text(
                    "ALTER TABLE groups ADD COLUMN uncategorized_first "
                    "BOOLEAN NOT NULL DEFAULT 0"
                )
            )

        if "notes" not in template_item_columns:
            connection.execute(
                text("ALTER TABLE template_items ADD COLUMN notes VARCHAR(255)")
            )


# Dependency para injeção de sessão
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
