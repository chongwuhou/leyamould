#!/usr/bin/env python3
"""Prevent CSS rules from silently defeating catalog filters/pagination."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent.parent
CSS=(ROOT/"dist/assets/site.css").read_text(encoding="utf-8")
SOURCE_CSS=(ROOT/"assets/site.css").read_text(encoding="utf-8")
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
for path in ("products/index.html","es/products/index.html","pt/products/index.html",
             "ru/products/index.html","tr/products/index.html"):
    html=(ROOT/"dist"/path).read_text(encoding="utf-8")
    assert html.count("data-product-card")>=85,(path,"product cards missing")
    assert 'data-catalog-query' in html,(path,"catalog search input missing")
    assert 'data-catalog-category' in html,(path,"catalog category input missing")
print("XUYI_CATALOG_VISIBILITY_PASSED five-language filter/pagination CSS and JS invariants")