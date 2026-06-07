"""Testa o registry de adapters — descoberta por slug e erro controlado."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.registry import get_adapter, list_sources, ADAPTERS


class TestRegistry(unittest.TestCase):
    def test_todas_as_fontes_esperadas_registradas(self):
        slugs = {s["slug"] for s in list_sources()}
        esperadas = {
            "shadcn", "magicui", "21stdev", "aceternity", "reactbits",
            "originui", "uiverse", "hyperui", "daisyui", "floatui",
        }
        self.assertEqual(slugs, esperadas)

    def test_get_adapter_retorna_instancia(self):
        adapter = get_adapter("magicui")
        self.assertEqual(adapter.slug, "magicui")
        self.assertTrue(hasattr(adapter, "collect"))

    def test_get_adapter_slug_desconhecido_levanta_erro(self):
        with self.assertRaises(ValueError):
            get_adapter("fonte-que-nao-existe")

    def test_cada_adapter_tem_metadados(self):
        for slug, adapter in ADAPTERS.items():
            self.assertTrue(adapter.slug, f"{slug} sem slug")
            self.assertTrue(adapter.display_name, f"{slug} sem display_name")
            self.assertTrue(adapter.license, f"{slug} sem license")


if __name__ == "__main__":
    unittest.main()
