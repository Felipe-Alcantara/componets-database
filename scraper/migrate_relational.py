#!/usr/bin/env python3
"""
migrate_relational.py — Migra o banco flat (1 tabela) para o esquema relacional.

Lê a tabela `components` antiga (com listas em JSON) e reconstrói o banco no
esquema normalizado (sources, components, tags, component_tags, component_files,
component_dependencies) com índices. Não recoleta nada da rede.

Uso:
    python migrate_relational.py            # preview (não grava)
    python migrate_relational.py --commit   # cria <db>.relational e valida
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.schema import init_db, get_or_create_source, get_or_create_tag
from src.categorize import canonical_category, category_tags, is_demo

OLD_DB = Path("data/components.db")
NEW_DB = Path("data/components.relational.db")


def _json_list(value: str) -> list:
    if not value:
        return []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []


def _has_column(conn, table, col) -> bool:
    return col in {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}


def migrate(old_db: Path, new_db: Path) -> dict:
    old = sqlite3.connect(old_db)
    old.row_factory = sqlite3.Row
    if new_db.exists():
        new_db.unlink()
    new = init_db(new_db)

    has_canon = _has_column(old, "components", "canonical_category")
    has_tags = _has_column(old, "components", "category_tags")
    has_demo = _has_column(old, "components", "is_demo")

    rows = old.execute("SELECT * FROM components").fetchall()
    stats = {"components": 0, "tags": 0, "files": 0, "deps": 0}

    for r in rows:
        source_id = get_or_create_source(
            new, r["source_slug"], r["source_slug"], r["framework"], r["license"]
        )
        primary = (r["canonical_category"] if has_canon and r["canonical_category"]
                   else canonical_category(r["name"], r["category"] or ""))
        demo = (bool(r["is_demo"]) if has_demo and r["is_demo"] is not None
                else is_demo(r["name"]))
        tags = (_json_list(r["category_tags"]) if has_tags and r["category_tags"]
                else category_tags(r["name"], r["category"] or ""))

        cur = new.execute(
            """INSERT INTO components (
                external_id, source_id, name, title, description, source_url,
                public_url, category, canonical_category, is_demo, license,
                author, capture_source, preview_image, first_seen_at, last_seen_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                r["external_id"], source_id, r["name"], r["title"], r["description"],
                r["source_url"], r["public_url"], r["category"], primary,
                1 if demo else 0, r["license"], r["author"], r["capture_source"],
                r["preview_image"], r["first_seen_at"], r["last_seen_at"],
            ),
        )
        comp_id = cur.lastrowid
        stats["components"] += 1

        for tag_name in tags:
            tag_id = get_or_create_tag(new, tag_name)
            new.execute(
                "INSERT OR IGNORE INTO component_tags (component_id, tag_id) VALUES (?,?)",
                (comp_id, tag_id),
            )
            stats["tags"] += 1

        for f in _json_list(r["files"]):
            new.execute(
                "INSERT INTO component_files (component_id, path, type, content) VALUES (?,?,?,?)",
                (comp_id, f.get("path", ""), f.get("type", ""), f.get("content", "")),
            )
            stats["files"] += 1

        for dep in _json_list(r["dependencies"]):
            new.execute(
                "INSERT OR IGNORE INTO component_dependencies (component_id, name, is_dev) VALUES (?,?,0)",
                (comp_id, dep),
            )
            stats["deps"] += 1
        for dep in _json_list(r["dev_dependencies"]):
            new.execute(
                "INSERT OR IGNORE INTO component_dependencies (component_id, name, is_dev) VALUES (?,?,1)",
                (comp_id, dep),
            )
            stats["deps"] += 1

    new.commit()

    # Validação de integridade
    integrity = new.execute("PRAGMA integrity_check").fetchone()[0]
    fk_errors = new.execute("PRAGMA foreign_key_check").fetchall()
    stats["integrity"] = integrity
    stats["fk_errors"] = len(fk_errors)
    stats["distinct_tags"] = new.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
    stats["sources"] = new.execute("SELECT COUNT(*) FROM sources").fetchone()[0]

    old.close()
    new.close()
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Migra banco flat para relacional")
    parser.add_argument("--commit", action="store_true",
                        help="grava o banco relacional (padrão: preview só conta)")
    args = parser.parse_args()

    if not OLD_DB.exists():
        print(f"Banco de origem não encontrado: {OLD_DB}")
        sys.exit(1)

    if not args.commit:
        n = sqlite3.connect(OLD_DB).execute("SELECT COUNT(*) FROM components").fetchone()[0]
        print(f"[preview] {n} componentes seriam migrados de {OLD_DB} para esquema relacional.")
        print(f"[preview] rode com --commit para gerar {NEW_DB}.")
        return

    print(f"[migrate] migrando {OLD_DB} -> {NEW_DB} (relacional)...")
    stats = migrate(OLD_DB, NEW_DB)
    print(f"\n[migrate] concluído:")
    print(f"  sources:    {stats['sources']}")
    print(f"  components: {stats['components']}")
    print(f"  tags:       {stats['distinct_tags']} distintas ({stats['tags']} relações)")
    print(f"  files:      {stats['files']}")
    print(f"  deps:       {stats['deps']}")
    print(f"  integrity:  {stats['integrity']}")
    print(f"  fk_errors:  {stats['fk_errors']}")
    print(f"\nRevise {NEW_DB}. Para promover: mv {NEW_DB} {OLD_DB}")


if __name__ == "__main__":
    main()
