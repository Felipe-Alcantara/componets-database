"""
Esquema relacional do banco de componentes.

Modelo normalizado com chaves estrangeiras e índices:

    sources (1) ──< (N) components (N) >──< (N) tags     [via component_tags]
                              (1) ──< (N) component_files

Em vez de listas embutidas como JSON, tags e arquivos viram tabelas próprias
com FK, permitindo JOINs indexados em vez de LIKE sobre texto.
"""
import sqlite3
from pathlib import Path

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sources (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    slug         TEXT UNIQUE NOT NULL,
    display_name TEXT,
    framework    TEXT,
    license      TEXT
);

CREATE TABLE IF NOT EXISTS components (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id        TEXT UNIQUE NOT NULL,
    source_id          INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    name               TEXT NOT NULL,
    title              TEXT,
    description        TEXT,
    source_url         TEXT,
    public_url         TEXT,
    category           TEXT,
    canonical_category TEXT,
    is_demo            INTEGER NOT NULL DEFAULT 0,
    license            TEXT,
    author             TEXT,
    capture_source     TEXT,
    preview_image      TEXT,
    first_seen_at      TEXT,
    last_seen_at       TEXT
);

CREATE TABLE IF NOT EXISTS tags (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS component_tags (
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    tag_id       INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (component_id, tag_id)
);

CREATE TABLE IF NOT EXISTS component_files (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    path         TEXT,
    type         TEXT,
    content      TEXT
);

CREATE TABLE IF NOT EXISTS component_dependencies (
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    name         TEXT NOT NULL,
    is_dev       INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (component_id, name, is_dev)
);

-- Índices para as buscas comuns (evitam full table scan)
CREATE INDEX IF NOT EXISTS idx_components_source       ON components(source_id);
CREATE INDEX IF NOT EXISTS idx_components_canonical    ON components(canonical_category);
CREATE INDEX IF NOT EXISTS idx_components_is_demo      ON components(is_demo);
CREATE INDEX IF NOT EXISTS idx_components_name         ON components(name);
CREATE INDEX IF NOT EXISTS idx_component_tags_tag      ON component_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_component_files_comp    ON component_files(component_id);
CREATE INDEX IF NOT EXISTS idx_component_deps_comp     ON component_dependencies(component_id);
"""


def init_db(db_path: Path) -> sqlite3.Connection:
    """Cria o banco com o esquema relacional (idempotente) e retorna a conexão."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def get_or_create_source(conn: sqlite3.Connection, slug: str, display_name: str = "",
                         framework: str = "", license: str = "") -> int:
    """Retorna o id da fonte, inserindo-a se ainda não existir."""
    row = conn.execute("SELECT id FROM sources WHERE slug = ?", (slug,)).fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO sources (slug, display_name, framework, license) VALUES (?,?,?,?)",
        (slug, display_name, framework, license),
    )
    return cur.lastrowid


def get_or_create_tag(conn: sqlite3.Connection, name: str) -> int:
    """Retorna o id da tag, inserindo-a se ainda não existir."""
    row = conn.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
    if row:
        return row[0]
    cur = conn.execute("INSERT INTO tags (name) VALUES (?)", (name,))
    return cur.lastrowid
