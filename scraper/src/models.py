from dataclasses import dataclass, field


@dataclass
class ComponentFile:
    path: str
    content: str
    type: str = ""


@dataclass
class ComponentDTO:
    external_id: str
    name: str
    source_slug: str
    source_url: str
    public_url: str = ""
    title: str = ""
    description: str = ""
    framework: str = ""
    category: str = ""
    canonical_category: str = ""
    license: str = ""
    author: str = ""
    dependencies: list[str] = field(default_factory=list)
    dev_dependencies: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    files: list[ComponentFile] = field(default_factory=list)
    preview_image: str = ""
    capture_source: str = ""
    extras: dict = field(default_factory=dict)


@dataclass
class ImportSummary:
    mode: str = "preview"
    sources_seen: int = 0
    components_seen: int = 0
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    duplicates: int = 0
    blocked: int = 0
    errors: int = 0

    def report(self) -> dict:
        return {
            "mode": self.mode,
            "sources_seen": self.sources_seen,
            "components_seen": self.components_seen,
            "created": self.created,
            "updated": self.updated,
            "unchanged": self.unchanged,
            "duplicates": self.duplicates,
            "blocked": self.blocked,
            "errors": self.errors,
        }
