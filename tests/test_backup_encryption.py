"""Contratos BL-0009 escritos antes do pipeline; execução dispensada pelo usuário."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import textwrap
import time
from datetime import datetime, timedelta, timezone

import pytest

from scripts.backup_artifacts import Artifact, BackupError
from scripts.backup_encryption import EncryptionSettings, EncryptionConfigurationError
from scripts.backup_pipeline import create_backup, prune_encrypted

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def synthetic_tools(tmp_path, monkeypatch):
    """Executáveis descartáveis: verificam fluxo/processos, não criptografia real."""
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    configuration = bin_dir / 'configuration.json'
    configuration.write_text('{}')
    source = textwrap.dedent('''\
        import json, os, pathlib, sys, time
        directory = pathlib.Path(__file__).parent
        options = json.loads((directory / 'configuration.json').read_text())
        name = pathlib.Path(sys.argv[0]).name
        with (directory / 'calls.jsonl').open('a') as log:
            log.write(json.dumps([name, sys.argv[1:], os.environ.get('PGSSLMODE')]) + '\\n')
        if name == 'pg_dump':
            if '--version' in sys.argv:
                print('pg_dump (PostgreSQL) 17.6'); sys.exit(0)
            if options.get('stall'):
                time.sleep(60)
            for _ in range(options.get('chunks', 256)):
                sys.stdout.buffer.write(b'X' * 65536)
            sys.stdout.buffer.flush()
            sys.exit(9 if options.get('dump_failure') else 0)
        if name == 'pg_restore':
            sys.stdin.buffer.read(32)
            sys.exit(8 if options.get('restore_failure') else 0)
        if name == 'age':
            if options.get('age_failure'):
                sys.exit(7)
            sys.stdout.buffer.write(b'age-encryption.org/v1\\n')
            for chunk in iter(lambda: sys.stdin.buffer.read(65536), b''):
                sys.stdout.buffer.write(chunk)
    ''')
    for name in ('pg_dump', 'pg_restore', 'age'):
        executable = bin_dir / name
        executable.write_text('#!' + sys.executable + '\n' + source)
        executable.chmod(0o755)
    recipients = tmp_path / 'recipients.txt'
    recipients.write_text('age1' + 'q' * 58 + '\n')  # Apenas fake; age real valida checksum.
    for name, value in {
        'PATH': str(bin_dir) + os.pathsep + os.environ['PATH'],
        'DATABASE_URL': 'postgresql+psycopg://synthetic:secret@db.invalid/jaci',
        'DATABASE_SSL_MODE': 'verify-full', 'BACKUP_ENABLED': 'true',
        'BACKUP_ENCRYPTION_ENABLED': 'true', 'BACKUP_RECIPIENTS_FILE': str(recipients),
        'BACKUP_DIR': str(tmp_path / 'backups'), 'BACKUP_RETENTION_DAYS': '30',
    }.items():
        monkeypatch.setenv(name, value)
    return bin_dir, configuration, recipients


def test_large_stream_and_early_catalog_exit_publish_complete_pair(tmp_path, synthetic_tools):
    settings = EncryptionSettings.from_environment()
    result = create_backup(settings)
    artifact = Artifact.load(result.manifest)
    assert artifact.metadata['size_bytes'] > 8 * 1024 * 1024
    assert artifact.metadata['ciphertext_sha256'] == hashlib.sha256(artifact.archive.read_bytes()).hexdigest()
    assert artifact.archive.stat().st_mode & 0o777 == 0o600
    assert artifact.manifest.stat().st_mode & 0o777 == 0o600
    assert settings.directory.stat().st_mode & 0o777 == 0o700
    assert set(path.suffix for path in settings.directory.iterdir()) == {'.age', '.json'}
    calls = [json.loads(line) for line in (synthetic_tools[0] / 'calls.jsonl').read_text().splitlines()]
    dump = next(call for call in calls if call[0] == 'pg_dump' and '--version' not in call[1])
    assert not any('--file' in value or 'secret' in value for value in dump[1])
    assert dump[2] == 'verify-full'


@pytest.mark.parametrize('failure', ['dump_failure', 'restore_failure', 'age_failure'])
def test_process_failures_publish_nothing_and_preserve_previous(tmp_path, synthetic_tools, failure):
    settings = EncryptionSettings.from_environment()
    previous = create_backup(settings)
    synthetic_tools[1].write_text(json.dumps({failure: True}))
    with pytest.raises(BackupError):
        create_backup(settings)
    assert Artifact.load(previous.manifest)
    assert len(list(settings.directory.glob('*.manifest.json'))) == 1
    assert not list(settings.directory.glob('*.part.*'))


def test_timeout_cancels_children_and_cleans_temporaries(tmp_path, synthetic_tools, monkeypatch):
    from scripts import backup_pipeline
    synthetic_tools[1].write_text('{"stall": true}')
    monkeypatch.setattr(backup_pipeline, 'PIPELINE_TIMEOUT', 0.2)
    with pytest.raises(BackupError):
        create_backup(EncryptionSettings.from_environment())
    assert not list((tmp_path / 'backups').glob('*.part.*'))
    assert not list((tmp_path / 'backups').glob('*.manifest.json'))


@pytest.mark.parametrize('text', ['', 'AGE-SECRET-KEY-1private', 'ssh-ed25519 unsupported', 'age1bad'])
def test_invalid_recipient_fails_before_dump(tmp_path, synthetic_tools, text):
    synthetic_tools[2].write_text(text)
    with pytest.raises(EncryptionConfigurationError):
        EncryptionSettings.from_environment()
    assert not (synthetic_tools[0] / 'calls.jsonl').exists()


def test_recipient_snapshot_is_not_changed_by_file_rotation(tmp_path, synthetic_tools):
    settings = EncryptionSettings.from_environment()
    synthetic_tools[2].write_text('AGE-SECRET-KEY-1must-not-be-read')
    artifact = create_backup(settings)
    assert artifact.metadata['recipient_id'] == settings.recipient_id


@pytest.mark.parametrize('flag, database', [('false', 'postgresql://synthetic/db'), ('true', 'sqlite:///local.db')])
def test_disabled_or_sqlite_needs_no_key_or_tools(monkeypatch, flag, database):
    monkeypatch.setenv('BACKUP_ENABLED', flag)
    monkeypatch.setenv('DATABASE_URL', database)
    monkeypatch.setenv('BACKUP_ENCRYPTION_ENABLED', 'true')
    monkeypatch.delenv('BACKUP_RECIPIENTS_FILE', raising=False)
    assert not EncryptionSettings.from_environment().enabled


def test_missing_age_refuses_encryption_before_postgres(tmp_path, synthetic_tools):
    (synthetic_tools[0] / 'age').unlink()
    settings = EncryptionSettings.from_environment()
    with pytest.raises(BackupError):
        create_backup(settings, tool_search=lambda name: None if name == 'age' else str(synthetic_tools[0] / name))
    assert not (synthetic_tools[0] / 'calls.jsonl').exists()


def test_publication_failure_removes_uncommitted_ciphertext(tmp_path, synthetic_tools, monkeypatch):
    from scripts import backup_pipeline
    monkeypatch.setattr(backup_pipeline, 'publish_manifest', lambda *_: (_ for _ in ()).throw(OSError('disk full')))
    with pytest.raises(BackupError):
        create_backup(EncryptionSettings.from_environment())
    assert not list((tmp_path / 'backups').glob('*.dump.age'))
    assert not list((tmp_path / 'backups').glob('*.part.*'))


def test_retention_keeps_newest_and_never_touches_legacy_or_links(tmp_path, synthetic_tools):
    settings = EncryptionSettings.from_environment()
    first = create_backup(settings)
    value = first.metadata.copy()
    value['created_at'] = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    first.manifest.write_text(json.dumps(value))
    legacy = settings.directory / 'jaci_legacy.dump'
    legacy.write_bytes(b'old unencrypted file owned by user')
    link = settings.directory / 'jaci_symlink.manifest.json'
    link.symlink_to(legacy)
    newest = create_backup(settings)
    prune_encrypted(settings.directory, 30)
    assert not first.manifest.exists() and not first.archive.exists()
    assert Artifact.load(newest.manifest)
    assert legacy.exists() and link.is_symlink()
    # Mesmo com prazo vencido, o último conjunto íntegro deve permanecer.
    value = newest.metadata.copy()
    value['created_at'] = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    newest.manifest.write_text(json.dumps(value))
    prune_encrypted(settings.directory, 30)
    assert Artifact.load(newest.manifest)


def test_sigterm_cleans_pipeline_files(tmp_path, synthetic_tools):
    synthetic_tools[1].write_text('{"stall": true}')
    process = subprocess.Popen([sys.executable, '-m', 'scripts.backup_pipeline'], cwd=PROJECT_ROOT,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ.copy())
    try:
        deadline = time.monotonic() + 10
        while not list((tmp_path / 'backups').glob('*.part.*')):
            assert process.poll() is None and time.monotonic() < deadline
            time.sleep(0.02)
        process.send_signal(signal.SIGTERM)
        stdout, stderr = process.communicate(timeout=10)
        assert process.returncode != 0 and b'secret' not in stdout + stderr
        assert not list((tmp_path / 'backups').glob('*.part.*'))
        assert not list((tmp_path / 'backups').glob('*.manifest.json'))
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate()


@pytest.mark.skipif(not (shutil.which('age') and shutil.which('age-keygen')), reason='Requer age real instalado explicitamente')
def test_real_age_decryption_rotation_wrong_key_and_corruption(tmp_path, synthetic_tools):
    # age real; PostgreSQL simulado. Não comprova restauração PostgreSQL.
    (synthetic_tools[0] / 'age').unlink()
    recovered = []
    for number in range(2):
        key = tmp_path / f'recovery-{number}.key'
        subprocess.run(['age-keygen', '-o', str(key)], check=True, capture_output=True)
        recipient = subprocess.run(['age-keygen', '-y', str(key)], check=True, capture_output=True, text=True).stdout
        synthetic_tools[2].write_text(recipient)
        artifact = create_backup(EncryptionSettings.from_environment())
        decrypted = subprocess.run(['age', '--decrypt', '-i', str(key), str(artifact.archive)], capture_output=True, check=True).stdout
        assert decrypted == b'X' * 65536 * 256
        recovered.append((artifact, key))
    wrong = subprocess.run(['age', '--decrypt', '-i', str(recovered[1][1]), str(recovered[0][0].archive)], capture_output=True)
    assert wrong.returncode != 0
    payload = recovered[1][0].archive.read_bytes()
    recovered[1][0].archive.write_bytes(payload[:-1] + bytes([payload[-1] ^ 1]))
    corrupt = subprocess.run(['age', '--decrypt', '-i', str(recovered[1][1]), str(recovered[1][0].archive)], capture_output=True)
    assert corrupt.returncode != 0


def test_shell_dispatches_encrypted_mode_without_plaintext_dump(tmp_path, synthetic_tools):
    result = subprocess.run(['bash', str(PROJECT_ROOT / 'scripts/backup_database.sh')],
                            cwd=PROJECT_ROOT, capture_output=True, timeout=20)
    assert result.returncode == 0
    assert len(list((tmp_path / 'backups').glob('*.manifest.json'))) == 1
    assert not list((tmp_path / 'backups').glob('*.dump'))
    assert b'secret' not in result.stdout + result.stderr


def test_no_encrypted_fallback_on_shell_configuration_error(tmp_path, synthetic_tools):
    synthetic_tools[2].write_text('AGE-SECRET-KEY-1private')
    result = subprocess.run(['bash', str(PROJECT_ROOT / 'scripts/backup_database.sh')],
                            cwd=PROJECT_ROOT, capture_output=True, timeout=20)
    assert result.returncode != 0
    assert not list((tmp_path / 'backups').glob('*.dump'))
    assert not (synthetic_tools[0] / 'calls.jsonl').exists()


def test_manifest_is_published_only_after_valid_ciphertext(tmp_path, synthetic_tools, monkeypatch):
    from scripts import backup_pipeline
    original = backup_pipeline.publish_manifest
    events = []
    def publish(path, metadata):
        assert not path.exists()
        archive = path.parent / metadata['filename']
        assert archive.exists() and not list(path.parent.glob('*.part.*'))
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == metadata['ciphertext_sha256']
        events.append(metadata['backup_id'])
        original(path, metadata)
    monkeypatch.setattr(backup_pipeline, 'publish_manifest', publish)
    artifact = create_backup(EncryptionSettings.from_environment())
    assert events == [artifact.backup_id]
