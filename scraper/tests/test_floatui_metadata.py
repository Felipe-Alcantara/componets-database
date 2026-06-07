"""
Testa que o adapter do Float UI extrai SÓ metadados e NUNCA o código.

Crítico para conformidade de licença: o Float UI proíbe redistribuir os componentes,
então o código (campo `ltr` do frontmatter) deve ser sempre descartado.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.adapters.floatui import FloatUIAdapter

FIXTURE = Path(__file__).parent / "fixtures" / "floatui_sample.mdx"


class TestFloatUIMetadata(unittest.TestCase):
    def setUp(self):
        self.adapter = FloatUIAdapter()
        self.content = FIXTURE.read_text(encoding="utf-8")
        self.meta = self.adapter._extract_metadata(self.content)

    def test_extrai_campos_seguros(self):
        self.assertEqual(self.meta.get("title"), "Buttons with icons")
        self.assertEqual(self.meta.get("category"), "Application")
        self.assertEqual(self.meta.get("slug"), "/buttons")
        self.assertEqual(self.meta.get("id"), "24eced77-46a5-4c86-898d-5fbbbed09f14")

    def test_nao_extrai_o_campo_ltr_com_codigo(self):
        # O campo `ltr` (JSON gigante com o código) NÃO pode ser capturado
        self.assertNotIn("ltr", self.meta)

    def test_metadados_nao_contem_o_codigo_do_componente(self):
        # Nenhum valor de metadado pode conter o código sanitizado da fixture
        blob = " ".join(str(v) for v in self.meta.values())
        self.assertNotIn("SEGREDO-NAO-DEVE-VAZAR", blob)
        self.assertNotIn("SEGREDO-PREVIEW", blob)

    def test_derive_public_url(self):
        url = self.adapter.derive_public_url("/buttons")
        self.assertEqual(url, "https://floatui.com/components/buttons")


if __name__ == "__main__":
    unittest.main()
