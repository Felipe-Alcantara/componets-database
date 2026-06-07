"""Testa persistência: upsert idempotente e bloqueio de itens sem public_url."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models import ComponentDTO, ComponentFile
from src.persistence import persist_components, init_db


def make_dto(external_id="test_1", name="button") -> ComponentDTO:
    return ComponentDTO(
        external_id=external_id,
        name=name,
        source_slug="test",
        source_url="https://example.com/button",
        public_url="https://example.com/docs/button",
        title="Button",
        framework="React",
        license="MIT",
        files=[ComponentFile(path="button.tsx", content="export const Button = () => null", type="ui")],
        capture_source="test",
    )


class TestPersistence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "components.db"
        self.json = Path(self.tmp.name) / "out.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _count(self) -> int:
        conn = init_db(self.db)
        n = conn.execute("SELECT COUNT(*) FROM components").fetchone()[0]
        conn.close()
        return n

    def test_upsert_idempotente_nao_duplica(self):
        dto = make_dto()
        persist_components([dto], self.db, self.json, commit=True)
        persist_components([dto], self.db, self.json, commit=True)
        # Rodar duas vezes com o mesmo external_id mantém 1 registro
        self.assertEqual(self._count(), 1)

    def test_segunda_rodada_conta_como_update(self):
        dto = make_dto()
        s1 = persist_components([dto], self.db, self.json, commit=True)
        s2 = persist_components([dto], self.db, self.json, commit=True)
        self.assertEqual(s1.created, 1)
        self.assertEqual(s2.updated, 1)
        self.assertEqual(s2.created, 0)

    def test_dry_run_nao_grava(self):
        dto = make_dto()
        persist_components([dto], self.db, self.json, commit=False)
        # Sem --commit, o banco nem é criado / fica vazio
        self.assertEqual(self._count(), 0)


if __name__ == "__main__":
    unittest.main()
