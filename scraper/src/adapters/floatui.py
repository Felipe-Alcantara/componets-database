import re
from .base import SourceAdapter
from ..models import ComponentDTO
from ..config import ScraperConfig
from ..git_clone import ensure_repo, read_text

REPO_URL = "https://github.com/Float-UI/floatui-oss.git"
REPO_NAME = "floatui"
DB_PATH = "componentsDB"

# IMPORTANTE: o Float UI tem licença que proíbe redistribuir os componentes
# como itens standalone. Este adapter coleta APENAS metadados (título,
# categoria, slug, id, link público) e NUNCA o código do componente.
# O código fica no campo `ltr` do frontmatter, que é deliberadamente ignorado.


class FloatUIAdapter(SourceAdapter):
    slug = "floatui"
    display_name = "Float UI"
    framework = "React/HTML (Tailwind)"
    license = "proprietary (metadados apenas)"

    def collect(self, config: ScraperConfig) -> list[ComponentDTO]:
        repo = ensure_repo(REPO_URL, REPO_NAME)
        if not repo:
            print("  [floatui] falha ao clonar, abortando")
            return []

        components = []
        db_dir = repo / DB_PATH
        if not db_dir.is_dir():
            print(f"  [floatui] diretório não encontrado: {DB_PATH}")
            return []

        for cat_dir in sorted([d for d in db_dir.iterdir() if d.is_dir()]):
            if len(components) >= config.max_components:
                break
            category = cat_dir.name
            mdx_files = sorted(cat_dir.glob("*.mdx"))
            print(f"  [floatui] {category}: {len(mdx_files)} arquivos (só metadados)")

            for mdx in mdx_files:
                if len(components) >= config.max_components:
                    break
                meta = self._extract_metadata(read_text(mdx))
                if not meta:
                    continue
                name = mdx.stem

                components.append(ComponentDTO(
                    external_id=f"floatui_{category}_{name}",
                    name=name,
                    source_slug=self.slug,
                    source_url=f"https://github.com/Float-UI/floatui-oss/blob/main/{DB_PATH}/{category}/{mdx.name}",
                    public_url=self.derive_public_url(meta.get("slug", "")),
                    title=meta.get("title", name),
                    description="",
                    framework=self.framework,
                    category=category,
                    license=self.license,
                    # files=[] propositalmente vazio: não redistribuímos o código
                    files=[],
                    capture_source="git_clone_metadata_only",
                    extras={
                        "paid": meta.get("paid", ""),
                        "slug": meta.get("slug", ""),
                        "floatui_id": meta.get("id", ""),
                        "note": "metadados apenas; código não coletado por restrição de licença",
                    },
                ))

        print(f"  [floatui] total coletado (metadados): {len(components)}")
        return components

    def _extract_metadata(self, content: str) -> dict:
        """Extrai apenas campos seguros do frontmatter, ignorando o código (campo ltr)."""
        if not content:
            return {}
        fm_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            return {}
        fm = fm_match.group(1)

        meta = {}
        # Campos simples de uma linha (evita o campo ltr, que é um JSON gigante com código)
        for field in ("title", "category", "paid", "slug", "id"):
            m = re.search(rf"^{field}:\s*(.+?)\s*$", fm, re.MULTILINE)
            if m:
                value = m.group(1).strip()
                # Ignora se a "linha" começar como JSON (não é um campo simples)
                if not value.startswith("{"):
                    meta[field] = value
        return meta

    def derive_public_url(self, slug: str) -> str:
        if slug:
            return f"https://floatui.com/components{slug}"
        return "https://floatui.com/components"
