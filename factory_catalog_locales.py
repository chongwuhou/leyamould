from __future__ import annotations

import html
import re


SOURCE_DOCUMENT = "puyunsm(1).pdf"
GRID_OPEN = '<div class="grid grid--4 product-grid">'

CATEGORY_NAMES = {
    "Plastic Shaker Bottles": {
        "en": "Sports Shaker Bottle",
        "es": "Botella mezcladora deportiva",
        "pt": "Coqueteleira esportiva",
        "ru": "Спортивный шейкер",
        "tr": "Sporcu shaker şişesi",
    },
    "Plastic Sports Water Bottles": {
        "en": "Plastic Sports Water Bottle",
        "es": "Botella deportiva de plástico",
        "pt": "Garrafa esportiva de plástico",
        "ru": "Пластиковая спортивная бутылка",
        "tr": "Plastik spor matarası",
    },
    "Large Capacity Water Jugs": {
        "en": "Large-Capacity Sports Water Bottle",
        "es": "Botella deportiva de gran capacidad",
        "pt": "Garrafa esportiva de grande capacidade",
        "ru": "Спортивная бутылка большого объёма",
        "tr": "Büyük hacimli spor matarası",
    },
    "Spray Water Bottles": {
        "en": "Spray Water Bottle",
        "es": "Botella con pulverizador",
        "pt": "Garrafa com borrifador",
        "ru": "Бутылка с распылителем",
        "tr": "Spreyli su şişesi",
    },
    "Two-Way Drinking Cups": {
        "en": "Two-Way Drinking Cup",
        "es": "Vaso con dos formas de beber",
        "pt": "Copo com duas formas de beber",
        "ru": "Термокружка с двумя способами питья",
        "tr": "İki içim seçenekli bardak",
    },
    "Titanium Vacuum Cups": {
        "en": "Titanium Vacuum Cup",
        "es": "Vaso térmico al vacío de titanio",
        "pt": "Copo térmico a vácuo de titânio",
        "ru": "Вакуумная термокружка из титана",
        "tr": "Titanyum vakumlu termos bardak",
    },
}

LABELS = {
    "en": {"model": "MODEL", "capacity": "Capacity", "new": "NEW", "english": "View English specifications", "details": "View product details"},
    "es": {"model": "MODELO", "capacity": "Capacidad", "new": "NUEVO", "english": "Ver especificaciones en inglés", "details": "Ver detalles del producto"},
    "pt": {"model": "MODELO", "capacity": "Capacidade", "new": "NOVO", "english": "Ver especificações em inglês", "details": "Ver detalhes do produto"},
    "ru": {"model": "МОДЕЛЬ", "capacity": "Объём", "new": "НОВИНКА", "english": "Характеристики на английском", "details": "Подробнее о товаре"},
    "tr": {"model": "MODEL", "capacity": "Kapasite", "new": "YENİ", "english": "İngilizce teknik özellikler", "details": "Ürün ayrıntılarını görüntüle"},
}


def _escape(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def _page_grid_bounds(body: str) -> tuple[int, int] | None:
    start = body.find(GRID_OPEN)
    if start < 0:
        return None
    content_start = start + len(GRID_OPEN)
    depth = 1
    for match in re.finditer(r"</?div\b[^>]*>", body[content_start:], re.I):
        token = match.group(0)
        if token.lower().startswith("</div"):
            depth -= 1
            if depth == 0:
                return content_start, content_start + match.start()
        else:
            depth += 1
    raise ValueError("Unclosed localized product grid")


def _source_products(series: dict) -> list[dict]:
    rows = []
    for key, product in series.items():
        if not isinstance(product, dict) or product.get("sourceDocument") != SOURCE_DOCUMENT:
            continue
        if product.get("manualNew") is not True:
            continue
        model = str(product.get("model") or key).strip().lower()
        slug = str(product.get("slug") or model).strip("/")
        category = str(product.get("category") or "")
        images = product.get("images") or []
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,79}", slug):
            raise ValueError(f"Invalid factory product slug: {slug!r}")
        if not images:
            raise ValueError(f"Factory product {model} has no image")
        if not category:
            raise ValueError(f"Factory product {model} has no category")
        try:
            page = int(product.get("sourcePage") or 0)
        except (TypeError, ValueError):
            page = 0
        rows.append((page, model, product))
    rows.sort(key=lambda item: (item[0], item[1]))
    return [item[2] for item in rows]


def _render_card(product: dict, locale: str, category_slug: str, translated_routes: set[str], photo) -> str:
    labels = LABELS[locale]
    slug = str(product.get("slug") or product.get("model") or "").strip("/")
    route = f"/products/{slug}/"
    has_translation = route in translated_routes
    link_label = labels["details"] if has_translation else labels["english"]
    factory_model = str(product.get("factoryModel") or product.get("model") or slug)
    capacity = str(product.get("capacity") or "").strip()
    category = str(product.get("category") or "")
    title = CATEGORY_NAMES.get(category, {}).get(locale, category)
    image = str((product.get("images") or [""])[0])
    english_name = str(product.get("name") or "")
    search = " ".join(part for part in (title, factory_model, slug, capacity, english_name) if part)
    alt = " ".join(part for part in (title, labels["model"], factory_model, capacity) if part)
    small = f'{labels["model"]} {_escape(factory_model)}'
    if capacity:
        small += f' · {_escape(labels["capacity"])}: {_escape(capacity)}'
    image_html = photo(image, alt)
    return (
        f'<a class="product-card" data-product-card data-new-product="true" '
        f'data-category="{_escape(category_slug)}" data-search="{_escape(search)}" href="{_escape(route)}">'
        f'<div class="product-card__image">{image_html}</div>'
        f'<div class="product-card__body"><span class="product-card__new">{_escape(labels["new"])}</span>'
        f'<span class="product-card__small">{small}</span><h3>{_escape(title)}</h3>'
        f'<span class="product-card__link">{_escape(link_label)} ↗</span></div></a>'
    )


def catalog_cards(body: str, locale: str, route: str, translated_routes=None, series=None) -> str:
    """Add localized catalog cards for the 58 factory products without fabricating translated detail pages."""
    if locale not in LABELS or (route != "/products/" and not route.startswith("/collections/")):
        return body

    from site_renderer import CAT, SERIES, photo

    source = SERIES if series is None else series
    products = _source_products(source)
    if route.startswith("/collections/"):
        category_slug = route.strip("/").split("/")[-1]
        products = [
            product for product in products
            if product.get("category") in CAT and CAT[product["category"]][1] == category_slug
        ]
    if not products:
        return body

    translated = set(translated_routes or ())
    bounds = _page_grid_bounds(body)
    if bounds is None:
        raise ValueError(f"Localized catalog grid missing for {route}")
    content_start, content_end = bounds
    grid_content = body[content_start:content_end]
    cards = []

    for product in products:
        slug = str(product.get("slug") or product.get("model") or "").strip("/")
        href = f'/products/{slug}/'
        pattern = re.compile(
            r'<a\b(?=[^>]*\bhref=["\']' + re.escape(href) + r'["\'])[^>]*>.*?</a>',
            re.I | re.S,
        )
        matches = list(pattern.finditer(grid_content))
        if len(matches) > 1:
            raise ValueError(f"Duplicate factory product card for {slug} on {route}")
        if matches:
            card = matches[0].group(0)
            grid_content = grid_content[:matches[0].start()] + grid_content[matches[0].end():]
            if "data-product-card" not in card:
                card = re.sub(r"<a\b", '<a data-product-card', card, count=1, flags=re.I)
            if "data-new-product" not in card:
                card = re.sub(r"<a\b", '<a data-new-product="true"', card, count=1, flags=re.I)
            if "product-card__new" not in card:
                badge = f'<span class="product-card__new">{_escape(LABELS[locale]["new"])}</span>'
                card = card.replace('<div class="product-card__body">', '<div class="product-card__body">' + badge, 1)
            default_link = "View Product ↗"
            label = LABELS[locale]["details"] if href in translated else LABELS[locale]["english"]
            card = card.replace(default_link, _escape(label) + " ↗", 1)
            cards.append(card)
        else:
            category_slug = CAT[product["category"]][1]
            cards.append(_render_card(product, locale, category_slug, translated, photo))

    return body[:content_start] + "".join(cards) + grid_content + body[content_end:]