#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 || ! "$1" =~ ^v?[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Uso: $0 <versao> [arquivo-env] (exemplo: $0 1.3.0)" >&2
    exit 1
fi

APP_VERSION="${1#v}"
ENV_FILE="${2:-.env.production}"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "Arquivo de ambiente não encontrado: $ENV_FILE" >&2
    exit 1
fi

# Python 3 permite substituir o arquivo atomicamente sem interpretar seu conteúdo.
python3 - "$ENV_FILE" "$APP_VERSION" <<'PY'
import os
from pathlib import Path
import re
import stat
import sys
import tempfile

target = Path(sys.argv[1]).resolve()
version = sys.argv[2]
temporary = None
try:
    mode = stat.S_IMODE(target.stat().st_mode)
    if not mode & 0o222 or not os.access(target, os.W_OK):
        raise PermissionError
    with target.open(encoding="utf-8", newline="") as source:
        lines = source.readlines()
    updated = []
    found = False
    for line in lines:
        assignment = re.match(r"^[ \t]*(?:export[ \t]+)?APP_VERSION[ \t]*=(.*)", line)
        if not assignment:
            updated.append(line)
            continue
        value = re.fullmatch(
            r'''[ \t]*(?:'[^']*'|"[^"]*"|[^#]*?)[ \t]*(#.*)?''',
            assignment.group(1).rstrip("\r\n"),
        )
        comment = value.group(1) if value else None
        if not found:
            updated.append(f"APP_VERSION={version}" + (f" {comment}" if comment else "") + "\n")
            found = True
        elif comment:
            updated.append(comment + "\n")
    if not found:
        if updated and not updated[-1].endswith("\n"):
            updated.append("\n")
        updated.append(f"APP_VERSION={version}\n")
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", dir=target.parent,
        prefix=target.name + ".", delete=False,
    ) as output:
        temporary = output.name
        output.writelines(updated)
        output.flush()
        os.fchmod(output.fileno(), mode)
    os.replace(temporary, target)
    temporary = None
except (OSError, UnicodeError):
    print("Não foi possível atualizar APP_VERSION no arquivo de ambiente.", file=sys.stderr)
    sys.exit(1)
finally:
    if temporary is not None:
        os.unlink(temporary)
PY

export ENV_FILE APP_VERSION

docker compose --env-file "$ENV_FILE" build
docker compose --env-file "$ENV_FILE" run --rm jaci python -m scripts.create_database
docker compose --env-file "$ENV_FILE" run --rm jaci python -m scripts.apply_migrations
docker compose --env-file "$ENV_FILE" up -d --remove-orphans
