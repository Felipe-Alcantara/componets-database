#!/usr/bin/env python3
"""
migrate_categories.py — Aplica categorização ao banco já coletado.

Adiciona/preenche, sem recoletar:
- canonical_category: categoria primária (navegação)
- category_tags: facetas múltiplas em JSON (busca multi-uso)
- is_demo: marca variações de demonstração (escondidas por padrão na busca)

Uso:
    python migrate_categories.py            # preview (mostra distribuição, não grava)
    python migrate_categories.py --commit   # grava no banco
"""
import argparse
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.categorize import canonical_category, category_tags, is_demo

DB_PATH = Path("data/components.db")

COLUMNS = {
    "canonical_category": "TEXT",
    "category_tags": "TEXT",
    "is_demo": "INTEGER DEFAULT 0",
}


def ensure_columns(conn: sqlite3.Connection) -> None:
    existing = {r[1] for r in conn.execute("PRAGMA table_info(components)").fetchall()}
    for col, coltype in COLUMNS.items():
        if col not in existing:
            print(f"[migrate] adicionando coluna {col}...")
            conn.execute(f"ALTER TABLE components ADD COLUMN {col} {coltype}")
    conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Aplica categorização ao banco")
    parser.add_argument("--commit", action="store_true", help="grava no banco (padrão: preview)")
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"Banco não encontrado em {DB_PATH}. Rode a coleta primeiro.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    if args.commit:
        ensure_columns(conn)

    rows = conn.execute("SELECT external_id, name, category FROM components").fetchall()
    primary_dist = Counter()
    tag_dist = Counter()
    demo_count = 0
    updates = []

    for external_id, name, category in rows:
        cat = category or ""
        primary = canonical_category(name, cat)
        tags = category_tags(name, cat)
        demo = is_demo(name)

        primary_dist[primary] += 1
        for t in tags:
            tag_dist[t] += 1
        if demo:
            demo_count += 1

        updates.append((primary, json.dumps(tags), 1 if demo else 0, external_id))

    print(f"\n{len(rows)} componentes")
    print(f"Demos detectadas: {demo_count}")
    print(f"\nCategoria primária ({len(primary_dist)} categorias):")
    for cat, n in primary_dist.most_common(15):
        print(f"  {cat:<16} {n}")
    print(f"\nFacetas (tags) mais comuns:")
    for t, n in tag_dist.most_common(15):
        print(f"  {t:<16} {n}")

    if not args.commit:
        print(f"\n[preview] nada gravado. Rode com --commit para aplicar.")
        conn.close()
        return

    conn.executemany(
        "UPDATE components SET canonical_category=?, category_tags=?, is_demo=? "
        "WHERE external_id=?",
        updates,
    )
    conn.commit()
    conn.close()
    print(f"\n[migrate] {len(updates)} componentes atualizados.")


if __name__ == "__main__":
    main()
