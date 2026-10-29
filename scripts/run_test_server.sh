#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PYTHON="${TEST_PYTHON:-$ROOT/venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then
    echo 'Python do ambiente não encontrado; instale requirements-dev.txt.' >&2
    exit 1
fi
exec "$PYTHON" -m scripts.test_environment --serve --env-file "${ENV_FILE:-$ROOT/.env.test}" "$@"
