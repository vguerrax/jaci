"""Executa o Jaci aplicando migrações antes de iniciar o servidor."""

import argparse
import os
import subprocess
import sys

import uvicorn


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa o servidor Jaci.")
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Porta HTTP (padrão: 8000).",
    )
    parser.add_argument(
        "--restart",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Reinicia automaticamente ao alterar arquivos (padrão: ativo).",
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Arquivo de ambiente carregado antes da aplicação (padrão: .env).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    os.environ["ENV_FILE"] = args.env_file
    subprocess.run(
        [sys.executable, "-m", "scripts.apply_migrations"],
        check=True,
    )
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=args.port,
        reload=args.restart,
    )


if __name__ == "__main__":
    main()
