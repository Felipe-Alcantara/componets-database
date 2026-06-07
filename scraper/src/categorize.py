"""
Categorização canônica de componentes.

Cada fonte usa sua própria taxonomia (capitalização, idioma e granularidade
diferentes), e algumas não trazem categoria nenhuma. Este módulo deriva uma
`canonical_category` unificada a partir do nome do componente e da categoria
original, para permitir filtro consistente entre todas as fontes.

A categoria original é sempre preservada; a canônica é um campo adicional.
"""
import re

# Taxonomia canônica: rótulos estáveis usados para filtrar entre fontes.
# A ordem importa — regras mais específicas vêm antes das genéricas.
CANONICAL = [
    "button", "input", "form", "checkbox", "radio", "toggle", "select",
    "card", "table", "modal", "dialog", "tooltip", "popover", "dropdown",
    "menu", "navbar", "sidebar", "tabs", "accordion", "carousel", "pagination",
    "badge", "alert", "notification", "avatar", "loader", "progress",
    "background", "text-animation", "animation", "hero", "pricing",
    "testimonial", "footer", "newsletter", "calendar", "chart", "breadcrumb",
    "slider", "skeleton", "pattern", "effect", "section", "layout",
    "cursor", "device-mockup", "text", "other",
]

# Mapa de palavra-chave (no nome ou categoria, em minúsculas) -> canônica.
# A primeira regra que casar define a categoria.
_RULES: list[tuple[str, str]] = [
    # Botões
    (r"\bbutton", "button"),
    (r"\bbtn\b", "button"),
    # Inputs e campos
    (r"input", "input"),
    (r"\bfield\b", "input"),
    (r"textarea", "input"),
    (r"\bkbd\b", "input"),
    # Formulários e controles
    (r"\bform\b", "form"),
    (r"checkbox", "checkbox"),
    (r"radio", "radio"),
    (r"toggle|switch", "toggle"),
    (r"select|combobox", "select"),
    # Contêineres
    (r"\bcard", "card"),
    (r"\btable", "table"),
    (r"\bmodal", "modal"),
    (r"dialog|drawer|sheet", "dialog"),
    (r"tooltip", "tooltip"),
    (r"popover|hover-card", "popover"),
    (r"dropdown", "dropdown"),
    (r"context-menu|menubar|\bmenu\b|command", "menu"),
    (r"navbar|navigation", "navbar"),
    (r"sidebar", "sidebar"),
    (r"\btabs?\b", "tabs"),
    (r"accordion|collapsible", "accordion"),
    (r"carousel|marquee|slider-images|images-slider", "carousel"),
    (r"pagination", "pagination"),
    # Indicadores
    (r"\bbadge", "badge"),
    (r"\balert", "alert"),
    (r"notification|toast|sonner", "notification"),
    (r"avatar", "avatar"),
    (r"loader|loading|spinner|skeleton", "loader"),
    (r"progress|number-ticker", "progress"),
    # Visual / fundo / animação
    (r"background|aurora|meteors|vortex|particles|grid-pattern|dot-pattern|retro-grid|wavy|shooting-stars|warp", "background"),
    (r"text-(animation|generate|reveal|hover|rotate|3d|animate)|typewriter|typing|morphing-text|hyper-text|sparkles-text|shiny-text|aurora-text|comic-text|word-rotate", "text-animation"),
    (r"pattern", "pattern"),
    (r"effect|spotlight|glow|beam|ripple|confetti|cool-mode|glare|shine|shimmer|backlight|lens|cover|tracing", "effect"),
    (r"animat|orbiting|spinning|blur-fade", "animation"),
    # Seções de página
    (r"hero", "hero"),
    (r"pricing", "pricing"),
    (r"testimonial", "testimonial"),
    (r"footer", "footer"),
    (r"newsletter", "newsletter"),
    (r"calendar", "calendar"),
    (r"chart", "chart"),
    (r"breadcrumb", "breadcrumb"),
    (r"\bslider\b|range", "slider"),
    (r"steps?\b|stats?\b|feature-section|cta|team-section|contact-section|section-header|logo-grid|banner|authentication|404|faq", "section"),
    # Layout / separadores / utilitários estruturais
    (r"separator|divider|aspect-ratio|resizable|scroll-area|layout-grid|bento", "layout"),
    (r"\blabel\b|\bbadge\b|\bchip\b", "badge"),
    # Cursores e ponteiros
    (r"cursor|pointer", "cursor"),
    # Mockups de dispositivo / janelas
    (r"iphone|android|safari|macbook|terminal|window|device", "device-mockup"),
    # Texto e tipografia (não-animado)
    (r"\btext\b|typography|shadow-text", "text"),
]

_COMPILED = [(re.compile(pat), cat) for pat, cat in _RULES]

# Facetas transversais: qualidades que se somam à categoria primária em vez de
# substituí-la. Um "shimmer-button" é primariamente um button, mas também tem a
# faceta "animation" e "effect" — relevante para quem busca "botão animado".
# Estas regras NÃO definem a categoria primária; só entram nas tags.
_FACET_RULES: list[tuple[str, str]] = [
    (r"animat|shimmer|pulsat|shiny|ripple|rainbow|spinning|orbiting|blur-fade|marquee|kinetic|morphing|typing|typewriter", "animation"),
    (r"effect|glow|beam|spotlight|glare|shine|backlight|confetti|cool-mode|gradient|neon|aurora|sparkle|meteor|vortex", "effect"),
    (r"3d|parallax|perspective|tilt", "3d"),
    (r"\btext\b|word|letter|typography", "text"),
    (r"hover|interactive", "interactive"),
    (r"\bdark\b|theme-toggle|theme-toggler", "theme"),
    (r"glass|blur|frosted", "glassmorphism"),
    (r"neobrutalism|brutalist", "neobrutalism"),
]
_FACET_COMPILED = [(re.compile(pat), cat) for pat, cat in _FACET_RULES]


def canonical_category(name: str, original_category: str = "") -> str:
    """
    Deriva a categoria PRIMÁRIA (uma só) a partir do nome do componente e da
    categoria original. Retorna 'other' quando nenhuma regra casa.
    Usada para navegação e ordenação.
    """
    haystack = f"{name} {original_category}".lower()
    for regex, cat in _COMPILED:
        if regex.search(haystack):
            return cat
    return "other"


def category_tags(name: str, original_category: str = "") -> list[str]:
    """
    Deriva TODAS as facetas aplicáveis (categoria primária + tipos secundários +
    facetas transversais), para busca multi-uso. Um componente pode aparecer em
    várias categorias conforme o caso de uso.

    Ex: "shimmer-button" -> ["button", "animation", "effect"]
        "pricing-card"    -> ["card", "pricing", "section"]
    """
    haystack = f"{name} {original_category}".lower()
    tags: list[str] = []

    # Categoria primária sempre entra primeiro
    primary = canonical_category(name, original_category)
    if primary != "other":
        tags.append(primary)

    # Outros tipos estruturais que também casam (ex: pricing-card -> card E pricing)
    for regex, cat in _COMPILED:
        if cat not in tags and cat != "other" and regex.search(haystack):
            tags.append(cat)

    # Facetas transversais (animation, effect, 3d, theme...)
    for regex, facet in _FACET_COMPILED:
        if facet not in tags and regex.search(haystack):
            tags.append(facet)

    return tags or ["other"]


def is_demo(name: str) -> bool:
    """
    Indica se o nome é uma variação de demonstração (ex: '-demo', '-demo-2').
    Útil para filtrar exemplos de componentes reais (comum no Magic UI).
    """
    return bool(re.search(r"-demo(-\d+)?$|^index$|^utils$", name.lower()))
