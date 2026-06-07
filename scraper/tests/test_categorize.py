"""Testa a categorização canônica — unifica taxonomia entre fontes."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.categorize import canonical_category, category_tags, is_demo, CANONICAL


class TestCanonicalCategory(unittest.TestCase):
    def test_normaliza_caixa_e_idioma(self):
        # Buttons / buttons / button -> mesma categoria canônica
        self.assertEqual(canonical_category("button", "Buttons"), "button")
        self.assertEqual(canonical_category("primary-buttons", "buttons"), "button")
        self.assertEqual(canonical_category("btn-group", ""), "button")

    def test_deriva_pelo_nome_quando_categoria_vazia(self):
        # shadcn não traz categoria; deve inferir do nome
        self.assertEqual(canonical_category("accordion", ""), "accordion")
        self.assertEqual(canonical_category("alert-dialog", ""), "dialog")
        self.assertEqual(canonical_category("checkbox", ""), "checkbox")
        self.assertEqual(canonical_category("tooltip", ""), "tooltip")

    def test_categoria_generica_components_e_refinada_pelo_nome(self):
        # daisyui/originui usam "components" genérico; o nome desambigua
        self.assertEqual(canonical_category("card", "components"), "card")
        self.assertEqual(canonical_category("table", "components"), "table")

    def test_efeitos_e_animacoes(self):
        self.assertEqual(canonical_category("meteors", ""), "background")
        self.assertEqual(canonical_category("typewriter-effect", ""), "text-animation")
        self.assertEqual(canonical_category("card-spotlight", ""), "card")  # card vem antes

    def test_retorna_valor_da_taxonomia_conhecida(self):
        cat = canonical_category("globe", "")
        self.assertIn(cat, CANONICAL)

    def test_other_para_desconhecido(self):
        self.assertEqual(canonical_category("xyz-quux-foo", ""), "other")

    def test_is_demo(self):
        self.assertTrue(is_demo("magic-card-demo"))
        self.assertTrue(is_demo("border-beam-demo-2"))
        self.assertTrue(is_demo("index"))
        self.assertFalse(is_demo("magic-card"))
        self.assertFalse(is_demo("button"))


class TestCategoryTags(unittest.TestCase):
    def test_primaria_sempre_primeira(self):
        tags = category_tags("shimmer-button", "")
        self.assertEqual(tags[0], "button")

    def test_componente_multi_uso_recebe_facetas(self):
        # botão animado deve ter button + animation
        tags = category_tags("shimmer-button", "")
        self.assertIn("button", tags)
        self.assertIn("animation", tags)

    def test_theme_toggler_tem_toggle_animation_theme(self):
        tags = category_tags("animated-theme-toggler", "")
        self.assertIn("toggle", tags)
        self.assertIn("animation", tags)
        self.assertIn("theme", tags)

    def test_pricing_card_tem_card_e_pricing(self):
        tags = category_tags("pricing-cards-radio-group", "")
        self.assertIn("card", tags)
        self.assertIn("pricing", tags)

    def test_componente_simples_tem_uma_tag(self):
        tags = category_tags("button", "Buttons")
        self.assertEqual(tags, ["button"])

    def test_3d_card_recebe_faceta_3d(self):
        tags = category_tags("3d-card", "")
        self.assertIn("card", tags)
        self.assertIn("3d", tags)

    def test_sem_match_retorna_other(self):
        self.assertEqual(category_tags("xyz-quux", ""), ["other"])

    def test_tags_sem_duplicatas(self):
        tags = category_tags("animated-animated-button", "")
        self.assertEqual(len(tags), len(set(tags)))


if __name__ == "__main__":
    unittest.main()
