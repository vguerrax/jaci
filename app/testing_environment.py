"""Guardas sem efeitos colaterais para os ambientes sintéticos do Jaci."""
import json
from pathlib import Path
import tempfile

from sqlalchemy.engine import make_url

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MARKER = '.jaci-test-runtime'


def allowed_runtime(directory: Path) -> bool:
    directory = directory.resolve()
    local = PROJECT_ROOT / '.test-runtime'
    return (directory.is_relative_to(local) and directory != local) or (
        directory.is_relative_to(Path(tempfile.gettempdir()).resolve())
        and directory.name.startswith('jaci-test-')
    )


def validate_runtime(directory: Path) -> Path:
    directory = directory.resolve()
    if not allowed_runtime(directory):
        raise ValueError('Diretório fora do ambiente isolado de testes.')
    try:
        marker = json.loads((directory / MARKER).read_text())
    except (OSError, ValueError) as exc:
        raise ValueError('Marcador do ambiente isolado ausente ou inválido.') from exc
    if marker != {'kind': 'jaci-test-runtime-v1', 'root': str(directory)}:
        raise ValueError('Marcador do ambiente isolado não corresponde ao diretório.')
    return directory


def validate_database(database_url: str) -> Path:
    url = make_url(database_url)
    if url.drivername != 'sqlite' or url.query or not url.database or url.database == ':memory:':
        raise ValueError('Banco deve ser SQLite em arquivo no ambiente isolado de testes.')
    database = Path(url.database).resolve()
    validate_runtime(database.parent)
    if database.name != 'jaci.sqlite3':
        raise ValueError('Nome do banco fora do ambiente isolado de testes.')
    return database
