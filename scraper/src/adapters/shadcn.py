from .base import SourceAdapter
from ..models import ComponentDTO, ComponentFile
from ..config import ScraperConfig
from ..git_clone import ensure_repo, read_text

REPO_URL = "https://github.com/shadcn-ui/ui.git"
REPO_NAME = "shadcn-ui"
UI_PATH = "apps/v4/registry/new-york-v4/ui"


class ShadcnAdapter(SourceAdapter):
    slug = "shadcn"
    display_name = "shadcn/ui"
    framework = "React"
    license = "MIT"

    def collect(self, config: ScraperConfig) -> list[ComponentDTO]:
        repo = ensure_repo(REPO_URL, REPO_NAME)
        if not repo:
            print("  [shadcn] falha ao clonar, abortando")
            return []

        components = []
        ui_dir = repo / UI_PATH
        if not ui_dir.is_dir():
            print(f"  [shadcn] diretório não encontrado: {UI_PATH}")
            return []

        tsx_files = sorted([f for f in ui_dir.glob("*.tsx") if not f.name.startswith("_")])
        limit = min(config.max_components, len(tsx_files))
        print(f"  [shadcn] {len(tsx_files)} componentes encontrados, coletando {limit}")

        for f in tsx_files[:limit]:
            content = read_text(f)
            if not content.strip():
                continue
            name = f.stem

            components.append(ComponentDTO(
                external_id=f"shadcn_{name}",
                name=name,
                source_slug=self.slug,
                source_url=f"https://github.com/shadcn-ui/ui/blob/main/{UI_PATH}/{f.name}",
                public_url=f"https://ui.shadcn.com/docs/components/{name}",
                title=name.replace("-", " ").title(),
                framework=self.framework,
                license=self.license,
                files=[ComponentFile(
                    path=f"{UI_PATH}/{f.name}",
                    content=content,
                    type="registry:ui",
                )],
                capture_source="git_clone",
            ))

        print(f"  [shadcn] total coletado: {len(components)}")
        return components
