from .base import SourceAdapter
from ..models import ComponentDTO, ComponentFile
from ..config import ScraperConfig
from ..git_clone import ensure_repo, read_text

REPO_URL = "https://github.com/DavidHDev/react-bits.git"
REPO_NAME = "react-bits"
BASE_PATH = "src/ts-tailwind"
CATEGORIES = ["Animations", "Backgrounds", "Components", "TextAnimations"]


class ReactBitsAdapter(SourceAdapter):
    slug = "reactbits"
    display_name = "React Bits"
    framework = "React"
    license = "MIT+Commons Clause"

    def collect(self, config: ScraperConfig) -> list[ComponentDTO]:
        repo = ensure_repo(REPO_URL, REPO_NAME)
        if not repo:
            print("  [reactbits] falha ao clonar, abortando")
            return []

        components = []
        base = repo / BASE_PATH
        for category in CATEGORIES:
            if len(components) >= config.max_components:
                break
            cat_dir = base / category
            if not cat_dir.is_dir():
                continue

            comp_dirs = sorted([d for d in cat_dir.iterdir() if d.is_dir()])
            print(f"  [reactbits] {category}: {len(comp_dirs)} componentes")

            for comp_dir in comp_dirs:
                if len(components) >= config.max_components:
                    break
                files = []
                for f in sorted(comp_dir.glob("*")):
                    if f.suffix in (".tsx", ".ts", ".css"):
                        content = read_text(f)
                        if content.strip():
                            files.append(ComponentFile(
                                path=f"{BASE_PATH}/{category}/{comp_dir.name}/{f.name}",
                                content=content,
                                type="registry:component",
                            ))
                if not files:
                    continue

                name = comp_dir.name
                components.append(ComponentDTO(
                    external_id=f"reactbits_{name}",
                    name=name,
                    source_slug=self.slug,
                    source_url=f"https://github.com/DavidHDev/react-bits/tree/main/{BASE_PATH}/{category}/{name}",
                    public_url="https://reactbits.dev",
                    title=name,
                    framework=self.framework,
                    category=category,
                    license=self.license,
                    files=files,
                    capture_source="git_clone",
                ))

        print(f"  [reactbits] total coletado: {len(components)}")
        return components
