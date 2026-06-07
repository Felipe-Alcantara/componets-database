import time
import httpx
from .base import SourceAdapter
from ..models import ComponentDTO, ComponentFile
from ..config import ScraperConfig

COMPONENT_BASE = "https://ui.aceternity.com/registry/{name}.json"

# Lista de componentes conhecidos do Aceternity UI
KNOWN_COMPONENTS = [
    "3d-card", "3d-marquee", "3d-pin", "animated-beam", "animated-gradient-text",
    "animated-list", "animated-modal", "animated-testimonials", "animated-tooltip",
    "aurora-background", "background-beams", "background-beams-with-collision",
    "background-boxes", "background-gradient", "background-lines",
    "bento-grid", "card-hover-effect", "card-spotlight", "card-stack",
    "compare", "container-scroll-animation", "container-text-flip",
    "cover", "direction-aware-hover", "evervault-card",
    "feature-sections", "file-upload", "floating-dock", "floating-navbar",
    "focus-cards", "following-pointer", "glare-card", "glowing-effect",
    "globe", "google-gemini-effect", "grid-and-dot-backgrounds",
    "hero-highlight", "hover-border-gradient", "images-slider",
    "infinite-moving-cards", "input", "label", "lamp",
    "layout-grid", "lens", "link-preview", "macbook-scroll",
    "meteors", "modal", "multi-step-loader", "navbar-menu",
    "number-ticker", "parallax-scroll", "placeholders-and-vanish-input",
    "resizable-navbar", "shooting-stars", "sidebar", "sparkles",
    "spotlight", "sticky-scroll-reveal", "svg-mask-effect", "tabs",
    "tailwindcss-buttons", "text-generate-effect", "text-hover-effect",
    "text-reveal-card", "timeline", "tracing-beam", "typewriter-effect",
    "vortex", "wavy-background", "wobble-card", "world-map",
]


class AceternityAdapter(SourceAdapter):
    slug = "aceternity"
    display_name = "Aceternity UI"
    framework = "React"
    license = "custom"

    def collect(self, config: ScraperConfig) -> list[ComponentDTO]:
        components = []
        limit = min(config.max_components, len(KNOWN_COMPONENTS))

        with httpx.Client(timeout=config.timeout_ms / 1000, follow_redirects=True) as client:
            for name in KNOWN_COMPONENTS[:limit]:
                url = COMPONENT_BASE.format(name=name)
                try:
                    resp = client.get(url)
                    if resp.status_code != 200:
                        print(f"  [aceternity] skip {name}: HTTP {resp.status_code}")
                        continue
                    data = resp.json()
                    dto = self._parse(data, url, name)
                    if dto:
                        components.append(dto)
                        print(f"  [aceternity] ok {name}")
                except Exception as exc:
                    print(f"  [aceternity] erro {name}: {exc}")

                time.sleep(config.request_delay)

        return components

    def _parse(self, data: dict, source_url: str, slug: str) -> ComponentDTO | None:
        name = data.get("name", slug)
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
            external_id=f"aceternity_{name}",
            name=name,
            source_slug=self.slug,
            source_url=source_url,
            public_url=self.derive_public_url(source_url),
            title=data.get("title", name),
            description=data.get("description", ""),
            framework=self.framework,
            category=data.get("category", ""),
            license=self.license,
            author=data.get("author", "aceternity"),
            dependencies=data.get("dependencies", []),
            dev_dependencies=data.get("devDependencies", []),
            files=files,
            capture_source="registry_json",
        )

    def derive_public_url(self, source_url: str) -> str:
        name = source_url.rstrip("/").split("/")[-1].replace(".json", "")
        return f"https://ui.aceternity.com/components/{name}"
