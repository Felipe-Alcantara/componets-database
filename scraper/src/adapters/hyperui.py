import re
from .base import SourceAdapter
from ..models import ComponentDTO, ComponentFile
from ..config import ScraperConfig
from ..git_clone import ensure_repo, read_text

REPO_URL = "https://github.com/markmead/hyperui.git"
REPO_NAME = "hyperui"
CONTENT_PATH = "src/content/collection"


class HyperUIAdapter(SourceAdapter):
    slug = "hyperui"
    display_name = "HyperUI"
    framework = "HTML/Tailwind"
    license = "MIT"

    def collect(self, config: ScraperConfig) -> list[ComponentDTO]:
        repo = ensure_repo(REPO_URL, REPO_NAME)
        if not repo:
            print("  [hyperui] falha ao clonar, abortando")
            return []

        components = []
        content_dir = repo / CONTENT_PATH
        if not content_dir.is_dir():
            print(f"  [hyperui] diretório não encontrado: {CONTENT_PATH}")
            return []

        for cat_dir in sorted([d for d in content_dir.iterdir() if d.is_dir()]):
            if len(components) >= config.max_components:
                break
            category = cat_dir.name
            mdx_files = sorted(cat_dir.glob("*.mdx"))
            print(f"  [hyperui] {category}: {len(mdx_files)} arquivos")

            for mdx in mdx_files:
                if len(components) >= config.max_components:
                    break
                content = read_text(mdx)
                dto = self._parse_mdx(content, mdx.stem, category)
                if dto:
                    components.append(dto)

        print(f"  [hyperui] total coletado: {len(components)}")
        return components

    def _parse_mdx(self, content: str, name: str, category: str) -> ComponentDTO | None:
        if not content:
            return None

        title = name
        description = ""
        fm_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if fm_match:
            fm = fm_match.group(1)
            t = re.search(r'title:\s*["\']?(.+?)["\']?\s*$', fm, re.MULTILINE)
            d = re.search(r'description:\s*["\']?(.+?)["\']?\s*$', fm, re.MULTILINE)
            if t:
                title = t.group(1).strip()
            if d:
                description = d.group(1).strip()

        code_blocks = re.findall(r"```(?:html|jsx|tsx|js)?\n(.*?)```", content, re.DOTALL)
        files = [
            ComponentFile(path=f"{name}_{i}.html", content=block, type="html")
            for i, block in enumerate(code_blocks)
            if block.strip()
        ]

        return ComponentDTO(
            external_id=f"hyperui_{category}_{name}",
            name=name,
            source_slug=self.slug,
            source_url=f"https://github.com/markmead/hyperui/blob/main/{CONTENT_PATH}/{category}/{name}.mdx",
            public_url=f"https://www.hyperui.dev/components/{category}/{name}",
            title=title,
            description=description,
            framework=self.framework,
            category=category,
            license=self.license,
            files=files,
            capture_source="git_clone",
        )
