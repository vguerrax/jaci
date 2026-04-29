from sqlalchemy import create_engine, event
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


# Dependency para injeção de sessão
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()