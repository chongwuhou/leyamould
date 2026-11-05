#!/usr/bin/env python3
"""Prevent CSS rules from silently defeating catalog filters/pagination."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent.parent
CSS=(ROOT/"dist/assets/site.css").read_text(encoding="utf-8")
SOURCE_CSS=(ROOT/"assets/site.css").read_text(encoding="utf-8")
assert ".pagination a{" in SOURCE_CSS
assert ".pagination__pages{" in SOURCE_CSS
assert ".pagination__pages a{" in SOURCE_CSS
for text in (CSS,SOURCE_CSS):
    assert re.search(r"\[hidden\]\s*\{\s*display\s*:\s*none\s*!important\s*\}",text),(
        "Catalog search and pagination mark .product-card hidden; CSS must honor it"
    )

SCRIPT=(ROOT/"dist/assets/site.js").read_text(encoding="utf-8")
assert "c.hidden=true" in SCRIPT
assert "c.hidden=false" in SCRIPT
assert "q?.addEventListener('input'" in SCRIPT
assert "perPage=18" in SCRIPT
assert "matching.slice((page-1)*perPage,page*perPage)" in SCRIPT
CATEGORY_SLUGS=(
    "sports-water-bottles","large-capacity-water-jugs","kids-water-bottles",
    "plastic-shaker-bottles","spray-water-bottles","two-way-drinking-cups",
    "titanium-vacuum-cups"
)
for path in ("products/index.html","es/products/index.html","pt/products/index.html",
             "ru/products/index.html","tr/products/index.html"):
    html=(ROOT/"dist"/path).read_text(encoding="utf-8")
    assert html.count("data-product-card")>=85,(path,"product cards missing")
    assert 'data-catalog-query' in html,(path,"catalog search input missing")
    assert 'data-catalog-category' in html,(path,"catalog category input missing")
    prefix="" if path=="products/index.html" else "/"+path.split("/",1)[0]
    for slug in CATEGORY_SLUGS:
        assert f'href="{prefix}/collections/{slug}/"' in html,(path,slug,"catalog sidebar link missing")
        assert f'value="{slug}"' in html,(path,slug,"catalog filter option missing")
    assert 'class="pagination__pages"' in html,(path,"crawlable page links missing")
    assert html.count('data-page-link="15"')==1,(path,"15-page catalog navigation missing")
print("XUYI_CATALOG_VISIBILITY_PASSED five-language filter/pagination CSS and JS invariants")
