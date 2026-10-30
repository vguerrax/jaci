"""Configuração do produtor age, sem dotenv, aplicação ou conexão com banco."""

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path

from scripts.backup_artifacts import BackupError


class EncryptionConfigurationError(BackupError):
    """Configuração inválida, cujo valor não deve ser publicado em logs."""


def enabled_flag(name: str, default: str = 'false') -> bool:
    value = os.environ.get(name, default).strip().lower()
    if value not in {'true', '1', 'yes', 'on', 'false', '0', 'no', 'off'}:
        raise EncryptionConfigurationError('Flag de backup inválida.')
    return value in {'true', '1', 'yes', 'on'}


def prepare_directory(directory: Path) -> None:
    if not directory.is_absolute() or any(path.is_symlink() for path in (directory, *directory.parents)):
        raise EncryptionConfigurationError('Diretório de backup deve ser absoluto e sem links.')
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not directory.is_dir() or directory.stat().st_mode & 0o077:
        raise EncryptionConfigurationError('Preparar diretório privado (0700) antes da ativação.')


@dataclass(frozen=True)
class EncryptionSettings:
    enabled: bool = False
    directory: Path = Path('/var/backups/jaci')
    database_url: str = ''
    sslmode: str = ''
    retention_days: int = 30
    recipients: tuple[str, ...] = ()

    @property
    def recipient_id(self) -> str:
        canonical = '\n'.join(self.recipients) + '\n'
        return 'sha256:' + hashlib.sha256(canonical.encode()).hexdigest()

    @classmethod
    def from_environment(cls) -> 'EncryptionSettings':
        database = os.environ.get('DATABASE_URL', '')
        if (not enabled_flag('BACKUP_ENABLED', 'true') or database.startswith('sqlite:')
                or not enabled_flag('BACKUP_ENCRYPTION_ENABLED')):
            return cls()
        try:
            if database.startswith('postgresql+psycopg://'):
                database = database.replace('postgresql+psycopg://', 'postgresql://', 1)
            elif database.startswith('postgres://'):
                database = database.replace('postgres://', 'postgresql://', 1)
            if not database.startswith('postgresql://') or database == 'postgresql://':
                raise ValueError()
            retention = int(os.environ.get('BACKUP_RETENTION_DAYS', '30'))
            if retention < 1:
                raise ValueError()
            path = Path(os.environ['BACKUP_RECIPIENTS_FILE'])
            if (not path.is_absolute() or path.is_symlink() or not path.is_file()
                    or not 0 < path.stat().st_size <= 65536):
                raise ValueError()
            contents = path.read_text(encoding='utf-8')
            if 'AGE-SECRET-KEY-' in contents or 'PRIVATE KEY' in contents:
                raise ValueError()
            lines = [line.strip() for line in contents.splitlines()]
            recipients = tuple(sorted({line for line in lines if line and not line.startswith('#')}))
            # Só destinatários nativos públicos; sem identidades privadas ou plugins.
            # O checksum/curva são validados pelo próprio age antes do pg_dump.
            if not 1 <= len(recipients) <= 32 or any(not re.fullmatch(r'age1[0-9a-z]{58}', item) for item in recipients):
                raise ValueError()
            directory = Path(os.environ.get('BACKUP_DIR', '/var/backups/jaci'))
            if not directory.is_absolute() or any(part.is_symlink() for part in (directory, *directory.parents)):
                raise ValueError()
            return cls(True, directory, database, os.environ.get('DATABASE_SSL_MODE', ''), retention, recipients)
        except (OSError, ValueError, KeyError) as exc:
            raise EncryptionConfigurationError('Configuração criptografada inválida; conferir banco, retenção e arquivo de destinatários públicos age.') from exc
