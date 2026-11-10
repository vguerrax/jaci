"""Remove registros de sessão além da retenção técnica, no ambiente selecionado."""
from app.config import get_settings
from app.database import SessionLocal
from app.services.access_session_service import prune_sessions


def main() -> None:
    if not get_settings().session_guard_enabled:
        raise SystemExit("A sessão persistida precisa estar habilitada.")
    with SessionLocal() as db:
        removed = prune_sessions(db)
    print(f"Registros de sessão removidos: {removed}")


if __name__ == "__main__":
    main()
