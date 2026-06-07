import re
from .base import SourceAdapter
from ..models import ComponentDTO, ComponentFile
from ..config import ScraperConfig
from ..git_clone import ensure_repo, read_text

REPO_URL = "https://github.com/markmead/hyperui.git"
REPO_NAME = "hyperui"
EXAMPLES_PATH = "public/examples"
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

        examples_dir = repo / EXAMPLES_PATH
        if not examples_dir.is_dir():
            print(f"  [hyperui] diretório não encontrado: {EXAMPLES_PATH}")
            return []

        components = []
        for cat_dir in sorted([d for d in examples_dir.iterdir() if d.is_dir()]):
            if len(components) >= config.max_components:
                break
            category = cat_dir.name

            for comp_dir in sorted([d for d in cat_dir.iterdir() if d.is_dir()]):
                if len(components) >= config.max_components:
                    break
                slug = comp_dir.name
                # Metadados (título/descrição) vêm do MDX correspondente, quando existe
                title, description = self._read_meta(repo, category, slug)

                # Pega as variantes "light" (1.html, 2.html...), ignorando *-dark
                html_files = sorted(
                    f for f in comp_dir.glob("*.html") if "-dark" not in f.stem
                )
                for html in html_files:
                    if len(components) >= config.max_components:
                        break
                    raw = read_text(html)
                    code = self._extract_body(raw)
                    if not code.strip():
                        continue
                    variant = html.stem  # "1", "2", ...

                    components.append(ComponentDTO(
                        external_id=f"hyperui_{category}_{slug}_{variant}",
                        name=f"{slug}-{variant}",
                        source_slug=self.slug,
                        source_url=f"https://github.com/markmead/hyperui/blob/main/{EXAMPLES_PATH}/{category}/{slug}/{html.name}",
                        public_url=f"https://www.hyperui.dev/components/{category}/{slug}",
                        title=f"{title} {variant}" if title else f"{slug} {variant}",
                        description=description,
                        framework=self.framework,
                        category=category,
                        license=self.license,
                        files=[ComponentFile(
                            path=f"{slug}-{variant}.html", content=code, type="html"
                        )],
                        capture_source="git_clone",
                    ))

        print(f"  [hyperui] total coletado: {len(components)}")
        return components

    def _read_meta(self, repo, category: str, slug: str) -> tuple[str, str]:
        """Lê title/description do frontmatter do MDX, se existir."""
        mdx = repo / CONTENT_PATH / category / f"{slug}.mdx"
        if not mdx.is_file():
            return "", ""
        content = read_text(mdx)
        fm = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not fm:
            return "", ""
        block = fm.group(1)
        t = re.search(r'title:\s*["\']?(.+?)["\']?\s*$', block, re.MULTILINE)
        d = re.search(r'description:\s*["\']?(.+?)["\']?\s*$', block, re.MULTILINE)
        return (t.group(1).strip() if t else ""), (d.group(1).strip() if d else "")

    def _extract_body(self, raw: str) -> str:
        """Extrai o conteúdo de <body>, descartando o boilerplate do HTML."""
        body = re.search(r"<body[^>]*>(.*?)</body>", raw, re.DOTALL | re.IGNORECASE)
        return body.group(1).strip() if body else raw.strip()
