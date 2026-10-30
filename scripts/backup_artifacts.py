"""Contrato de artefatos criptografados compartilhado com o produtor BL-0009."""

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

IDENTIFIER = r"jaci_[A-Za-z0-9_-]{1,96}"
MANIFEST_FIELDS = {
    "schema_version", "backup_id", "created_at", "postgresql_version", "filename",
    "size_bytes", "ciphertext_sha256", "recipient_id",
}


class BackupError(Exception):
    """Erro operacional cujo texto pode ser publicado sem dados externos."""


def validate_metadata(data: dict, manifest_name: str) -> datetime:
    identifier = data["backup_id"]
    if (
        set(data) != MANIFEST_FIELDS
        or type(data["schema_version"]) is not int or data["schema_version"] != 1
        or not re.fullmatch(IDENTIFIER, identifier)
        or manifest_name != identifier + ".manifest.json"
        or data["filename"] != identifier + ".dump.age"
        or type(data["size_bytes"]) is not int or data["size_bytes"] <= 0
        or not re.fullmatch(r"[0-9a-f]{64}", data["ciphertext_sha256"])
        or not isinstance(data["recipient_id"], str)
        or not re.fullmatch(r"[A-Za-z0-9_:+/=@.-]{1,256}", data["recipient_id"])
        or not isinstance(data["postgresql_version"], str)
        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._()+:-]{0,127}", data["postgresql_version"])
    ):
        raise ValueError()
    created = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
    if created.utcoffset() != timedelta(0) or created > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise ValueError()
    return created


def digest(path: Path) -> tuple[int, str]:
    total = 0
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            total += len(chunk)
            checksum.update(chunk)
    return total, checksum.hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        # Persistir também o rename, inclusive após reinício inesperado do host.
        directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@dataclass(frozen=True)
class Artifact:
    manifest: Path
    archive: Path
    metadata: dict
    created_at: datetime

    @property
    def backup_id(self) -> str:
        return self.metadata["backup_id"]

    @classmethod
    def load(cls, manifest: Path) -> "Artifact":
        try:
            if manifest.is_symlink() or not manifest.is_file() or manifest.stat().st_size > 65536:
                raise ValueError()
            data = json.loads(manifest.read_text(encoding="utf-8"))
            created = validate_metadata(data, manifest.name)
            archive = manifest.parent / data["filename"]
            if archive.is_symlink() or not archive.is_file():
                raise ValueError()
            with archive.open("rb") as stream:
                if stream.readline(128) != b"age-encryption.org/v1\n":
                    raise ValueError()
            if digest(archive) != (data["size_bytes"], data["ciphertext_sha256"]):
                raise ValueError()
            return cls(manifest, archive, data, created)
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
            raise BackupError("Artefato criptografado ausente, inválido ou corrompido.") from exc


def discover(directory: Path) -> tuple[list[Artifact], list[str]]:
    artifacts, invalid = [], []
    for manifest in directory.glob("jaci_*.manifest.json"):
        try:
            artifacts.append(Artifact.load(manifest))
        except BackupError:
            invalid.append("invalid_artifact")
    artifacts.sort(key=lambda item: (item.created_at, item.backup_id))
    return artifacts, invalid
