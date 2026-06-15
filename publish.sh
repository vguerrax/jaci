#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-.env.production}"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "Arquivo de ambiente não encontrado: $ENV_FILE" >&2
    exit 1
fi

export ENV_FILE

docker compose --env-file "$ENV_FILE" build
docker compose --env-file "$ENV_FILE" run --rm jaci python -m scripts.create_database
docker compose --env-file "$ENV_FILE" run --rm jaci python -m scripts.apply_migrations
docker compose --env-file "$ENV_FILE" up -d --remove-orphans
