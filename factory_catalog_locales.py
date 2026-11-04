from __future__ import annotations

import html
import re


SOURCE_DOCUMENTS = {"puyunsm(1).pdf", "水杯最新产品.pptx"}
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


TWO_WAY_SIZE = {
    "en": ((400, "Compact"), (550, "Everyday"), (650, "Mid-Size"), (850, "Large-Capacity"), (10000, "Extra-Large")),
    "es": ((400, "Compacto"), (550, "De uso diario"), (650, "Tamaño medio"), (850, "Gran capacidad"), (10000, "Extra grande")),
    "pt": ((400, "Compacto"), (550, "Para uso diário"), (650, "Tamanho médio"), (850, "Grande capacidade"), (10000, "Extra grande")),
    "ru": ((400, "Компактная"), (550, "Повседневная"), (650, "Среднего размера"), (850, "Большой ёмкости"), (10000, "Сверхбольшая")),
    "tr": ((400, "Kompakt"), (550, "Günlük"), (650, "Orta boy"), (850, "Büyük kapasiteli"), (10000, "Ekstra büyük")),
}

TWO_WAY_ANGLE = {
    "en": ("Dual-Mode Drinking Cup", "Two-Way Travel Cup", "Two-Way Cup with Seal Design", "Daily-Use Two-Way Cup", "OEM Dual-Drink Cup"),
    "es": ("Vaso de doble modo", "Vaso de dos formas para viaje", "Vaso de doble uso con diseño de sellado", "Vaso de doble uso para el día a día", "Vaso de doble uso para OEM"),
    "pt": ("Copo de dupla função", "Copo de dupla função para viagem", "Copo de dupla função com vedação", "Copo de dupla função para uso diário", "Copo de dupla função para OEM"),
    "ru": ("Кружка с двумя режимами питья", "Дорожная кружка 2-в-1", "Кружка 2-в-1 с конструкцией уплотнения", "Кружка 2-в-1 для повседневного использования", "Кружка 2-в-1 для OEM-заказов"),
    "tr": ("Çift içimli bardak", "İki içimli seyahat bardağı", "Sızdırmazlık tasarımlı çift içimli bardak", "Günlük kullanım için çift içimli bardak", "OEM çift içimli bardak"),
}

TWO_WAY_BUYER = {
    "en": (
        "OEM Wholesale Manufacturer", "Factory OEM Supplier", "B2B Custom Branding",
        "Ask About Custom Colors", "Ask About Custom Materials",
        "Wholesale Drinkware Supplier", "Bulk Two-Way Cup Orders", "Private Label OEM Factory",
        "Custom Logo Cup Manufacturer", "Promotional Drinkware Wholesale",
        "OEM Cup Production Partner", "Factory-Direct Bulk Supply", "B2B Travel Cup Sourcing",
        "Custom Color OEM Options", "Material Options for OEM Orders", "Wholesale Retail Cup Supply",
        "Private Label Drinkware Supplier", "Bulk Promotional Cup Sourcing",
        "Custom Branding Cup Factory", "OEM Two-Way Cup Wholesale",
    ),
    "es": (
        "Fabricante OEM para mayoristas", "Proveedor OEM de fábrica", "Marca personalizada B2B",
        "Consulte colores personalizados", "Consulte materiales personalizados",
        "Proveedor mayorista de vasos", "Pedidos al por mayor de vasos 2 vías", "Fábrica OEM de marca privada",
        "Fabricante de vasos con logotipo", "Vasos promocionales al por mayor",
        "Socio de producción OEM", "Suministro directo de fábrica", "Abastecimiento B2B de vasos de viaje",
        "Opciones OEM de color personalizado", "Materiales para pedidos OEM", "Suministro mayorista para tiendas",
        "Proveedor de vasos de marca privada", "Compra al por mayor de vasos promocionales",
        "Fábrica de vasos con marca personalizada", "Vasos 2 vías OEM al por mayor",
    ),
    "pt": (
        "Fabricante OEM para atacado", "Fornecedor OEM de fábrica", "Marca personalizada B2B",
        "Consulte cores personalizadas", "Consulte materiais personalizados",
        "Fornecedor atacadista de copos", "Pedidos em volume de copos dupla função", "Fábrica OEM de marca própria",
        "Fabricante de copos com logotipo", "Copos promocionais no atacado",
        "Parceiro de produção OEM", "Fornecimento direto da fábrica", "Compra B2B de copos para viagem",
        "Opções OEM de cores personalizadas", "Materiais para pedidos OEM", "Fornecimento atacadista para varejo",
        "Fornecedor de copos de marca própria", "Compra em volume de copos promocionais",
        "Fábrica de copos com marca personalizada", "Copos dupla função OEM no atacado",
    ),
    "ru": (
        "Оптовый OEM-производитель", "Заводской OEM-поставщик", "B2B-брендинг под заказ",
        "Уточните варианты цветов", "Уточните варианты материалов",
        "Оптовый поставщик посуды", "Оптовые заказы кружек 2-в-1", "OEM-завод для частных марок",
        "Производитель кружек с логотипом", "Промокружки оптом",
        "Партнёр OEM-производства", "Прямые поставки с завода", "B2B-закупка дорожных кружек",
        "OEM-варианты индивидуальных цветов", "Материалы для OEM-заказов", "Оптовые поставки для розницы",
        "Поставщик кружек под своей маркой", "Оптовая закупка промокружек",
        "Заводская брендированная продукция", "Кружки 2-в-1 OEM оптом",
    ),
    "tr": (
        "Toptan OEM üreticisi", "Fabrika OEM tedarikçisi", "B2B özel markalama",
        "Özel renkleri sorun", "Özel malzemeleri sorun",
        "Toptan içecek gereçleri tedarikçisi", "Çift içimli bardak toplu siparişi", "Özel markalı OEM fabrikası",
        "Logolu bardak üreticisi", "Promosyon bardak toptan satışı",
        "OEM üretim ortağı", "Fabrikadan doğrudan toplu tedarik", "B2B seyahat bardağı tedariki",
        "Özel renk OEM seçenekleri", "OEM siparişleri için malzemeler", "Perakende için toptan tedarik",
        "Özel markalı bardak tedarikçisi", "Toplu promosyon bardağı tedariki",
        "Özel markalı bardak fabrikası", "OEM çift içimli bardak toptan",
    ),
}


def _card_title(product: dict, locale: str) -> str:
    """Create distinct, source-grounded B2B product titles for factory buyers."""
    if product.get("category") != "Two-Way Drinking Cups":
        from scripts.source_catalog_capacity_oz import product_h1_text
        return product_h1_text(locale, product)

    from scripts.source_catalog_capacity_oz import catalog_volume_numbers, volume_terms

    numbers = catalog_volume_numbers(product)
    if not numbers:
        raise ValueError("Two-way factory product needs a source-verified capacity: " + str(product.get("model")))
    model = str(product.get("factoryModel") or product.get("model") or product.get("slug") or "").strip().upper()
    match = re.search(r"(\d+)$", model)
    if not match:
        raise ValueError("Two-way factory product needs a numeric factory model: " + model)
    ordinal = int(match.group(1))
    size_value = max(numbers)
    size = next(label for upper, label in TWO_WAY_SIZE[locale] if size_value <= upper)
    volume = volume_terms(numbers, locale)
    angle = TWO_WAY_ANGLE[locale][(ordinal - 1) % len(TWO_WAY_ANGLE[locale])]
    buyer = TWO_WAY_BUYER[locale][(ordinal - 1) % len(TWO_WAY_BUYER[locale])]
    return f"{volume} {size} {angle} | {buyer}"





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
        if not isinstance(product, dict) or product.get("sourceDocument") not in SOURCE_DOCUMENTS:
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
    from scripts.source_catalog_capacity_oz import catalog_volume_numbers, volume_terms, verified_source_material
    labels = LABELS[locale]
    slug = str(product.get("slug") or product.get("model") or "").strip("/")
    route = f"/products/{slug}/"
    has_translation = route in translated_routes
    factory_model_value = product.get("factoryModel")
    factory_model = (factory_model_value.strip() if isinstance(factory_model_value, str) and factory_model_value.strip()
                     else str(product.get("model") or slug))
    capacity = str(product.get("capacity") or "").strip()
    numbers = catalog_volume_numbers(product)
    volume = volume_terms(numbers, locale) if numbers else ""
    category = str(product.get("category") or "")
    title = _card_title(product, locale)
    material = verified_source_material(product)
    image = str((product.get("images") or [""])[0])
    search = " ".join(part for part in (title, factory_model, slug, capacity, volume, material,
        "wholesale B2B OEM factory manufacturer custom plastic material options") if part)
    is_new_product = product.get("manualNew") is True and product.get("sourceDocument") in SOURCE_DOCUMENTS
    new_flag = ' data-new-product="true"' if is_new_product else ""
    badge = f'<span class="product-card__new">{_escape(labels["new"])}</span>' if is_new_product else ""
    family = product.get("imageReviewStatus") == "visually_reviewed_source_family_image"
    alt = ({"en":"Shared factory-family image; confirm exact model variant",
            "es":"Imagen compartida de familia; confirme la variante exacta",
            "pt":"Imagem compartilhada da família; confirme a variante exata",
            "ru":"Общее фото семейства; уточните конкретный вариант",
            "tr":"Ortak ürün ailesi görseli; kesin varyantı doğrulayın"}[locale]
           if family else " ".join(part for part in (title, labels["model"], factory_model, volume, material) if part))
    small = f'{labels["model"]} {_escape(factory_model)}'
    if capacity and category != "Two-Way Drinking Cups":
        small += f' · {_escape(labels["capacity"])}: {_escape(capacity)}'
    image_html = photo(image, alt)
    capacity_badge = f'<span class="product-card__capacity">{_escape(volume)}</span>' if volume and category != "Two-Way Drinking Cups" else ""
    return (
        f'<a class="product-card" data-product-card{new_flag} '
        f'data-category="{_escape(category_slug)}" data-search="{_escape(search)}" href="{_escape(route)}">'
        f'<div class="product-card__image">{image_html}</div>'
        f'<div class="product-card__body">{badge}'
        f'<span class="product-card__small">{small}</span><h3>{_escape(title)}</h3>{capacity_badge}'
        f'<span class="product-card__link">{_escape(labels["details"] if has_translation else labels["english"])} ↗</span></div></a>'
    )

def catalog_cards(body: str, locale: str, route: str, translated_routes=None, series=None) -> str:
    """Apply source-grounded B2B titles and search terms to every catalog product card."""
    if locale not in LABELS or (route != "/products/" and not route.startswith("/collections/")):
        return body

    from site_renderer import CAT, SERIES, photo

    source = SERIES if series is None else series
    products = [
        product for product in source.values()
        if isinstance(product, dict) and str(product.get("slug") or "").strip("/") and product.get("category") in CAT
    ]
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
    priority_cards = []
    priority_urls = set()
    if route == "/products/" or route.startswith("/collections/"):
        # Keep LO first and the eight G-series gallery references second in
        # the main catalog; preserve the matching priority cards in categories.
        card_pattern = re.compile(r'<a\b[^>]*\bdata-product-card\b[^>]*>.*?</a>', re.I | re.S)
        lo_matches = []
        gallery_matches = []
        for match in card_pattern.finditer(grid_content):
            card = match.group(0)
            opening = card.split(">", 1)[0]
            href_match = re.search(r'\bhref=["\']([^"\']+)["\']', opening, re.I)
            href = href_match.group(1) if href_match else ""
            item = (match.start(), match.end(), card, href)
            if "/products/lo-" in href:
                lo_matches.append(item)
            elif 'data-gallery-reference="true"' in opening:
                gallery_matches.append(item)
        lo_urls = [item[3] for item in lo_matches]
        gallery_urls = [item[3] for item in gallery_matches]
        if len(lo_urls) != len(set(lo_urls)):
            raise ValueError("Duplicate LO launch card in " + locale + " " + route)
        if len(gallery_urls) != len(set(gallery_urls)):
            raise ValueError("Duplicate gallery reference card in " + locale + " " + route)
        if route == "/products/" and len(lo_matches) != 8:
            raise ValueError("Main product catalog must retain all eight LO launch cards")
        if route == "/products/" and len(gallery_matches) != 8:
            raise ValueError("Main product catalog must retain all eight gallery reference cards")
        for start, end, _card, _url in sorted(lo_matches + gallery_matches, key=lambda item: item[0], reverse=True):
            grid_content = grid_content[:start] + grid_content[end:]
        priority_cards = [item[2] for item in lo_matches] + [item[2] for item in gallery_matches]
        priority_urls = set(lo_urls + gallery_urls)
        from product_slug_fix import REVERSE as LEGACY_PRODUCT_SLUGS
        priority_products = {}
        for product in products:
            slug = str(product.get("slug") or product.get("model") or "").strip("/")
            candidates = [f"/products/{slug}/"]
            if locale != "en":
                candidates.append(f"/{locale}/products/{slug}/")
            legacy_slug = LEGACY_PRODUCT_SLUGS.get(slug)
            if legacy_slug:
                candidates.append(f"/products/{legacy_slug}/")
                if locale != "en":
                    candidates.append(f"/{locale}/products/{legacy_slug}/")
            for candidate in candidates:
                priority_products[candidate] = product

        from scripts.source_catalog_capacity_oz import catalog_volume_numbers, volume_terms, verified_source_material
        from factory_product_locales import localized_name

        def refresh_priority_card(card):
            opening = card.split(">", 1)[0]
            href_match = re.search(r'\bhref=["\']([^"\']+)["\']', opening, re.I)
            product = priority_products.get(href_match.group(1)) if href_match else None
            if product is None:
                return card

            slug = str(product.get("slug") or product.get("model") or "").strip("/")
            title = _card_title(product, locale)
            heading = re.search(r"<h3\b[^>]*>(.*?)</h3>", card, re.I | re.S)
            if not heading:
                raise ValueError("Priority factory product card is missing its title heading: " + slug)
            current_title = html.unescape(re.sub(r"<[^>]+>", " ", heading.group(1))).strip()
            default_titles = {
                localized_name(product, locale),
                str(product.get("name") or "").strip(),
                str(product.get("model") or slug).strip(),
            }
            capacity_text = str(product.get("capacity") or "").strip()
            if capacity_text:
                default_titles.update(capacity_text + " " + value for value in tuple(default_titles) if value)
            if current_title in default_titles:
                card, heading_count = re.subn(
                    r"(<h3\b[^>]*>).*?(</h3>)",
                    lambda match: match.group(1) + _escape(title) + match.group(2),
                    card, count=1, flags=re.I | re.S
                )
                if heading_count != 1:
                    raise ValueError("Priority factory product card title update failed: " + slug)

            numbers = catalog_volume_numbers(product)
            volume = volume_terms(numbers, locale) if numbers else ""
            if product.get("category") == "Two-Way Drinking Cups":
                card = re.sub(r'<span class="product-card__capacity">.*?</span>', "", card, count=1, flags=re.I | re.S)
            elif volume:
                badge = f'<span class="product-card__capacity">{_escape(volume)}</span>'
                if re.search(r'<span class="product-card__capacity">.*?</span>', card, re.I | re.S):
                    card = re.sub(r'<span class="product-card__capacity">.*?</span>', lambda _: badge, card, count=1, flags=re.I | re.S)
                else:
                    card, badge_count = re.subn(r"</h3>", "</h3>" + badge, card, count=1, flags=re.I)
                    if badge_count != 1:
                        raise ValueError("Priority factory product card capacity badge insertion failed: " + slug)

            factory_model_value = product.get("factoryModel")
            factory_model = (factory_model_value.strip() if isinstance(factory_model_value, str) and factory_model_value.strip()
                             else str(product.get("model") or slug))
            material = verified_source_material(product)
            search_parts = (
                title, factory_model, slug, capacity_text, volume, material,
                "wholesale B2B OEM factory manufacturer custom plastic material options colors bulk"
            )
            search_match = re.search(r'\bdata-search="([^"]*)"', card, re.I)
            existing_search = html.unescape(search_match.group(1)) if search_match else ""
            search = " ".join(dict.fromkeys((existing_search + " " + " ".join(part for part in search_parts if part)).split()))
            if search_match:
                card = re.sub(r'\bdata-search="[^"]*"', lambda _: 'data-search="' + _escape(search) + '"', card, count=1, flags=re.I)
            else:
                card = re.sub(r"<a\b", '<a data-search="' + _escape(search) + '"', card, count=1, flags=re.I)
            return card

        priority_cards = [refresh_priority_card(card) for card in priority_cards]
        # A template may contain both a gallery-priority card and an older
        # ordinary card for the same SKU. Keep the priority copy only.
        for priority_url in priority_urls:
            duplicate_pattern = re.compile(
                r'<a\b(?=[^>]*\bhref=["\']' + re.escape(priority_url) + r'["\'])[^>]*>.*?</a>',
                re.I | re.S,
            )
            grid_content = duplicate_pattern.sub("", grid_content)
    cards = []

    for product in products:
        slug = str(product.get("slug") or product.get("model") or "").strip("/")
        href = f'/products/{slug}/'
        localized_href = f'/{locale}/products/{slug}/' if locale != "en" else href
        from product_slug_fix import REVERSE as LEGACY_PRODUCT_SLUGS
        legacy_slug = LEGACY_PRODUCT_SLUGS.get(slug)
        candidate_hrefs = [href, localized_href]
        if legacy_slug:
            legacy_href = f'/products/{legacy_slug}/'
            legacy_localized_href = f'/{locale}/products/{legacy_slug}/' if locale != "en" else legacy_href
            candidate_hrefs.extend((legacy_href, legacy_localized_href))
        if any(candidate in priority_urls for candidate in candidate_hrefs):
            continue
        href_pattern = "(?:" + "|".join(re.escape(value) for value in dict.fromkeys(candidate_hrefs)) + r")(?:[?#][^\"']*)?"
        pattern = re.compile(
            r'<a\b(?=[^>]*\bhref=["\']' + href_pattern + r'["\'])[^>]*>.*?</a>',
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
            is_new_product = product.get("manualNew") is True and product.get("sourceDocument") in SOURCE_DOCUMENTS
            if is_new_product and "data-new-product" not in card:
                card = re.sub(r"<a\b", '<a data-new-product="true"', card, count=1, flags=re.I)
            if is_new_product and "product-card__new" not in card:
                badge = f'<span class="product-card__new">{_escape(LABELS[locale]["new"])}</span>'
                card = card.replace('<div class="product-card__body">', '<div class="product-card__body">' + badge, 1)
            default_link = "View Product ↗"
            label = LABELS[locale]["details"] if any(candidate in translated for candidate in candidate_hrefs) else LABELS[locale]["english"]
            card = card.replace(default_link, _escape(label) + " ↗", 1)
            from scripts.source_catalog_capacity_oz import catalog_volume_numbers, volume_terms, verified_source_material
            factory_model_value = product.get("factoryModel")
            factory_model = (factory_model_value.strip() if isinstance(factory_model_value, str) and factory_model_value.strip()
                             else str(product.get("model") or slug))
            numbers = catalog_volume_numbers(product)
            volume = volume_terms(numbers, locale) if numbers else ""
            material = verified_source_material(product)
            title = _card_title(product, locale)
            search_parts = (
                title, factory_model, slug, str(product.get("capacity") or ""), volume, material,
                "wholesale B2B OEM factory manufacturer custom plastic material options colors bulk"
            )
            search_match = re.search(r'\bdata-search="([^"]*)"', card, re.I)
            existing_search = html.unescape(search_match.group(1)) if search_match else ""
            generated_search = " ".join(part for part in search_parts if part)
            search = " ".join(dict.fromkeys((existing_search + " " + generated_search).split()))
            if product.get("category") == "Two-Way Drinking Cups":
                card, heading_count = re.subn(
                    r"(<h3\b[^>]*>).*?(</h3>)",
                    lambda match: match.group(1) + _escape(title) + match.group(2),
                    card, count=1, flags=re.I | re.S
                )
                if heading_count != 1:
                    raise ValueError("Two-way product card is missing its title heading: " + slug)
                small = f'{LABELS[locale]["model"]} {_escape(factory_model)}'
                card, model_count = re.subn(
                    r'(<span class="product-card__small">).*?(</span>)',
                    lambda match: match.group(1) + small + match.group(2),
                    card, count=1, flags=re.I | re.S
                )
                if model_count != 1:
                    raise ValueError("Two-way product card is missing its model label: " + slug)
                card = re.sub(r'<span class="product-card__capacity">.*?</span>', "", card, count=1, flags=re.I | re.S)
            else:
                heading = re.search(r"<h3\b[^>]*>(.*?)</h3>", card, re.I | re.S)
                if not heading:
                    raise ValueError("Factory product card is missing its title heading: " + slug)
                current_title = html.unescape(re.sub(r"<[^>]+>", " ", heading.group(1))).strip()
                from factory_product_locales import localized_name
                default_titles = {localized_name(product, locale), str(product.get("name") or "").strip(), str(product.get("model") or slug).strip()}
                capacity_text = str(product.get("capacity") or "").strip()
                if capacity_text:
                    default_titles.update(capacity_text + " " + value for value in tuple(default_titles) if value)
                if current_title in default_titles:
                    card, heading_count = re.subn(
                        r"(<h3\b[^>]*>).*?(</h3>)",
                        lambda match: match.group(1) + _escape(title) + match.group(2),
                        card, count=1, flags=re.I | re.S
                    )
                    if heading_count != 1:
                        raise ValueError("Factory product card title update failed: " + slug)
            card, search_count = re.subn(
                r'\bdata-search="[^"]*"',
                lambda _: 'data-search="' + _escape(search) + '"',
                card, count=1, flags=re.I | re.S
            )
            if search_count != 1:
                card = re.sub(r"<a\b", '<a data-search="' + _escape(search) + '"', card, count=1, flags=re.I)
            cards.append(card)
        else:
            category_slug = CAT[product["category"]][1]
            cards.append(_render_card(product, locale, category_slug, translated, photo))

    return body[:content_start] + "".join(priority_cards + cards) + grid_content + body[content_end:]
