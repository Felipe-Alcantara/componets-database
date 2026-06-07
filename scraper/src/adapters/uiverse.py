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

            # Título legível baseado na categoria (singular) + número sequencial.
            # Os nomes do Uiverse são slugs aleatórios do autor (ex: "hungry-penguin-30"),
            # que não dizem nada — então o título usa "Button 1", "Card 2", etc.
            singular = self._singular(category)

            for idx, html_file in enumerate(html_files, start=1):
                if len(components) >= config.max_components:
                    break
                content = read_text(html_file)
                if not content.strip():
                    continue
                name = html_file.stem
                author = name.split("_", 1)[0] if "_" in name else ""

                # O Uiverse não expõe uma URL pública determinística por elemento
                # (a numeração do arquivo não bate com a do site → 404). O link
                # confiável é o arquivo no GitHub, que sempre existe e mostra o código.
                gh_url = f"https://github.com/uiverse-io/galaxy/blob/main/{category}/{html_file.name}"
                components.append(ComponentDTO(
                    external_id=f"uiverse_{category.lower()}_{name}",
                    name=name,
                    source_slug=self.slug,
                    source_url=gh_url,
                    public_url=gh_url,
                    title=f"{singular} {idx}",
                    framework=self.framework,
                    category=category,
                    license=self.license,
                    author=author,
                    files=[ComponentFile(
                        path=f"{category}/{html_file.name}",
                        content=content,
                        type="html",
                    )],
                    capture_source="git_clone",
                ))

        print(f"  [uiverse] total coletado: {len(components)}")
        return components

    def _singular(self, category: str) -> str:
        """Converte a categoria para um rótulo singular legível."""
        base = category.replace("-", " ").strip().title()
        # Plurais comuns do Uiverse
        specials = {
            "Toggle Switches": "Toggle Switch",
            "Radio Buttons": "Radio Button",
            "Loaders": "Loader",
            "Patterns": "Pattern",
        }
        if base in specials:
            return specials[base]
        if base.endswith("es") and base[:-2].endswith(("x", "ch", "sh", "s")):
            return base[:-2]
        if base.endswith("s"):
            return base[:-1]
        return base

    def _find_dir_case_insensitive(self, repo, name: str):
        target = name.lower()
        for d in repo.iterdir():
            if d.is_dir() and d.name.lower() == target:
                return d
        return None

    def derive_public_url(self, name: str) -> str:
        return f"https://uiverse.io/elements/{name}"
