import json
import sqlite3
import dataclasses
from datetime import datetime, timezone
from pathlib import Path
from .models import ComponentDTO, ComponentFile, ImportSummary
from .categorize import canonical_category


def _dto_to_dict(dto: ComponentDTO) -> dict:
    d = dataclasses.asdict(dto)
    # Deriva a categoria canônica de forma centralizada (todas as fontes).
    if not d.get("canonical_category"):
        d["canonical_category"] = canonical_category(dto.name, dto.category)
    d["files"] = json.dumps(d["files"])
    d["dependencies"] = json.dumps(d["dependencies"])
    d["dev_dependencies"] = json.dumps(d["dev_dependencies"])
    d["tags"] = json.dumps(d["tags"])
    d["extras"] = json.dumps(d["extras"])
    return d


def save_json(components: list[ComponentDTO], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = []
    for dto in components:
        d = dataclasses.asdict(dto)
        data.append(d)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  [persistence] JSON salvo em {path} ({len(components)} componentes)")


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            source_slug TEXT NOT NULL,
            source_url TEXT,
            public_url TEXT,
            title TEXT,
            description TEXT,
            framework TEXT,
            category TEXT,
            canonical_category TEXT,
            license TEXT,
            author TEXT,
            dependencies TEXT,
            dev_dependencies TEXT,
            tags TEXT,
            files TEXT,
            preview_image TEXT,
            capture_source TEXT,
            extras TEXT,
            first_seen_at TEXT,
            last_seen_at TEXT
        )
    """)
    conn.commit()
    return conn


def persist_components(
    components: list[ComponentDTO],
    db_path: Path,
    json_path: Path,
    commit: bool = False,
) -> ImportSummary:
    summary = ImportSummary(mode="commit" if commit else "preview")
    summary.components_seen = len(components)

    # Salva JSON sempre (auditoria)
    save_json(components, json_path)

    if not commit:
        summary.preview = len(components)  # type: ignore[attr-defined]
        print(f"  [persistence] dry-run: {len(components)} componentes não gravados no banco")
        return summary

    conn = init_db(db_path)
    now = datetime.now(timezone.utc).isoformat()

    for dto in components:
        d = _dto_to_dict(dto)
        existing = conn.execute(
            "SELECT id, last_seen_at FROM components WHERE external_id = ?",
            (dto.external_id,),
        ).fetchone()

        if existing:
            conn.execute(
                """UPDATE components SET
                    name=?, source_url=?, public_url=?, title=?, description=?,
                    framework=?, category=?, canonical_category=?, license=?, author=?,
                    dependencies=?, dev_dependencies=?, tags=?, files=?, preview_image=?,
                    capture_source=?, extras=?, last_seen_at=?
                WHERE external_id=?""",
                (
                    d["name"], d["source_url"], d["public_url"], d["title"],
                    d["description"], d["framework"], d["category"],
                    d["canonical_category"], d["license"],
                    d["author"], d["dependencies"], d["dev_dependencies"], d["tags"],
                    d["files"], d["preview_image"], d["capture_source"], d["extras"],
                    now, dto.external_id,
                ),
            )
            summary.updated += 1
        else:
            conn.execute(
                """INSERT INTO components (
                    external_id, name, source_slug, source_url, public_url,
                    title, description, framework, category, canonical_category,
                    license, author, dependencies, dev_dependencies, tags, files,
                    preview_image, capture_source, extras, first_seen_at, last_seen_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    dto.external_id, d["name"], d["source_slug"], d["source_url"],
                    d["public_url"], d["title"], d["description"], d["framework"],
                    d["category"], d["canonical_category"], d["license"], d["author"],
                    d["dependencies"], d["dev_dependencies"], d["tags"], d["files"],
                    d["preview_image"], d["capture_source"], d["extras"], now, now,
                ),
            )
            summary.created += 1

    conn.commit()
    conn.close()
    print(f"  [persistence] banco: {summary.created} criados, {summary.updated} atualizados")
    return summary
