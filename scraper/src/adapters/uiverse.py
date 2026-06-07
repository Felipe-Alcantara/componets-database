from .base import SourceAdapter
from ..models import ComponentDTO, ComponentFile
from ..config import ScraperConfig
from ..git_clone import ensure_repo, read_text

REPO_URL = "https://github.com/uiverse-io/galaxy.git"
REPO_NAME = "uiverse-galaxy"

# Categorias = pastas de primeiro nível no repo
CATEGORIES = [
    "Buttons", "Cards", "Checkboxes", "Forms", "Inputs",
    "Loaders", "Notifications", "Patterns", "Radio-buttons",
    "Toggle-switches", "Tooltips",
]


class UniverseAdapter(SourceAdapter):
    slug = "uiverse"
    display_name = "Uiverse.io"
    framework = "HTML/CSS"
    license = "MIT"

    def collect(self, config: ScraperConfig) -> list[ComponentDTO]:
        repo = ensure_repo(REPO_URL, REPO_NAME)
        if not repo:
            print("  [uiverse] falha ao clonar, abortando")
            return []

        components = []
        for category in CATEGORIES:
            if len(components) >= config.max_components:
                break
            cat_dir = repo / category
            if not cat_dir.is_dir():
                # Algumas categorias podem ter capitalização diferente
                cat_dir = self._find_dir_case_insensitive(repo, category)
                if not cat_dir:
                    print(f"  [uiverse] categoria não encontrada: {category}")
                    continue

            html_files = sorted(cat_dir.glob("*.html"))
            print(f"  [uiverse] {category}: {len(html_files)} arquivos")

            for html_file in html_files:
                if len(components) >= config.max_components:
                    break
                content = read_text(html_file)
                if not content.strip():
                    continue
                name = html_file.stem

                components.append(ComponentDTO(
                    external_id=f"uiverse_{category.lower()}_{name}",
                    name=name,
                    source_slug=self.slug,
                    source_url=f"https://github.com/uiverse-io/galaxy/blob/main/{category}/{html_file.name}",
                    public_url=self.derive_public_url(name),
                    title=name.replace("-", " ").title(),
                    framework=self.framework,
                    category=category,
                    license=self.license,
                    files=[ComponentFile(
                        path=f"{category}/{html_file.name}",
                        content=content,
                        type="html",
                    )],
                    capture_source="git_clone",
                ))

        print(f"  [uiverse] total coletado: {len(components)}")
        return components

    def _find_dir_case_insensitive(self, repo, name: str):
        target = name.lower()
        for d in repo.iterdir():
            if d.is_dir() and d.name.lower() == target:
                return d
        return None

    def derive_public_url(self, name: str) -> str:
        return f"https://uiverse.io/elements/{name}"
