import json
import dataclasses
from datetime import datetime, timezone
from pathlib import Path
from .models import ComponentDTO, ImportSummary
from .categorize import canonical_category, category_tags, is_demo
from .schema import init_db, get_or_create_source, get_or_create_tag


def _derive(dto: ComponentDTO) -> tuple[str, list[str], bool]:
    """Deriva categoria primária, tags de faceta e flag de demo."""
    primary = dto.canonical_category or canonical_category(dto.name, dto.category)
    tags = dto.category_tags or category_tags(dto.name, dto.category)
    demo = dto.is_demo or is_demo(dto.name)
    return primary, tags, demo


def save_json(components: list[ComponentDTO], path: Path) -> None:
    """Salva o snapshot da coleta em JSON (auditoria)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [dataclasses.asdict(dto) for dto in components]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  [persistence] JSON salvo em {path} ({len(components)} componentes)")


def _upsert_component(conn, dto: ComponentDTO, now: str, summary: ImportSummary) -> None:
    primary, tags, demo = _derive(dto)
    source_id = get_or_create_source(
        conn, dto.source_slug, dto.source_slug, dto.framework, dto.license
    )

    existing = conn.execute(
        "SELECT id FROM components WHERE external_id = ?", (dto.external_id,)
    ).fetchone()

    if existing:
        comp_id = existing[0]
        conn.execute(
            """UPDATE components SET
                source_id=?, name=?, title=?, description=?, source_url=?,
                public_url=?, category=?, canonical_category=?, is_demo=?,
                license=?, author=?, capture_source=?, preview_image=?, last_seen_at=?
            WHERE id=?""",
            (
                source_id, dto.name, dto.title, dto.description, dto.source_url,
                dto.public_url, dto.category, primary, 1 if demo else 0,
                dto.license, dto.author, dto.capture_source, dto.preview_image,
                now, comp_id,
            ),
        )
        # Recria relações filhas (idempotente)
        conn.execute("DELETE FROM component_tags WHERE component_id=?", (comp_id,))
        conn.execute("DELETE FROM component_files WHERE component_id=?", (comp_id,))
        conn.execute("DELETE FROM component_dependencies WHERE component_id=?", (comp_id,))
        summary.updated += 1
    else:
        cur = conn.execute(
            """INSERT INTO components (
                external_id, source_id, name, title, description, source_url,
                public_url, category, canonical_category, is_demo, license,
                author, capture_source, preview_image, first_seen_at, last_seen_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                dto.external_id, source_id, dto.name, dto.title, dto.description,
                dto.source_url, dto.public_url, dto.category, primary,
                1 if demo else 0, dto.license, dto.author, dto.capture_source,
                dto.preview_image, now, now,
            ),
        )
        comp_id = cur.lastrowid
        summary.created += 1

    # Tags (N:N)
    for tag_name in tags:
        tag_id = get_or_create_tag(conn, tag_name)
        conn.execute(
            "INSERT OR IGNORE INTO component_tags (component_id, tag_id) VALUES (?,?)",
            (comp_id, tag_id),
        )

    # Arquivos de código
    for f in dto.files:
        conn.execute(
            "INSERT INTO component_files (component_id, path, type, content) VALUES (?,?,?,?)",
            (comp_id, f.path, f.type, f.content),
        )

    # Dependências
    for dep in dto.dependencies:
        conn.execute(
            "INSERT OR IGNORE INTO component_dependencies (component_id, name, is_dev) VALUES (?,?,0)",
            (comp_id, dep),
        )
    for dep in dto.dev_dependencies:
        conn.execute(
            "INSERT OR IGNORE INTO component_dependencies (component_id, name, is_dev) VALUES (?,?,1)",
            (comp_id, dep),
        )


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
        print(f"  [persistence] dry-run: {len(components)} componentes não gravados no banco")
        return summary

    conn = init_db(db_path)
    now = datetime.now(timezone.utc).isoformat()
    try:
        for dto in components:
            _upsert_component(conn, dto, now, summary)
        conn.commit()
    finally:
        conn.close()

    print(f"  [persistence] banco: {summary.created} criados, {summary.updated} atualizados")
    return summary
