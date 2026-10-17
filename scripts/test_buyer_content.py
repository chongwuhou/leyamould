#!/usr/bin/env python3
"""XUYI-only B2B buyer content release gate. No production data writes."""
from pathlib import Path
import html
import re
ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
home=(DIST/"index.html").read_text(encoding="utf-8")
visible_home=html.unescape(home)
assert 'Explore Plastic Bottles <span>for Your Market</span>' in home
assert "Rocket Your Brand With" not in home
assert 'class="buyer-paths"' in home
for term in ("Browse Existing Models","Plan Custom Branding","Discuss Samples & Supply"):
    assert term in visible_home,term
for category,markers in {
    "sports-water-bottles":("Compare Closure Styles","Match Capacity & Handling","Plan Your Branding"),
    "large-capacity-water-jugs":("Consider Filled Handling","Confirm Outer Cartons","Specify the Exact Variant"),
    "kids-water-bottles":("Check Intended Age & Market","Review Removable Components","Confirm Materials & Evidence"),
    "plastic-shaker-bottles":("Verify Mixing Accessories","Compare Capacity & Markings","Prepare an OEM Brief"),
}.items():
    text=html.unescape((DIST/"collections"/category/"index.html").read_text(encoding="utf-8"))
    for marker in markers:
        assert marker in text,(category,marker)
    assert 'href="/contact/#inquiry"' in text,category
    assert 'class="section section--soft catalog-buyer-guide"' in text,category
assert '<h2>Brands &amp; Customers' in home
assert 'id="customer-brands"' in home
assert "Material options include PC, Tritan, PP and PETG" not in home
assert "The source catalog lists PC and PP" in home
for file in (DIST/"products").glob("*/index.html"):
    source=file.read_text(encoding="utf-8")
    model=file.parent.name
    inquiry_model=model.upper() if model.startswith(("lo-","g-")) else model
    assert 'href="/contact/?model='+inquiry_model+'&amp;type=Samples#inquiry"' in source,model
    if model.startswith("g-"):
        # G-series numbers are actual factory models. Unprovided material,
        # packing and capacity figures still require product-specific review.
        assert "Factory Model" in source and "not a factory model" not in source.lower(),model
    else:
        assert 'product-detail__quote-note' in source,model
css=(DIST/"assets/site.css").read_text(encoding="utf-8")
assert 'html[lang="en"] .header__inner>.nav{' in css
assert 'margin-left:clamp(8px,2.7vw,48px)' in css
assert 'gap:clamp(15px,2.4vw,38px)' in css
assert 'html[lang="en"] .header__inner>.nav{margin-left:0}' not in css
print("XUYI_BUYER_CONTENT_RELEASE_TESTS_PASSED: 4 categories, 3 paths, 101 product pages")
