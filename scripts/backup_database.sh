#!/usr/bin/env bash
set -Eeuo pipefail

BACKUP_ENABLED="${BACKUP_ENABLED-true}"
BACKUP_DIR="${BACKUP_DIR-/var/backups/jaci}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS-30}"
DATABASE_URL="${DATABASE_URL-}"
DATABASE_SSL_MODE="${DATABASE_SSL_MODE-}"
TZ="${TZ-America/Sao_Paulo}"

normalized_enabled="${BACKUP_ENABLED,,}"
case "$normalized_enabled" in
    false | 0 | no | off)
        echo "Backup do banco desabilitado por BACKUP_ENABLED."
        exit 0
        ;;
esac

case "$DATABASE_URL" in
    sqlite:*)
        echo "Backup ignorado: SQLite não faz parte da rotina automática."
        exit 0
        ;;
    postgres://*)
        PG_DATABASE_URL="postgresql://${DATABASE_URL#postgres://}"
        ;;
    postgresql://*)
        PG_DATABASE_URL="$DATABASE_URL"
        ;;
    postgresql+psycopg://*)
        PG_DATABASE_URL="postgresql://${DATABASE_URL#postgresql+psycopg://}"
        ;;
    "")
        echo "DATABASE_URL é obrigatória para o backup PostgreSQL." >&2
        exit 1
        ;;
    *)
        echo "DATABASE_URL não usa um esquema PostgreSQL suportado." >&2
        exit 1
        ;;
esac

if [[ ! "$BACKUP_RETENTION_DAYS" =~ ^[1-9][0-9]*$ ]]; then
    echo "BACKUP_RETENTION_DAYS deve ser um número inteiro positivo." >&2
    exit 1
fi

if [[ -z "$BACKUP_DIR" ]]; then
    echo "BACKUP_DIR não pode ser vazio." >&2
    exit 1
fi

command -v pg_dump >/dev/null 2>&1 || {
    echo "pg_dump não está disponível." >&2
    exit 1
}
command -v pg_restore >/dev/null 2>&1 || {
    echo "pg_restore não está disponível." >&2
    exit 1
}

umask 077
mkdir -p "$BACKUP_DIR"
chmod 0700 "$BACKUP_DIR"

timestamp="$(TZ="$TZ" date +%Y%m%d_%H%M%S)"
final_path="$BACKUP_DIR/jaci_${timestamp}.dump"
temporary_path="${final_path}.tmp.$$"

cleanup() {
    if [[ -n "${temporary_path:-}" ]]; then
        rm -f -- "$temporary_path"
    fi
}
trap cleanup EXIT INT TERM

if [[ -e "$final_path" ]]; then
    echo "O arquivo de backup já existe: $final_path" >&2
    exit 1
fi

if [[ -n "$DATABASE_SSL_MODE" ]]; then
    export PGSSLMODE="$DATABASE_SSL_MODE"
fi

echo "Iniciando backup PostgreSQL."
pg_dump \
    --format=custom \
    --no-owner \
    --no-acl \
    --file="$temporary_path" \
    "$PG_DATABASE_URL"

chmod 0600 "$temporary_path"
pg_restore --list "$temporary_path" >/dev/null

mv -- "$temporary_path" "$final_path"
temporary_path=""
chmod 0600 "$final_path"

find "$BACKUP_DIR" \
    -maxdepth 1 \
    -type f \
    -name 'jaci_*.dump' \
    -mtime +"$BACKUP_RETENTION_DAYS" \
    -delete

echo "Backup PostgreSQL concluído: $final_path"
