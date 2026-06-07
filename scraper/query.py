#!/usr/bin/env python3
"""
query.py — Consulta o banco de componentes coletados.

Uso:
    python query.py --stats                          # totais por fonte
    python query.py --search button                  # busca por nome/título
    python query.py --search card --framework React  # filtra por framework
    python query.py --category button --limit 10     # lista por categoria canônica
    python query.py --categories                     # totais por categoria canônica
    python query.py --source uiverse --limit 10      # lista de uma fonte
    python query.py --show uiverse_buttons_xxx       # mostra um componente
"""
import argparse
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/components.db")


def connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        print(f"Banco não encontrado em {DB_PATH}.")
        print("Rode a coleta primeiro: python main.py --all-sources --commit")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def cmd_stats(conn: sqlite3.Connection) -> None:
    total = conn.execute("SELECT COUNT(*) FROM components").fetchone()[0]
    print(f"\nTotal de componentes: {total}\n")
    print(f"{'Fonte':<15} {'Total':>7}")
    print("-" * 23)
    rows = conn.execute(
        "SELECT source_slug, COUNT(*) AS n FROM components "
        "GROUP BY source_slug ORDER BY n DESC"
    ).fetchall()
    for r in rows:
        print(f"{r['source_slug']:<15} {r['n']:>7}")


def cmd_categories(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        "SELECT canonical_category, COUNT(*) AS n FROM components "
        "GROUP BY canonical_category ORDER BY n DESC"
    ).fetchall()
    print(f"\n{len(rows)} categorias canônicas:\n")
    print(f"{'Categoria':<18} {'Total':>7}")
    print("-" * 26)
    for r in rows:
        print(f"{r['canonical_category']:<18} {r['n']:>7}")


def cmd_category(conn: sqlite3.Connection, category: str, limit: int) -> None:
    rows = conn.execute(
        "SELECT external_id, name, title, source_slug FROM components "
        "WHERE canonical_category = ? ORDER BY source_slug, name LIMIT ?",
        (category, limit),
    ).fetchall()
    print(f"\n{len(rows)} componente(s) na categoria '{category}':\n")
    for r in rows:
        print(f"  [{r['source_slug']:<10}] {r['title'] or r['name']}  id={r['external_id']}")


def cmd_search(conn: sqlite3.Connection, term: str, framework: str, limit: int) -> None:
    sql = (
        "SELECT external_id, name, title, source_slug, framework, category, license "
        "FROM components WHERE (name LIKE ? OR title LIKE ?)"
    )
    params = [f"%{term}%", f"%{term}%"]
    if framework:
        sql += " AND framework LIKE ?"
        params.append(f"%{framework}%")
    sql += " ORDER BY source_slug, name LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    print(f"\n{len(rows)} resultado(s) para '{term}':\n")
    for r in rows:
        print(f"  [{r['source_slug']:<10}] {r['title'] or r['name']}")
        print(f"     {r['framework']} · {r['category']} · {r['license']} · id={r['external_id']}")


def cmd_source(conn: sqlite3.Connection, source: str, limit: int) -> None:
    rows = conn.execute(
        "SELECT external_id, name, title, category FROM components "
        "WHERE source_slug = ? ORDER BY name LIMIT ?",
        (source, limit),
    ).fetchall()
    print(f"\n{len(rows)} componente(s) de '{source}':\n")
    for r in rows:
        print(f"  {r['title'] or r['name']}  ({r['category']})  id={r['external_id']}")


def cmd_show(conn: sqlite3.Connection, external_id: str) -> None:
    r = conn.execute(
        "SELECT * FROM components WHERE external_id = ?", (external_id,)
    ).fetchone()
    if not r:
        print(f"Componente não encontrado: {external_id}")
        return
    print(f"\n=== {r['title'] or r['name']} ===")
    print(f"Fonte:      {r['source_slug']}")
    print(f"Framework:  {r['framework']}")
    print(f"Categoria:  {r['category']}")
    print(f"Licença:    {r['license']}")
    print(f"Origem:     {r['source_url']}")
    print(f"Público:    {r['public_url']}")
    print(f"Captura:    {r['capture_source']}")
    files = r["files"]
    if files and files != "[]":
        print(f"\nArquivos de código: presentes ({len(files)} bytes de JSON)")
    else:
        print("\nArquivos de código: nenhum (apenas metadados)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Consulta o banco de componentes")
    parser.add_argument("--stats", action="store_true", help="totais por fonte")
    parser.add_argument("--categories", action="store_true", help="totais por categoria canônica")
    parser.add_argument("--category", type=str, help="lista componentes de uma categoria canônica")
    parser.add_argument("--search", type=str, help="busca por nome ou título")
    parser.add_argument("--framework", type=str, default="", help="filtra por framework")
    parser.add_argument("--source", type=str, help="lista componentes de uma fonte")
    parser.add_argument("--show", type=str, help="mostra um componente por external_id")
    parser.add_argument("--limit", type=int, default=20, help="máximo de resultados")
    args = parser.parse_args()

    conn = connect()
    try:
        if args.stats:
            cmd_stats(conn)
        elif args.categories:
            cmd_categories(conn)
        elif args.category:
            cmd_category(conn, args.category, args.limit)
        elif args.search:
            cmd_search(conn, args.search, args.framework, args.limit)
        elif args.source:
            cmd_source(conn, args.source, args.limit)
        elif args.show:
            cmd_show(conn, args.show)
        else:
            parser.print_help()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
