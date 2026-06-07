#!/usr/bin/env python3
"""
migrate_categories.py — Aplica a categoria canônica ao banco já coletado.

Adiciona a coluna `canonical_category` (se não existir) e a preenche para
todos os componentes, derivando de name + category. Não recoleta nada.

Uso:
    python migrate_categories.py            # preview (mostra distribuição, não grava)
    python migrate_categories.py --commit   # grava a categoria canônica no banco
"""
import argparse
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.categorize import canonical_category

DB_PATH = Path("data/components.db")


def ensure_column(conn: sqlite3.Connection) -> None:
    cols = [r[1] for r in conn.execute("PRAGMA table_info(components)").fetchall()]
    if "canonical_category" not in cols:
        print("[migrate] adicionando coluna canonical_category...")
        conn.execute("ALTER TABLE components ADD COLUMN canonical_category TEXT")
        conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Aplica categoria canônica ao banco")
    parser.add_argument("--commit", action="store_true", help="grava no banco (padrão: preview)")
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"Banco não encontrado em {DB_PATH}. Rode a coleta primeiro.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    if args.commit:
        ensure_column(conn)

    rows = conn.execute("SELECT external_id, name, category FROM components").fetchall()
    dist = Counter()
    updates = []
    for external_id, name, category in rows:
        canon = canonical_category(name, category or "")
        dist[canon] += 1
        updates.append((canon, external_id))

    print(f"\n{len(rows)} componentes · {len(dist)} categorias canônicas\n")
    for cat, n in dist.most_common():
        print(f"  {cat:<16} {n}")

    if not args.commit:
        print(f"\n[preview] nada gravado. Rode com --commit para aplicar.")
        conn.close()
        return

    conn.executemany(
        "UPDATE components SET canonical_category = ? WHERE external_id = ?",
        updates,
    )
    conn.commit()
    conn.close()
    print(f"\n[migrate] {len(updates)} componentes atualizados com categoria canônica.")


if __name__ == "__main__":
    main()
