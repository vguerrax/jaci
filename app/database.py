from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import get_settings

settings = get_settings()

# Engine com configurações para SQLite (WAL + busy_timeout)
engine = create_engine(
    settings.database_url,
    connect_args={
        "check_same_thread": False,  # Necessário para FastAPI
    },
    echo= False #settings.debug,
)


# Ativa WAL mode e busy_timeout
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
    """Adiciona colunas simples introduzidas sem uma ferramenta de migração."""
    inspector = inspect(engine)

    category_columns = {column["name"] for column in inspector.get_columns("categories")}
    group_columns = {column["name"] for column in inspector.get_columns("groups")}

    with engine.begin() as connection:
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


# Dependency para injeção de sessão
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
