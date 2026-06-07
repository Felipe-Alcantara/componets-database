from .base import SourceAdapter
from ..models import ComponentDTO, ComponentFile
from ..config import ScraperConfig
from ..git_clone import ensure_repo, read_text

REPO_URL = "https://github.com/origin-space/originui.git"
REPO_NAME = "originui"
COMPONENTS_PATH = "packages/ui/src/components"


class OriginUIAdapter(SourceAdapter):
    slug = "originui"
    display_name = "Origin UI"
    framework = "React"
    license = "MIT"

    def collect(self, config: ScraperConfig) -> list[ComponentDTO]:
        repo = ensure_repo(REPO_URL, REPO_NAME)
        if not repo:
            print("  [originui] falha ao clonar, abortando")
            return []

        components = []
        comp_dir = repo / COMPONENTS_PATH
        if not comp_dir.is_dir():
            print(f"  [originui] diretório não encontrado: {COMPONENTS_PATH}")
            return []

        tsx_files = sorted([f for f in comp_dir.glob("*.tsx") if not f.name.startswith("_")])
        tsx_files += sorted([f for f in comp_dir.glob("*.ts") if not f.name.startswith("_")])
        limit = min(config.max_components, len(tsx_files))
        print(f"  [originui] {len(tsx_files)} componentes encontrados, coletando {limit}")

        for f in tsx_files[:limit]:
            content = read_text(f)
            if not content.strip():
                continue
            name = f.stem

            components.append(ComponentDTO(
                external_id=f"originui_{name}",
                name=name,
                source_slug=self.slug,
                source_url=f"https://github.com/origin-space/originui/blob/main/{COMPONENTS_PATH}/{f.name}",
                public_url=f"https://originui.com/components/{name}",
                title=name.replace("-", " ").title(),
                framework=self.framework,
                category="components",
                license=self.license,
                files=[ComponentFile(
                    path=f"{COMPONENTS_PATH}/{f.name}",
                    content=content,
                    type="registry:component",
                )],
                capture_source="git_clone",
            ))

        print(f"  [originui] total coletado: {len(components)}")
        return components
