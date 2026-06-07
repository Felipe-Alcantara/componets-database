#!/usr/bin/env python3
"""
start_app.py — Script padrão de inicialização (Felixo System Design).

Este projeto NÃO é uma aplicação web — é um coletor (CLI). Seguindo o espírito do
contrato de start do Felixo, este script faz, com um único comando:
  (1) instala as dependências, (2) executa a coleta de componentes.

Uso:
    python start_app.py                 # instala (se preciso) + coleta tudo (preview)
    python start_app.py --commit        # instala + coleta tudo e grava no banco SQLite
    python start_app.py --source magicui # coleta apenas uma fonte
    python start_app.py --no-install     # pula a instalação de dependências
    python start_app.py stats            # mostra estatísticas do banco já coletado
"""

import sys
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRAPER_DIR = ROOT / "scraper"
REQUIREMENTS = SCRAPER_DIR / "requirements.txt"


def install_deps() -> None:
    """Instala as dependências do scraper via pip."""
    if not REQUIREMENTS.exists():
        print(f"[start] ERRO: requirements.txt não encontrado em {REQUIREMENTS}")
        sys.exit(1)
    print("[start] Instalando dependências...")
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS)]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        # Fallback comum em distros com PEP 668 (Debian/Ubuntu)
        print("[start] pip falhou; tentando com --break-system-packages...")
        cmd.append("--break-system-packages")
        result = subprocess.run(cmd)
    if result.returncode != 0:
        print("[start] ERRO: não foi possível instalar as dependências.")
        print("[start] Tente manualmente: pip install -r scraper/requirements.txt")
        sys.exit(1)
    print("[start] Dependências instaladas.\n")


def run_scraper(args: list[str]) -> int:
    """Executa o coletor (scraper/main.py) com os argumentos dados."""
    main_py = SCRAPER_DIR / "main.py"
    if not main_py.exists():
        print(f"[start] ERRO: {main_py} não encontrado.")
        sys.exit(1)
    cmd = [sys.executable, str(main_py)] + args
    return subprocess.run(cmd, cwd=str(SCRAPER_DIR)).returncode


def run_query(args: list[str]) -> int:
    """Executa a consulta ao banco (scraper/query.py)."""
    query_py = SCRAPER_DIR / "query.py"
    if not query_py.exists():
        print(f"[start] ERRO: {query_py} não encontrado.")
        sys.exit(1)
    cmd = [sys.executable, str(query_py)] + args
    return subprocess.run(cmd, cwd=str(SCRAPER_DIR)).returncode


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Setup + coleta de componentes (Felixo UI Index)",
        add_help=True,
    )
    parser.add_argument("command", nargs="?", default="collect",
                        choices=["collect", "stats"],
                        help="collect (padrão) coleta componentes; stats mostra o banco")
    parser.add_argument("--commit", action="store_true",
                        help="grava no banco SQLite (sem isto, é só preview)")
    parser.add_argument("--source", type=str,
                        help="coleta apenas a fonte indicada (ex: magicui)")
    parser.add_argument("--no-install", action="store_true",
                        help="pula a instalação de dependências")
    args = parser.parse_args()

    if not args.no_install:
        install_deps()

    if args.command == "stats":
        sys.exit(run_query(["--stats"]))

    # Monta os argumentos da coleta
    scraper_args = []
    if args.source:
        scraper_args += ["--source", args.source]
    else:
        scraper_args += ["--all-sources"]
    if args.commit:
        scraper_args += ["--commit", "--no-interactive"]

    print(f"[start] Executando coleta: {' '.join(scraper_args)}\n")
    sys.exit(run_scraper(scraper_args))


if __name__ == "__main__":
    main()
