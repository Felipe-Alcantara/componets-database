"""
Camada de acesso a dados — única ponte com o SQLite.

Mantém o SQL isolado das rotas Flask. Devolve dicts puros, sem conhecer HTTP.
"""
import sqlite3
from pathlib import Path

# Banco gerado pelo scraper (raiz do repositório / scraper/data)
DB_PATH = Path(__file__).resolve().parents[2] / "scraper" / "data" / "components.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def db_exists() -> bool:
    return DB_PATH.exists()


def get_filters() -> dict:
    """Devolve as opções de filtro: fontes, frameworks, categorias e tags."""
    conn = _connect()
    try:
        sources = [dict(r) for r in conn.execute(
            "SELECT slug, display_name, framework, license, "
            "(SELECT COUNT(*) FROM components c WHERE c.source_id = s.id) AS count "
            "FROM sources s ORDER BY count DESC"
        )]
        frameworks = [r[0] for r in conn.execute(
            "SELECT DISTINCT framework FROM sources WHERE framework != '' ORDER BY framework"
        )]
        categories = [dict(r) for r in conn.execute(
            "SELECT canonical_category AS name, COUNT(*) AS count FROM components "
            "WHERE is_demo = 0 GROUP BY canonical_category ORDER BY count DESC"
        )]
        tags = [dict(r) for r in conn.execute(
            "SELECT t.name, COUNT(*) AS count FROM tags t "
            "JOIN component_tags ct ON ct.tag_id = t.id "
            "JOIN components c ON c.id = ct.component_id "
            "WHERE c.is_demo = 0 GROUP BY t.name ORDER BY count DESC"
        )]
        return {
            "sources": sources,
            "frameworks": frameworks,
            "categories": categories,
            "tags": tags,
        }
    finally:
        conn.close()


def search_components(
    q: str = "",
    source: str = "",
    framework: str = "",
    category: str = "",
    tag: str = "",
    include_demos: bool = False,
    page: int = 1,
    per_page: int = 24,
) -> dict:
    """Busca paginada com filtros combináveis. Não retorna o código (lista leve)."""
    where = []
    params: list = []

    if not include_demos:
        where.append("c.is_demo = 0")
    if q:
        where.append("(c.name LIKE ? OR c.title LIKE ? OR c.description LIKE ?)")
        params += [f"%{q}%", f"%{q}%", f"%{q}%"]
    if source:
        where.append("s.slug = ?")
        params.append(source)
    if framework:
        where.append("s.framework = ?")
        params.append(framework)
    if category:
        where.append("c.canonical_category = ?")
        params.append(category)

    join_tag = ""
    if tag:
        join_tag = (
            "JOIN component_tags ct ON ct.component_id = c.id "
            "JOIN tags t ON t.id = ct.tag_id AND t.name = ? "
        )
        params.insert(0, tag)  # o JOIN vem antes do WHERE na ordem dos params

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    base = (
        f"FROM components c "
        f"JOIN sources s ON s.id = c.source_id "
        f"{join_tag}"
        f"{where_sql}"
    )

    conn = _connect()
    try:
        total = conn.execute(f"SELECT COUNT(DISTINCT c.id) {base}", params).fetchone()[0]

        offset = (page - 1) * per_page
        rows = conn.execute(
            f"SELECT DISTINCT c.id, c.external_id, c.name, c.title, c.description, "
            f"c.canonical_category, c.is_demo, c.public_url, c.license, "
            f"s.slug AS source_slug, s.display_name AS source_name, s.framework "
            f"{base} ORDER BY s.slug, c.name LIMIT ? OFFSET ?",
            params + [per_page, offset],
        ).fetchall()

        items = [_attach_tags(conn, dict(r)) for r in rows]
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }
    finally:
        conn.close()


def get_component(external_id: str) -> dict | None:
    """Detalhe completo de um componente, incluindo código e dependências."""
    conn = _connect()
    try:
        r = conn.execute(
            "SELECT c.*, s.slug AS source_slug, s.display_name AS source_name, "
            "s.framework FROM components c JOIN sources s ON s.id = c.source_id "
            "WHERE c.external_id = ?",
            (external_id,),
        ).fetchone()
        if not r:
            return None
        comp = _attach_tags(conn, dict(r))

        comp["files"] = [dict(f) for f in conn.execute(
            "SELECT path, type, content FROM component_files WHERE component_id = ?",
            (r["id"],),
        )]
        comp["dependencies"] = [dict(d) for d in conn.execute(
            "SELECT name, is_dev FROM component_dependencies WHERE component_id = ?",
            (r["id"],),
        )]
        return comp
    finally:
        conn.close()


def _attach_tags(conn: sqlite3.Connection, comp: dict) -> dict:
    comp["tags"] = [row[0] for row in conn.execute(
        "SELECT t.name FROM tags t JOIN component_tags ct ON ct.tag_id = t.id "
        "WHERE ct.component_id = ? ORDER BY t.name",
        (comp["id"],),
    )]
    return comp
