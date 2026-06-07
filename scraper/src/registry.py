from .adapters.shadcn import ShadcnAdapter
from .adapters.magicui import MagicUIAdapter
from .adapters.twentyfirst import TwentyFirstAdapter
from .adapters.aceternity import AceternityAdapter
from .adapters.reactbits import ReactBitsAdapter
from .adapters.originui import OriginUIAdapter
from .adapters.uiverse import UniverseAdapter
from .adapters.hyperui import HyperUIAdapter
from .adapters.daisyui import DaisyUIAdapter
from .adapters.floatui import FloatUIAdapter

ADAPTERS = {
    ShadcnAdapter.slug: ShadcnAdapter(),
    MagicUIAdapter.slug: MagicUIAdapter(),
    TwentyFirstAdapter.slug: TwentyFirstAdapter(),
    AceternityAdapter.slug: AceternityAdapter(),
    ReactBitsAdapter.slug: ReactBitsAdapter(),
    OriginUIAdapter.slug: OriginUIAdapter(),
    UniverseAdapter.slug: UniverseAdapter(),
    HyperUIAdapter.slug: HyperUIAdapter(),
    DaisyUIAdapter.slug: DaisyUIAdapter(),
    FloatUIAdapter.slug: FloatUIAdapter(),
}


def get_adapter(slug: str):
    try:
        return ADAPTERS[slug]
    except KeyError as exc:
        known = ", ".join(sorted(ADAPTERS))
        raise ValueError(f"Fonte desconhecida: '{slug}'. Fontes disponíveis: {known}") from exc


def list_sources() -> list[dict]:
    return [
        {
            "slug": a.slug,
            "name": a.display_name,
            "framework": a.framework,
            "license": a.license,
        }
        for a in ADAPTERS.values()
    ]
