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
    sort: str = "smart",
    seed: int = 1,
    page: int = 1,
    per_page: int = 24,
) -> dict:
    """
    Busca paginada com filtros combináveis. Não retorna o código (lista leve).
    sort: 'smart' (renderizáveis primeiro) | 'random' (ordem embaralhada estável
    pelo seed, para paginar sem repetir) | 'name'.
    """
    where = []
    params: list = []

    if not include_demos:
        where.append("c.is_demo = 0")
    if q:
        # Busca em camadas: campos do componente, tags e — importante — o próprio
        # código. Muitos componentes têm nome genérico ("Footers 1") mas o código
        # menciona "instagram", "discord", "loading" etc. O termo de relevância
        # (campos vs código) é tratado na ordenação abaixo.
        like = f"%{q}%"
        where.append(
            "(c.name LIKE ? OR c.title LIKE ? OR c.description LIKE ? "
            " OR EXISTS (SELECT 1 FROM component_tags ctq JOIN tags tq "
            "            ON tq.id = ctq.tag_id "
            "            WHERE ctq.component_id = c.id AND tq.name LIKE ?) "
            " OR EXISTS (SELECT 1 FROM component_files cfq "
            "            WHERE cfq.component_id = c.id AND cfq.content LIKE ?))"
        )
        params += [like, like, like, like, like]
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

        # Prioridade de render: HTML/CSS (preview confiável) → React com demo →
        # React cru. Evita abrir o site na cara de componentes não renderizáveis.
        priority = (
            "CASE "
            "  WHEN s.framework LIKE '%HTML%' OR s.framework LIKE '%CSS%' THEN 0 "
            "  WHEN EXISTS (SELECT 1 FROM components d WHERE d.source_id = c.source_id "
            "               AND d.name = c.name || '-demo') THEN 1 "
            "  ELSE 2 END"
        )
        # Relevância da busca: casar no nome/título vem antes de casar só no código.
        relevance = ""
        if q:
            relevance = (
                "CASE WHEN c.name LIKE ? OR c.title LIKE ? THEN 0 ELSE 1 END, "
            )

        if sort == "random":
            # Embaralhamento estável por seed (mesma página → mesma ordem ao paginar),
            # mas ainda priorizando relevância e renderizáveis.
            order = f"ORDER BY {relevance}{priority}, (c.id * {int(seed)}) % 100003"
        elif sort == "name":
            order = f"ORDER BY {relevance}c.title, c.name"
        else:  # smart
            order = f"ORDER BY {relevance}{priority}, s.slug, c.name"

        # Params da relevância entram ANTES dos de LIMIT/OFFSET (que serão somados
        # ao chamar execute). O ORDER BY é avaliado após o WHERE, mas no SQLite os
        # placeholders são posicionais na ordem do texto: WHERE..., depois ORDER BY.
        order_params = [f"%{q}%", f"%{q}%"] if q else []
        rows = conn.execute(
            f"SELECT DISTINCT c.id, c.external_id, c.name, c.title, c.description, "
            f"c.canonical_category, c.is_demo, c.public_url, c.license, "
            f"s.slug AS source_slug, s.display_name AS source_name, s.framework "
            f"{base} {order} LIMIT ? OFFSET ?",
            params + order_params + [per_page, offset],
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
        # Para componentes React, anexa o código do "-demo" correspondente, quando
        # existir. O demo traz uma instância de uso pronta, usada para o preview.
        comp["demo_code"] = _find_demo_code(conn, r)
        return comp
    finally:
        conn.close()


def get_preview_data(external_id: str) -> dict | None:
    """
    Dados mínimos para o preview de um card: framework, fonte, o código do
    arquivo principal (preferindo HTML) e o demo. Mais leve que get_component.
    """
    conn = _connect()
    try:
        r = conn.execute(
            "SELECT c.id, c.name, c.source_id, s.slug AS source_slug, s.framework "
            "FROM components c JOIN sources s ON s.id = c.source_id "
            "WHERE c.external_id = ?",
            (external_id,),
        ).fetchone()
        if not r:
            return None

        files = [dict(f) for f in conn.execute(
            "SELECT path, type, content FROM component_files WHERE component_id = ?",
            (r["id"],),
        )]
        return {
            "external_id": external_id,
            "source_slug": r["source_slug"],
            "framework": r["framework"],
            "files": files,
            "demo_code": _find_demo_code(conn, r),
        }
    finally:
        conn.close()


def _find_demo_code(conn: sqlite3.Connection, row) -> str:
    """Busca o código do demo associado ('<name>-demo') na mesma fonte."""
    demo = conn.execute(
        "SELECT cf.content FROM components c "
        "JOIN component_files cf ON cf.component_id = c.id "
        "WHERE c.source_id = ? AND c.name = ? LIMIT 1",
        (row["source_id"], f"{row['name']}-demo"),
    ).fetchone()
    return demo[0] if demo else ""


def _attach_tags(conn: sqlite3.Connection, comp: dict) -> dict:
    comp["tags"] = [row[0] for row in conn.execute(
        "SELECT t.name FROM tags t JOIN component_tags ct ON ct.tag_id = t.id "
        "WHERE ct.component_id = ? ORDER BY t.name",
        (comp["id"],),
    )]
    return comp
