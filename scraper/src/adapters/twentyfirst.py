import time
import httpx
from .base import SourceAdapter
from ..models import ComponentDTO, ComponentFile
from ..config import ScraperConfig

# 21st.dev expõe componentes no formato shadcn registry
# O índice público lista componentes por autor/namespace
COMPONENT_BASE = "https://21st.dev/r/{author}/{name}"

# Componentes conhecidos do namespace principal
KNOWN_COMPONENTS = [
    ("shadcn", "accordion"), ("shadcn", "alert"), ("shadcn", "alert-dialog"),
    ("shadcn", "avatar"), ("shadcn", "badge"), ("shadcn", "button"),
    ("shadcn", "calendar"), ("shadcn", "card"), ("shadcn", "carousel"),
    ("shadcn", "checkbox"), ("shadcn", "collapsible"), ("shadcn", "command"),
    ("shadcn", "context-menu"), ("shadcn", "dialog"), ("shadcn", "drawer"),
    ("shadcn", "dropdown-menu"), ("shadcn", "form"), ("shadcn", "hover-card"),
    ("shadcn", "input"), ("shadcn", "label"), ("shadcn", "menubar"),
    ("shadcn", "navigation-menu"), ("shadcn", "pagination"), ("shadcn", "popover"),
    ("shadcn", "progress"), ("shadcn", "radio-group"), ("shadcn", "scroll-area"),
    ("shadcn", "select"), ("shadcn", "separator"), ("shadcn", "sheet"),
    ("shadcn", "skeleton"), ("shadcn", "slider"), ("shadcn", "switch"),
    ("shadcn", "table"), ("shadcn", "tabs"), ("shadcn", "textarea"),
    ("shadcn", "toast"), ("shadcn", "toggle"), ("shadcn", "tooltip"),
]


class TwentyFirstAdapter(SourceAdapter):
    slug = "21stdev"
    display_name = "21st.dev"
    framework = "React"
    license = "MIT"

    def collect(self, config: ScraperConfig) -> list[ComponentDTO]:
        components = []
        limit = min(config.max_components, len(KNOWN_COMPONENTS))

        with httpx.Client(timeout=config.timeout_ms / 1000, follow_redirects=True) as client:
            for author, name in KNOWN_COMPONENTS[:limit]:
                url = COMPONENT_BASE.format(author=author, name=name)
                try:
                    resp = client.get(url)
                    if resp.status_code != 200:
                        print(f"  [21stdev] skip {author}/{name}: HTTP {resp.status_code}")
                        continue
                    data = resp.json()
                    dto = self._parse(data, url, author)
                    if dto:
                        components.append(dto)
                        print(f"  [21stdev] ok {author}/{name}")
                except Exception as exc:
                    print(f"  [21stdev] erro {author}/{name}: {exc}")

                time.sleep(config.request_delay)

        return components

    def _parse(self, data: dict, source_url: str, author: str) -> ComponentDTO | None:
        name = data.get("name", "")
        if not name:
            return None

        files = [
            ComponentFile(
                path=f.get("path", ""),
                content=f.get("content", ""),
                type=f.get("type", ""),
            )
            for f in data.get("files", [])
        ]

        return ComponentDTO(
            external_id=f"21stdev_{author}_{name}",
            name=name,
            source_slug=self.slug,
            source_url=source_url,
            public_url=self.derive_public_url(source_url),
            title=data.get("title", name),
            description=data.get("description", ""),
            framework=self.framework,
            category=data.get("categories", [""])[0] if data.get("categories") else "",
            license=self.license,
            author=author,
            dependencies=data.get("dependencies", []),
            dev_dependencies=data.get("devDependencies", []),
            tags=data.get("categories", []),
            files=files,
            capture_source="registry_json",
        )

    def derive_public_url(self, source_url: str) -> str:
        # source_url é o endpoint da API (/r/{author}/{name}) — não é página.
        # A página pública do 21st é 21st.dev/{author}/{name}.
        parts = source_url.rstrip("/").split("/")
        if len(parts) >= 2:
            author, name = parts[-2], parts[-1]
            return f"https://21st.dev/{author}/{name}"
        return "https://21st.dev"
