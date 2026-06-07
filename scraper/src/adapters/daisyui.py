from .base import SourceAdapter
from ..models import ComponentDTO, ComponentFile
from ..config import ScraperConfig
from ..git_clone import ensure_repo, read_text

REPO_URL = "https://github.com/saadeghi/daisyui.git"
REPO_NAME = "daisyui"
COMPONENTS_PATH = "packages/daisyui/src/components"


class DaisyUIAdapter(SourceAdapter):
    slug = "daisyui"
    display_name = "DaisyUI"
    framework = "HTML/CSS (Tailwind)"
    license = "MIT"

    def collect(self, config: ScraperConfig) -> list[ComponentDTO]:
        repo = ensure_repo(REPO_URL, REPO_NAME)
        if not repo:
            print("  [daisyui] falha ao clonar, abortando")
            return []

        components = []
        comp_dir = repo / COMPONENTS_PATH
        if not comp_dir.is_dir():
            print(f"  [daisyui] diretório não encontrado: {COMPONENTS_PATH}")
            return []

        css_files = sorted(comp_dir.glob("*.css"))
        limit = min(config.max_components, len(css_files))
        print(f"  [daisyui] {len(css_files)} componentes encontrados, coletando {limit}")

        for css in css_files[:limit]:
            content = read_text(css)
            if not content.strip():
                continue
            name = css.stem

            components.append(ComponentDTO(
                external_id=f"daisyui_{name}",
                name=name,
                source_slug=self.slug,
                source_url=f"https://github.com/saadeghi/daisyui/blob/main/{COMPONENTS_PATH}/{css.name}",
                public_url=f"https://daisyui.com/components/{name}/",
                title=name.replace("-", " ").title(),
                framework=self.framework,
                category="components",
                license=self.license,
                files=[ComponentFile(
                    path=f"{COMPONENTS_PATH}/{css.name}",
                    content=content,
                    type="css",
                )],
                capture_source="git_clone",
            ))

        print(f"  [daisyui] total coletado: {len(components)}")
        return components
