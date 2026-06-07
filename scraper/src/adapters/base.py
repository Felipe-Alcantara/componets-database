from abc import ABC, abstractmethod
from ..models import ComponentDTO
from ..config import ScraperConfig


class SourceAdapter(ABC):
    slug: str = ""
    display_name: str = ""
    framework: str = ""
    license: str = ""

    @abstractmethod
    def collect(self, config: ScraperConfig) -> list[ComponentDTO]:
        """Coleta todos os componentes desta fonte."""

    def derive_public_url(self, source_url: str) -> str:
        return source_url
