#!/usr/bin/env python3
"""
Felixo UI Hub — Scraper de componentes UI

Uso:
  python main.py --help
  python main.py --list-sources
  python main.py --source shadcn --limit 20
  python main.py --source magicui
  python main.py --all-sources
  python main.py --all-sources --commit
  python main.py --all-sources --no-interactive
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ajuste de path para importar src/
sys.path.insert(0, str(Path(__file__).parent))


def load_dotenv(path: Path) -> None:
    """Carrega variáveis de um .env simples para os.environ (sem dependência externa)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


# Carrega .env antes de importar config (que lê os.getenv no nível do módulo)
load_dotenv(Path(__file__).parent / ".env")

from src.config import ScraperConfig
from src.registry import get_adapter, list_sources
from src.persistence import persist_components


def build_config(args) -> ScraperConfig:
    return ScraperConfig(
        max_components=args.limit,
        dry_run=not args.commit,
        headless=True,
        request_delay=args.delay,
    )


def run_source(slug: str, config: ScraperConfig, data_dir: Path) -> dict:
    print(f"\n{'='*50}")
    print(f"Coletando: {slug}")
    print(f"{'='*50}")

    adapter = get_adapter(slug)
    components = adapter.collect(config)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = data_dir / slug / f"{timestamp}.json"
    db_path = data_dir / "components.db"

    summary = persist_components(
        components,
        db_path=db_path,
        json_path=json_path,
        commit=not config.dry_run,
    )

    report = summary.report()
    report["source"] = slug
    report["components_collected"] = len(components)
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Felixo UI Hub — Coleta componentes UI de múltiplas fontes"
    )
    parser.add_argument("--list-sources", action="store_true", help="Lista fontes disponíveis")
    parser.add_argument("--source", type=str, help="Coleta de uma fonte específica (ex: shadcn)")
    parser.add_argument("--all-sources", action="store_true", help="Coleta de todas as fontes")
    parser.add_argument("--limit", type=int, default=500, help="Máximo de componentes por fonte")
    parser.add_argument("--commit", action="store_true", help="Grava no banco SQLite (padrão: dry-run)")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay entre requisições em segundos")
    parser.add_argument("--no-interactive", action="store_true", help="Sem confirmações interativas")
    parser.add_argument("--data-dir", type=str, default="data", help="Diretório para salvar dados")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    # Listar fontes disponíveis
    if args.list_sources:
        sources = list_sources()
        print("\nFontes disponíveis:\n")
        for s in sources:
            print(f"  {s['slug']:<15} {s['name']:<20} {s['framework']:<25} {s['license']}")
        return

    # Validar argumentos
    if not args.source and not args.all_sources:
        parser.print_help()
        return

    config = build_config(args)
    mode = "COMMIT (gravando no banco)" if args.commit else "DRY-RUN (apenas JSON, sem banco)"
    print(f"\nModo: {mode}")
    print(f"Limite por fonte: {config.max_components}")
    print(f"Delay: {config.request_delay}s")

    # Confirmação interativa
    if not args.no_interactive and args.commit:
        resp = input("\nConfirmar gravação no banco? [s/N] ").strip().lower()
        if resp != "s":
            print("Cancelado.")
            return

    # Coletar
    slugs_to_run = []
    if args.all_sources:
        slugs_to_run = [s["slug"] for s in list_sources()]
    elif args.source:
        slugs_to_run = [args.source]

    all_reports = []
    for slug in slugs_to_run:
        try:
            report = run_source(slug, config, data_dir)
            all_reports.append(report)
        except ValueError as exc:
            print(f"\nERRO: {exc}")
            sys.exit(1)
        except Exception as exc:
            print(f"\nERRO ao coletar {slug}: {exc}")
            all_reports.append({"source": slug, "error": str(exc)})

    # Resumo final
    print(f"\n{'='*50}")
    print("RESUMO FINAL")
    print(f"{'='*50}")
    total = sum(r.get("components_collected", 0) for r in all_reports)
    print(f"Total de componentes coletados: {total}")
    print(json.dumps(all_reports, indent=2, ensure_ascii=False))

    # Salvar resumo
    summary_path = data_dir / f"summary_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_reports, f, indent=2, ensure_ascii=False)
    print(f"\nResumo salvo em {summary_path}")


if __name__ == "__main__":
    main()
