#!/usr/bin/env bash
set -Eeuo pipefail

is_server_process() {
    [[ "${1-}" == "python" || "${1-}" == "python3" ]] \
        && [[ "${2-}" == "run.py" || "${2-}" == "/app/run.py" ]]
}

write_cron_environment() {
    local environment_file="${BACKUP_CRON_ENV_FILE:-/run/jaci-backup.env}"
    local temporary_file="${environment_file}.tmp.$$"
    local variable

    BACKUP_ENABLED="${BACKUP_ENABLED-true}"
    BACKUP_DIR="${BACKUP_DIR-/var/backups/jaci}"
    BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS-30}"
    TZ="${TZ-America/Sao_Paulo}"

    umask 077
    mkdir -p "$(dirname "$environment_file")"
    : > "$temporary_file"

    for variable in \
        DATABASE_URL \
        BACKUP_ENABLED \
        BACKUP_DIR \
        BACKUP_RETENTION_DAYS \
        DATABASE_SSL_MODE \
        TZ
    do
        printf 'export %s=%q\n' "$variable" "${!variable-}" >> "$temporary_file"
    done

    chmod 0600 "$temporary_file"
    mv -- "$temporary_file" "$environment_file"
}

if is_server_process "$@"; then
    write_cron_environment
    env -i \
        PATH="${PATH:-/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin}" \
        TZ="${TZ:-America/Sao_Paulo}" \
        cron
fi

exec "$@"
