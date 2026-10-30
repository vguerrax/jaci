"""Produtor PostgreSQL -> validação/age em memória; disco recebe só ciphertext."""

import argparse
import json
import os
import re
import select
import shutil
import signal
import subprocess
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.backup_artifacts import Artifact, BackupError, atomic_json, digest, discover
from scripts.backup_encryption import EncryptionConfigurationError, EncryptionSettings, prepare_directory

CHUNK_SIZE = 64 * 1024
BUFFER_LIMIT = 1024 * 1024  # Por consumidor, além dos pipes do kernel.
PIPELINE_TIMEOUT = 3600


def age_arguments(executable: str, settings: EncryptionSettings) -> list[str]:
    arguments = [executable, '--encrypt']
    for recipient in settings.recipients:
        arguments.extend(['--recipient', recipient])
    return arguments


def tool_environment() -> dict[str, str]:
    return {'PATH': os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin'), 'LC_ALL': 'C'}


def validate_tools(settings: EncryptionSettings, tool_search) -> tuple[dict[str, str], str]:
    tools = {name: tool_search(name) for name in ('age', 'pg_dump', 'pg_restore')}
    if not all(tools.values()):
        raise BackupError('backup_tool_unavailable')
    try:
        # Congelar destinatários já lidos; o age valida o checksum antes de acessar o banco.
        validation = subprocess.run(
            age_arguments(tools['age'], settings), input=b'', stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, timeout=30, check=False, env=tool_environment(),
        )
        if validation.returncode:
            raise EncryptionConfigurationError('Destinatário recusado pelo age.')
        version = subprocess.run(
            [tools['pg_dump'], '--version'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=30, check=False, env=tool_environment(),
        )
        match = re.search(rb'\b[0-9]+(?:\.[0-9]+)+\b', version.stdout)
        if version.returncode or not match:
            raise BackupError('postgresql_tool_version_unavailable')
        return tools, match.group().decode('ascii')
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BackupError('backup_tool_preflight_failed') from exc


def stop_children(processes: list[subprocess.Popen]) -> None:
    # Sem sessões filhas: um supervisor externo também pode encerrar o grupo inteiro.
    # Estes programas nativos não iniciam plugins/jobs auxiliares neste modo.
    for process in processes:
        if process.poll() is None:
            try:
                process.kill()
            except ProcessLookupError:
                pass
    for process in processes:
        process.wait()
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None and not stream.closed:
                stream.close()


def stream_dump(settings: EncryptionSettings, tools: dict[str, str], output) -> None:
    processes = []
    try:
        catalog = subprocess.Popen(
            [tools['pg_restore'], '--list'], stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, bufsize=0, env=tool_environment(),
        )
        processes.append(catalog)
        encrypted = subprocess.Popen(
            age_arguments(tools['age'], settings), stdin=subprocess.PIPE, stdout=output,
            stderr=subprocess.DEVNULL, bufsize=0, env=tool_environment(),
        )
        processes.append(encrypted)
        environment = dict(tool_environment(), PGDATABASE=settings.database_url, PGCONNECT_TIMEOUT='30')
        if settings.sslmode:
            environment['PGSSLMODE'] = settings.sslmode
        producer = subprocess.Popen(
            [tools['pg_dump'], '--format=custom', '--no-owner', '--no-acl', '--no-password'],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            bufsize=0, env=environment,
        )
        processes.append(producer)
        consumers = (catalog, encrypted)
        buffers = {process: bytearray() for process in consumers}
        for stream in (producer.stdout, catalog.stdin, encrypted.stdin):
            os.set_blocking(stream.fileno(), False)
        eof = False
        deadline = time.monotonic() + PIPELINE_TIMEOUT
        while True:
            if time.monotonic() >= deadline:
                raise BackupError('backup_pipeline_timeout')
            if producer.poll() not in (None, 0) or catalog.poll() not in (None, 0):
                raise BackupError('postgresql_dump_or_catalog_failed')
            if encrypted.poll() is not None:
                if encrypted.returncode != 0 or not encrypted.stdin.closed:
                    raise BackupError('encryption_failed_or_closed_early')
            # --list pode terminar após o TOC. Não bloquear pg_dump/age por isso.
            if catalog.poll() == 0 and not catalog.stdin.closed:
                catalog.stdin.close()
                buffers[catalog].clear()
            live = [process for process in consumers if not process.stdin.closed]
            if eof:
                for process in live:
                    if not buffers[process]:
                        process.stdin.close()
                live = [process for process in consumers if not process.stdin.closed]
            if eof and not live:
                statuses = [process.poll() for process in processes]
                if all(status is not None for status in statuses):
                    # Uma falha pode aparecer entre o poll inicial e este ponto.
                    if any(status != 0 for status in statuses):
                        raise BackupError('backup_process_failed_after_stream')
                    return
            readers = [producer.stdout] if not eof and all(
                len(buffers[process]) <= BUFFER_LIMIT - CHUNK_SIZE for process in live
            ) else []
            writers = [process.stdin for process in live if buffers[process]]
            readable, writable, _ = select.select(readers, writers, [], 0.1)
            if readable:
                try:
                    chunk = os.read(producer.stdout.fileno(), CHUNK_SIZE)
                except BlockingIOError:
                    chunk = None
                if chunk == b'':
                    eof = True
                    producer.stdout.close()
                elif chunk:
                    for process in live:
                        buffers[process].extend(chunk)
            for process in live:
                if process.stdin not in writable:
                    continue
                try:
                    count = os.write(process.stdin.fileno(), buffers[process])
                    del buffers[process][:count]
                except BlockingIOError:
                    continue
                except BrokenPipeError as exc:
                    if process is not catalog:
                        raise BackupError('encryption_pipe_closed') from exc
                    # O status final do catálogo ainda terá de ser zero.
                    process.stdin.close()
                    buffers[process].clear()
    finally:
        stop_children(processes)


def sync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def publish_manifest(path: Path, metadata: dict) -> None:
    atomic_json(path, metadata)


def create_backup(settings: EncryptionSettings, *, tool_search=None) -> Artifact:
    if not settings.enabled:
        raise EncryptionConfigurationError('Produtor criptografado não habilitado.')
    tools, version = validate_tools(settings, tool_search or shutil.which)
    prepare_directory(settings.directory)
    created = datetime.now(timezone.utc)
    identifier = 'jaci_' + created.strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex
    archive = settings.directory / (identifier + '.dump.age')
    manifest = settings.directory / (identifier + '.manifest.json')
    temporary = settings.directory / (archive.name + '.part.' + uuid.uuid4().hex)
    archive_published = False
    temporary_created = False
    try:
        if archive.exists() or archive.is_symlink() or manifest.exists() or manifest.is_symlink():
            raise BackupError('backup_identifier_conflict')
        with temporary.open('xb') as output:
            temporary_created = True
            os.fchmod(output.fileno(), 0o600)
            stream_dump(settings, tools, output)
            output.flush()
            os.fsync(output.fileno())
        with temporary.open('rb') as source:
            if source.readline(128) != b'age-encryption.org/v1\n':
                raise BackupError('invalid_encrypted_output')
        size, checksum = digest(temporary)
        metadata = dict(
            schema_version=1, backup_id=identifier, created_at=created.isoformat(),
            postgresql_version=version, filename=archive.name, size_bytes=size,
            ciphertext_sha256=checksum, recipient_id=settings.recipient_id,
        )
        os.rename(temporary, archive)
        archive_published = True
        sync_directory(settings.directory)
        publish_manifest(manifest, metadata)
        return Artifact.load(manifest)
    except BaseException as exc:
        if archive_published:
            # Só nomes do ID exclusivo desta execução; nunca tocar backup anterior.
            manifest.unlink(missing_ok=True)
            archive.unlink(missing_ok=True)
        if isinstance(exc, (OSError, ValueError)):
            raise BackupError('encrypted_backup_io_failed') from exc
        raise
    finally:
        if temporary_created:
            temporary.unlink(missing_ok=True)


def prune_encrypted(directory: Path, days: int, now: datetime | None = None) -> int:
    if days < 1:
        raise EncryptionConfigurationError('Retenção deve ser positiva.')
    artifacts, _ = discover(directory)
    cutoff = (now or datetime.now(timezone.utc)) - timedelta(days=days)
    expired = [artifact for artifact in artifacts[:-1] if artifact.created_at < cutoff]
    for artifact in expired:
        artifact.manifest.unlink()
        artifact.archive.unlink()
    if expired:
        sync_directory(directory)
    return len(expired)


def cancelled(_signum, _frame) -> None:
    raise BackupError('backup_cancelled')


def main() -> int:
    os.umask(0o077)
    signal.signal(signal.SIGTERM, cancelled)
    signal.signal(signal.SIGINT, cancelled)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', type=Path, metavar='MANIFEST', help='Conferir par local, sem gerar backup ou acessar o banco.')
    args = parser.parse_args()
    try:
        if args.verify is not None:
            print(json.dumps(Artifact.load(args.verify).metadata))
            return 0
        settings = EncryptionSettings.from_environment()
        if not settings.enabled:
            print(json.dumps({'health': 'disabled', 'encrypted': False}))
            return 0
        artifact = create_backup(settings)
        try:
            removed = prune_encrypted(settings.directory, settings.retention_days)
        except (OSError, BackupError):
            print(json.dumps({'health': 'failed', 'error': 'backup_created_retention_failed',
                              'backup_id': artifact.backup_id}))
            return 1
        print(json.dumps({'health': 'ok', 'encrypted': True, 'backup_id': artifact.backup_id,
                          'manifest': artifact.manifest.name, 'removed_pairs': removed}))
        return 0
    except EncryptionConfigurationError:
        print(json.dumps({'health': 'invalid_configuration', 'error': 'encryption_configuration_invalid'}))
        return 2
    except (BackupError, OSError):
        print(json.dumps({'health': 'failed', 'error': 'encrypted_backup_failed'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
