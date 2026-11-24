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
LOCALES = ["en", "es"]
CAP_PRODUCT_ROUTES = [
    "/product/Mineral-Water-Closure-cap-Molds.html",
    "/product/5-Gallon-Water-Cap-Mould.html",
    "/product/Oil-bottle-cap-mould.html",
    "/product/Engine-Oil-Cap-Mould.html",
    "/product/Food-Packaging-Cap-Mould.html",
    "/product/Medical-Cap-Mould.html",
    "/product/Flip-top-caps-mould.html",
    "/product/Personal-Care-Cap-Mould.html",
    "/product/Functional-Cap-Mould.html",
    "/product/Plastic-Handle-Cap-mould.html",
    "/product/Wine-Cap-Mould.html",
    "/product/PET-Preform-Mould.html",
    "/product/Blow-Bottle-Mould.html",
]


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
assert [row["code"] for row in manifest["locales"]] == LOCALES, manifest
assert (DIST / "build-meta.json").is_file()
meta = json.loads((DIST / "build-meta.json").read_text(encoding="utf-8"))
assert meta["siteOrigin"] == ORIGIN
assert meta["noindex"] is True
assert meta["templateSet"] == "templates/site"

routes = ["/", "/products/", "/Plastic-cap-mold.html", "/about/", "/manufacturing/", "/quality-control/", "/contact/", "/faq/", "/blog/", "/privacy-policy/"]
routes += CAP_PRODUCT_ROUTES
routes += [
    "/about/about_us.html", "/about/ABOUT_US.html", "/about/FAQs.html",
    "/machine/Cap-Auxiliary-Machines.html", "/cap-samples/Sample.html",
    "/news/news.html", "/videolist/Cap-Mold-Video.html", "/contact/contact_us.html",
]
for locale in LOCALES:
    prefix = "" if locale == "en" else locale
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
        assert 'hreflang="en"' in html and 'hreflang="es"' in html and 'hreflang="x-default"' in html
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
            if locale != "en" and localized.startswith(locale + "/"):
                localized = localized[len(locale) + 1 :]
            if not target or target.startswith("#"):
                continue
            if not (DIST / target).is_file() and not (DIST / target / "index.html").is_file():
                # The static site references only generated local routes/assets.
                raise AssertionError((locale, route, "broken local ref", ref))

home = (DIST / "index.html").read_text(encoding="utf-8")
assert home.count("/product/") >= len(CAP_PRODUCT_ROUTES)
for route in CAP_PRODUCT_ROUTES:
    assert route in home
assert "/collections/" not in home
expected_nav = [
    "Mineral Water Cap Mould",
    "5 Gallon Water Cap Mould",
    "Edible Oil Cap Mould",
    "Flip top caps mould",
    "Engine Oil Cap Mould",
    "Food Packaging Cap Mould",
    "Medical Cap Mould",
    "Personal Care Cap Mould",
    "Functional Cap Mould(Combination)",
    "Plastic Handle mould",
    "Wine Cap Mould",
    "PET Preform Mould",
    "Blow Bottle Mould",
]
positions = [home.index(">" + label + "</a>") for label in expected_nav]
assert positions == sorted(positions)
assert ">Cap Mould Series</a>" not in home
assert "4-55,Xicheng New Village,Huangyan Taizhou,Zhejiang Province, China" in home
assert 'class="info-item"' in home
assert 'class="social-link tiktok"' in home
assert 'class="social-link youtube"' in home
assert 'class="social-link facebook"' in home
for route in CAP_PRODUCT_ROUTES:
    path = DIST / route.strip("/")
    html = path.read_text(encoding="utf-8")
    assert "mould-detail-page" in html
    assert html.count("mould-product-card") >= 3
    assert html.count("mould-advantage-card") == 6
    assert "mould-samples-grid" in html and "mould-quality-list" in html
    assert "HIGH-RESOLUTION IMAGES / PDF" not in html
catalog_page = (DIST / "Plastic-cap-mold.html").read_text(encoding="utf-8")
catalog_page_es = (DIST / "es" / "Plastic-cap-mold.html").read_text(encoding="utf-8")
for page in (catalog_page, catalog_page_es):
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
    labels = ('Core Advantages of LEYA MOULD', 'Plastic Cap Samples', 'Engineering Excellence Behind Every Mould', 'Your Cap Mould Journey', 'Common Questions', 'Client Feedback', 'Start Your Cap Mould Project') if page is catalog_page else ('Ventajas clave de LEYA MOULD', 'Muestras de tapas de plástico', 'Excelencia de ingeniería detrás de cada molde', 'Su recorrido de molde', 'Preguntas frecuentes', 'Opiniones de clientes', 'Empiece su proyecto de moldes')
    for label in labels:
        assert label in page, label
    assert page.count('class="sample-card"') >= 18
    assert page.count('class="video-card"') >= 5
es_product = (DIST / "es" / CAP_PRODUCT_ROUTES[0].strip("/")).read_text(encoding="utf-8")
en_product = (DIST / CAP_PRODUCT_ROUTES[0].strip("/")).read_text(encoding="utf-8")
assert head_value(es_product, r'<meta name="description" content="([^"]*)"') != head_value(en_product, r'<meta name="description" content="([^"]*)"')
assert "Molde de tapón" in head_value(es_product, r"<title>([^<]+)</title>")
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
print("LEYA_MOULD_RELEASE_PASSED", len(routes), "routes x", len(LOCALES), "locales")



