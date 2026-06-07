import re
from .base import SourceAdapter
from ..models import ComponentDTO, ComponentFile
from ..config import ScraperConfig
from ..git_clone import ensure_repo, read_text

REPO_URL = "https://github.com/saadeghi/daisyui.git"
REPO_NAME = "daisyui"
COMPONENTS_PATH = "packages/daisyui/src/components"
DOCS_PATH = "packages/docs/src/routes/(routes)/components"


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

        comp_dir = repo / COMPONENTS_PATH
        docs_dir = repo / DOCS_PATH
        if not comp_dir.is_dir():
            print(f"  [daisyui] diretório não encontrado: {COMPONENTS_PATH}")
            return []

        css_files = sorted(comp_dir.glob("*.css"))
        limit = min(config.max_components, len(css_files))
        print(f"  [daisyui] {len(css_files)} componentes encontrados, coletando {limit}")

        components = []
        for css in css_files[:limit]:
            name = css.stem
            css_content = read_text(css)
            # Exemplo de uso (HTML) vindo da doc — é o que renderiza no preview
            example = self._read_example(docs_dir, name)

            files = []
            if example:
                files.append(ComponentFile(path=f"{name}.html", content=example, type="html"))
            if css_content.strip():
                files.append(ComponentFile(path=f"{name}.css", content=css_content, type="css"))
            if not files:
                continue

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
                files=files,
                capture_source="git_clone",
            ))
            print(f"  [daisyui] ok {name}{'  (com exemplo)' if example else '  (só css)'}")

        print(f"  [daisyui] total coletado: {len(components)}")
        return components

    def _read_example(self, docs_dir, name: str) -> str:
        """Extrai o primeiro bloco HTML de exemplo da doc do componente."""
        page = self._find_doc(docs_dir, name)
        if not page:
            return ""
        content = read_text(page)
        blocks = re.findall(r"```html\n(.*?)```", content, re.DOTALL)
        for block in blocks:
            code = block.strip()
            if code:
                # Remove o prefixo de namespace do build ($$btn -> btn)
                return code.replace("$$", "")
        return ""

    def _find_doc(self, docs_dir, name: str):
        """
        Acha o +page.md do componente. O nome do CSS (ex: 'fileinput',
        'radialprogress') às vezes difere da pasta da doc ('file-input',
        'radial-progress') ou tem variantes ('mockup' -> 'mockup-browser').
        """
        # 1) match direto
        page = docs_dir / name / "+page.md"
        if page.is_file():
            return page
        if not docs_dir.is_dir():
            return None
        # 2) match ignorando hífens (fileinput == file-input)
        target = name.replace("-", "")
        candidates = []
        for d in docs_dir.iterdir():
            if not d.is_dir():
                continue
            norm = d.name.replace("-", "")
            if norm == target:
                return d / "+page.md"
            if norm.startswith(target) or target.startswith(norm):
                candidates.append(d)
        # 3) primeira variante que começa com o nome (mockup -> mockup-browser)
        for d in sorted(candidates):
            p = d / "+page.md"
            if p.is_file():
                return p
        return None
