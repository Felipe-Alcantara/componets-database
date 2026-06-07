from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class ScraperConfig:
    headless: bool = os.getenv("SCRAPER_HEADLESS", "1") != "0"
    max_components: int = int(os.getenv("SCRAPER_MAX_COMPONENTS", "500"))
    max_pages: int = int(os.getenv("SCRAPER_MAX_PAGES", "10"))
    timeout_ms: int = int(os.getenv("SCRAPER_TIMEOUT_MS", "30000"))
    dry_run: bool = os.getenv("SCRAPER_DRY_RUN", "1") != "0"
    request_delay: float = float(os.getenv("SCRAPER_REQUEST_DELAY", "0.5"))
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    debug_dir: Path = Path(os.getenv("SCRAPER_DEBUG_DIR", "debug_html"))
    data_dir: Path = Path(os.getenv("SCRAPER_DATA_DIR", "data"))


DEFAULT_CONFIG = ScraperConfig()
