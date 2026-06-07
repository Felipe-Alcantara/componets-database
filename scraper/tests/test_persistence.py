"""Testa persistência relacional: upsert idempotente, FKs, tags e arquivos."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models import ComponentDTO, ComponentFile
from src.persistence import persist_components
from src.schema import init_db


def make_dto(external_id="test_1", name="shimmer-button") -> ComponentDTO:
    return ComponentDTO(
        external_id=external_id,
        name=name,
        source_slug="test",
        source_url="https://example.com/button",
        public_url="https://example.com/docs/button",
        title="Shimmer Button",
        framework="React",
        license="MIT",
        dependencies=["motion"],
        files=[ComponentFile(path="button.tsx", content="export const B = () => null", type="ui")],
        capture_source="test",
    )


class TestRelationalPersistence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "components.db"
        self.json = Path(self.tmp.name) / "out.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _conn(self):
        return init_db(self.db)

    def _count(self, table) -> int:
        conn = self._conn()
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        conn.close()
        return n

    def test_cria_linha_em_components_e_sources(self):
        persist_components([make_dto()], self.db, self.json, commit=True)
        self.assertEqual(self._count("components"), 1)
        self.assertEqual(self._count("sources"), 1)

    def test_upsert_idempotente_nao_duplica(self):
        dto = make_dto()
        persist_components([dto], self.db, self.json, commit=True)
        persist_components([dto], self.db, self.json, commit=True)
        self.assertEqual(self._count("components"), 1)
        # source também não duplica
        self.assertEqual(self._count("sources"), 1)

    def test_segunda_rodada_e_update(self):
        dto = make_dto()
        s1 = persist_components([dto], self.db, self.json, commit=True)
        s2 = persist_components([dto], self.db, self.json, commit=True)
        self.assertEqual(s1.created, 1)
        self.assertEqual(s2.updated, 1)
        self.assertEqual(s2.created, 0)

    def test_grava_tags_de_faceta(self):
        # shimmer-button -> button, effect, animation
        persist_components([make_dto()], self.db, self.json, commit=True)
        conn = self._conn()
        tags = {r[0] for r in conn.execute("SELECT name FROM tags").fetchall()}
        conn.close()
        self.assertIn("button", tags)
        self.assertIn("animation", tags)

    def test_grava_arquivos_e_dependencias(self):
        persist_components([make_dto()], self.db, self.json, commit=True)
        self.assertEqual(self._count("component_files"), 1)
        self.assertEqual(self._count("component_dependencies"), 1)

    def test_update_nao_duplica_relacoes_filhas(self):
        dto = make_dto()
        persist_components([dto], self.db, self.json, commit=True)
        persist_components([dto], self.db, self.json, commit=True)
        # arquivos e tags são recriados, não acumulados
        self.assertEqual(self._count("component_files"), 1)

    def test_integridade_referencial(self):
        persist_components([make_dto()], self.db, self.json, commit=True)
        conn = self._conn()
        fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        conn.close()
        self.assertEqual(len(fk_errors), 0)
        self.assertEqual(integrity, "ok")

    def test_dry_run_nao_grava(self):
        persist_components([make_dto()], self.db, self.json, commit=False)
        self.assertEqual(self._count("components"), 0)


if __name__ == "__main__":
    unittest.main()
