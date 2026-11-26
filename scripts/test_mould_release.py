#!/usr/bin/env python3
"""Release gate for the new LEYA MOULD public source build."""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ORIGIN = "https://leyamould.com"


class Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag in {"img", "script", "link"}:
            value = attrs.get("src") or attrs.get("href")
            if value and value.startswith("/"):
                self.images.append(value)


def head_value(document: str, pattern: str) -> str:
    match = re.search(pattern, document, re.I)
    assert match, pattern
    return match.group(1)


manifest = json.loads((DIST / "locale-manifest.json").read_text(encoding="utf-8"))
locale_rows = [row for row in manifest.get("locales", []) if row.get("enabled") and row.get("publishReady")]
assert locale_rows, "No publish-ready locale in manifest"
LOCALES = [str(row["code"]).lower() for row in locale_rows]
SOURCE_LOCALE = next((str(row["code"]).lower() for row in locale_rows if row.get("sortOrder") == 10), LOCALES[0])
assert SOURCE_LOCALE in LOCALES
assert len(LOCALES) == len(set(LOCALES)), LOCALES


def locale_prefix(locale: str) -> str:
    row = next(item for item in locale_rows if str(item["code"]).lower() == locale)
    return str(row.get("pathPrefix") or ("" if locale == SOURCE_LOCALE else row.get("code"))).strip("/")
assert (DIST / "build-meta.json").is_file()
meta = json.loads((DIST / "build-meta.json").read_text(encoding="utf-8"))
assert meta["siteOrigin"] == ORIGIN
assert meta["noindex"] is True
assert meta["templateSet"] == "templates/site"

all_manifest_routes = [str(route) for route in manifest.get("routes", []) if isinstance(route, str)]
assert all_manifest_routes, "Empty route manifest"
locale_prefixes = {str(row.get("pathPrefix") or row.get("code") or "").strip("/") for row in locale_rows}
locale_prefixes.discard("")
routes = []
for route in all_manifest_routes:
    clean = "/" + route.lstrip("/")
    if any(clean == "/" + prefix or clean.startswith("/" + prefix + "/") for prefix in locale_prefixes):
        continue
    if clean not in routes:
        routes.append(clean)
assert "/" in routes and "/product/" not in routes, routes
product_routes = sorted({route for route in routes if route.startswith("/product/") and route.endswith(".html")})
assert product_routes, "No product routes in locale manifest"
for locale in LOCALES:
    prefix = locale_prefix(locale)
    for route in routes:
        if route == "/":
            path = DIST / prefix / "index.html"
        elif route.endswith(".html"):
            path = DIST / prefix / route.strip("/")
        else:
            path = DIST / prefix / route.strip("/") / "index.html"
        assert path.is_file(), (locale, route, path)
        html = path.read_text(encoding="utf-8")
        assert "<main id=\"main-content\">" in html and "</html>" in html
        assert "LEYA MOULD" in html and "amyhu@leyamould.com" in html and "8613606727715" in html
        assert "XUYI" not in html and "drinkware" not in html.lower()
        assert '<meta name="robots" content="noindex,nofollow">' in html
        assert '<link rel="canonical" href="' in html
        for lang in LOCALES:
            assert f'hreflang="{lang}"' in html
        assert 'hreflang="x-default"' in html
        assert '<meta property="og:type" content="website">' in html
        assert '<meta property="og:url" content="' in html
        assert '<meta property="og:image" content="https://leyamould.com/' in html
        assert '<meta name="twitter:card" content="summary_large_image">' in html
        assert '<script type="application/ld+json">' in html
        assert head_value(html, r'<title>([^<]+)</title>').strip()
        assert head_value(html, r'<meta name="description" content="([^"]*)"').strip()
        parser = Refs()
        parser.feed(html)
        for ref in parser.links + parser.images:
            if ref.startswith(("/api/", "/media/", "mailto:", "https://", "tel:")):
                continue
            target = urlsplit(ref).path.lstrip("/")
            localized = target
            if prefix and localized.startswith(prefix + "/"):
                localized = localized[len(prefix) + 1 :]
            if not target or target.startswith("#"):
                continue
            if not (DIST / target).is_file() and not (DIST / target / "index.html").is_file():
                # The static site references only generated local routes/assets.
                raise AssertionError((locale, route, "broken local ref", ref))

home = (DIST / "index.html").read_text(encoding="utf-8")
assert home.count("/product/") >= len(product_routes)
assert home.count('class="cap-series-card"') == min(12, len(product_routes))
assert home.count('class="process-step"') == 5
for route in product_routes:
    assert route in home
assert "/collections/" not in home
# Navigation labels are D1-owned and may be edited in the admin.  The release
# gate therefore verifies the canonical route order rather than freezing copy
# into the build test.
ordered_nav_routes = sorted(product_routes, key=lambda route: home.index('href="' + route + '"'))
assert len(ordered_nav_routes) == len(product_routes)
positions = [home.index('href="' + route + '"') for route in ordered_nav_routes]
assert positions == sorted(positions)
assert ">Cap Mould Series</a>" not in home
assert "4-55,Xicheng New Village,Huangyan Taizhou,Zhejiang Province, China" in home
assert 'class="info-item"' in home
assert 'class="social-link tiktok"' in home
assert 'class="social-link youtube"' in home
assert 'class="social-link facebook"' in home
for route in product_routes:
    path = DIST / route.strip("/")
    html = path.read_text(encoding="utf-8")
    assert "mould-detail-page" in html
    assert html.count("mould-product-card") >= 3
    # Advantages are structured D1 content and may grow or shrink per family.
    # Verify that the module is rendered without freezing a historical card
    # count in the release gate.
    assert html.count("mould-advantage-card") >= 1
    assert "mould-samples-grid" in html and "mould-quality-list" in html
    assert "HIGH-RESOLUTION IMAGES / PDF" not in html
    assert html.count('class="mould-shared-cta mould-shared-cta--category"') == 1
    assert "Start Your Cap Mould Project" in html

# Every page-level contact panel is rendered through the same shared CTA
# module.  Only the localized copy/variant changes by route.
shared_cta_routes = {
    "/Plastic-cap-mold.html": "catalog",
    "/about/": "about",
    "/capabilities/": "auxiliary",
    "/faq/": "faq",
    "/samples/": "samples",
}
for locale in LOCALES:
    prefix = locale_prefix(locale)
    for route, variant in shared_cta_routes.items():
        path = DIST / prefix / (Path(route.strip("/")) / "index.html" if route.endswith("/") else Path(route.strip("/")))
        html = path.read_text(encoding="utf-8")
        assert html.count('class="mould-shared-cta mould-shared-cta--' + variant + '"') == 1, (locale, route, variant)
        assert 'class="mould-shared-cta__actions"' in html
        assert 'href="mailto:amyhu@leyamould.com"' in html
        assert 'href="https://wa.me/8613606727715"' in html

# The CAP MOULD menu is generated from the same D1/manifest product set as the
# aggregate/product pages, in every publish-ready locale.
for locale in LOCALES:
    prefix = locale_prefix(locale)
    path = DIST / prefix / "index.html"
    html = path.read_text(encoding="utf-8")
    assert html.count('id="menu-products"') == 1
    assert html.count('class="nav__drop nav__drop--products"') == 1
    assert html.count('class="mini-menu"') >= 3
    for route in product_routes:
        assert html.count(route) >= 2, (locale, route)
catalog_page = (DIST / "Plastic-cap-mold.html").read_text(encoding="utf-8")
catalog_pages = [(SOURCE_LOCALE, catalog_page)]
for locale in LOCALES:
    if locale == SOURCE_LOCALE:
        continue
    catalog_pages.append((locale, (DIST / locale_prefix(locale) / "Plastic-cap-mold.html").read_text(encoding="utf-8")))
for locale, page in catalog_pages:
    assert 'data-catalog-videos' in page
    assert 'Cap Mould Trial Videos' in page or 'Vídeos de pruebas de moldes' in page
    assert '/api/youtube-videos' in page
    assert page.count('class="video-card"') >= 5
    assert 'catalogVideoModal' in page and 'catalogVideoIframe' in page
    # Aggregate catalogue parity: the reference page continues well beyond
    # products and trials. Keep every major module present and in order so a
    # future template change cannot silently truncate the page again.
    required_sections = [
        'catalog-advantages', 'catalog-samples', 'catalog-video-section',
        'catalog-technology', 'catalog-quality', 'catalog-workflow',
        'catalog-faq', 'catalog-testimonials', 'catalog-contact',
    ]
    offsets = [page.index(section) for section in required_sections]
    assert offsets == sorted(offsets), offsets
    if locale == SOURCE_LOCALE:
        labels = ('Core Advantages of LEYA MOULD', 'Bottle Cap Sample Gallery', 'Technical Strength &amp; Process', 'Quality Control &amp; Inspection', 'Cooperation Process', 'Common Questions', 'Client Feedback', 'Start Your Cap Mould Project')
    elif locale == "es":
        labels = ('Ventajas clave de LEYA MOULD', 'Galería de muestras de tapas', 'Fortaleza técnica y proceso', 'Control de calidad e inspección', 'Proceso de cooperación', 'Preguntas frecuentes', 'Opiniones de clientes')
    else:
        labels = ('Core Advantages', 'Bottle Cap', 'Technical', 'Quality', 'Cooperation', 'Questions', 'Client', 'Cap Mould')
    for label in labels:
        assert label in page, (locale, label)
    if locale == "es":
        assert "Inicie su proyecto de moldes" in page or "Empiece su proyecto de moldes" in page
    if locale == SOURCE_LOCALE:
        assert page.count('id="catalog-testimonials"') == 1
        assert page.count('Client Feedback') == 1
    else:
        assert page.count('id="catalog-testimonials"') == 1
        assert page.count('Opiniones de clientes') == 1
    # Inventory sizes are D1-owned and may grow or shrink. Verify that the
    # modules are wired without freezing an historical sample/video count.
    assert 'class="catalog-sample-item"' in page
    assert 'class="video-card"' in page
if "es" in LOCALES:
    es_prefix = next(str(row.get("pathPrefix") or "es").strip("/") for row in locale_rows if str(row["code"]).lower() == "es")
    sample_product = product_routes[0]
    es_product = (DIST / es_prefix / sample_product.strip("/")).read_text(encoding="utf-8")
    en_product = (DIST / sample_product.strip("/")).read_text(encoding="utf-8")
    assert head_value(es_product, r'<meta name="description" content="([^"]*)"') != head_value(en_product, r'<meta name="description" content="([^"]*)"')
    assert head_value(es_product, r"<title>([^<]+)</title>").strip()
machine_en = (DIST / "Bottle-Cap-Machine" / "Bottle-Cap-Machine.html").read_text(encoding="utf-8")
machine_es = (DIST / "es" / "Bottle-Cap-Machine" / "Bottle-Cap-Machine.html").read_text(encoding="utf-8")
assert "nopic.gif" not in machine_en and "/assets/news/cooling-water-quality-cap-mold-performance.webp" in machine_en
assert "How does cooling-water quality affect cap mould stability?" in machine_en
assert "¿Cómo afecta la calidad del agua de refrigeración" in machine_es and "How does cooling-water quality" not in machine_es
detail_es = (DIST / "es" / "Bottle-Cap-Machine" / "cap-ejection-pin-placement.html").read_text(encoding="utf-8")
assert "¿Dónde deben colocarse los pasadores de expulsión" in detail_es
assert detail_es.count('class="blog-section"') == 7
assert detail_es.count('class="blog-editorial__product-link"') == 3
assert (DIST / "admin" / "index.html").is_file()
assert "LEYA MOULD" in (DIST / "admin" / "index.html").read_text(encoding="utf-8")
print("LEYA_MOULD_RELEASE_PASSED", len(routes), "routes x", len(LOCALES), "locales", "products", len(product_routes))






