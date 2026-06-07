import time
import httpx
from .base import SourceAdapter
from ..models import ComponentDTO, ComponentFile
from ..config import ScraperConfig

REGISTRY_INDEX = "https://magicui.design/registry.json"
COMPONENT_BASE = "https://magicui.design/r/{name}.json"


class MagicUIAdapter(SourceAdapter):
    slug = "magicui"
    display_name = "Magic UI"
    framework = "React"
    license = "MIT"

    def collect(self, config: ScraperConfig) -> list[ComponentDTO]:
        components = []

        with httpx.Client(timeout=config.timeout_ms / 1000, follow_redirects=True) as client:
            names = self._fetch_index(client)
            limit = min(config.max_components, len(names))
            print(f"  [magicui] {len(names)} componentes no índice, coletando {limit}")

            for name in names[:limit]:
                url = COMPONENT_BASE.format(name=name)
                try:
                    resp = client.get(url)
                    if resp.status_code != 200:
                        print(f"  [magicui] skip {name}: HTTP {resp.status_code}")
                        continue
                    data = resp.json()
                    dto = self._parse(data, url)
                    if dto:
                        components.append(dto)
                        print(f"  [magicui] ok {name}")
                except Exception as exc:
                    print(f"  [magicui] erro {name}: {exc}")

                time.sleep(config.request_delay)

        return components

    def _fetch_index(self, client: httpx.Client) -> list[str]:
        try:
            resp = client.get(REGISTRY_INDEX)
            data = resp.json()
            items = data.get("items", [])
            return [item["name"] for item in items if item.get("name")]
        except Exception as exc:
            print(f"  [magicui] erro ao buscar índice: {exc}")
            return []

    def _parse(self, data: dict, source_url: str) -> ComponentDTO | None:
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
            external_id=f"magicui_{name}",
            name=name,
            source_slug=self.slug,
            source_url=source_url,
            public_url=self.derive_public_url(source_url),
            title=data.get("title", name),
            description=data.get("description", ""),
            framework=self.framework,
            category=data.get("categories", [""])[0] if data.get("categories") else "",
            license=self.license,
            dependencies=data.get("dependencies", []),
            dev_dependencies=data.get("devDependencies", []),
            tags=data.get("categories", []),
            files=files,
            capture_source="registry_json",
        )

    def derive_public_url(self, source_url: str) -> str:
        name = source_url.rstrip("/").split("/")[-1].replace(".json", "")
        return f"https://magicui.design/docs/components/{name}"
