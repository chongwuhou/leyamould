#!/usr/bin/env python3
"""Validate all published source-catalog product detail templates.

Approved D1 product edits are allowed to change text or photos. The invariant
is complete rendering of all core detail sections and valid model routes.
"""
from pathlib import Path
import sys,re
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import site_renderer as site
ROOT=Path(__file__).resolve().parent.parent
count=0
for model,product in site.SERIES.items():
    path=ROOT/"dist"/"products"/(product["slug"])/"index.html"
    assert path.is_file(),(model,"missing detail")
    doc=path.read_text(encoding="utf8")
    for element in ('class="section product-overview"','class="product-detail__thumbs"',
                    'class="spec"','class="section product-ordering"',
                    'class="section section--soft product-content"','class="faq-list"',
                    'data-main-photo=', 'id="main-photo"'):
        assert element in doc,(model,element)
    main=doc.split('<main id="main-content">',1)[1].split("</main>",1)[0]
    assert len(re.findall(r"<h1(?:\s[^>]*)?>",main))==1,model
    assert "{{" not in main and "}}" not in main,model
    inquiry_model=product["model"] if product.get("loNew") or product.get("galleryReference") else product["slug"]
    assert 'href="/contact/?model='+inquiry_model+'&amp;type=Samples#inquiry"' in main,model
    assert 'href="/contact/?model='+inquiry_model+'#inquiry"' in main,model
    # New PPT factory products have English detail pages until each translation is
    # separately reviewed and published. Localized catalog cards link to the
    # English specification rather than fabricating untranslated detail pages.
    is_new_factory = product.get("manualNew") is True and product.get("sourceDocument") in {"puyunsm(1).pdf", "水杯最新产品.pptx"}
    for locale in ("en","es","pt","ru","tr"):
        localized=ROOT/"dist"/("" if locale=="en" else locale)/"products"/product["slug"]/"index.html"
        if is_new_factory and locale != "en" and not localized.is_file():
            continue
        assert localized.is_file(),(model,locale,"missing locale")
        html=localized.read_text(encoding="utf8")
        main_html=html.split('<main id="main-content">',1)[1].split("</main>",1)[0]
        h1=re.search(r"</h1>",main_html,re.I)
        assert h1,(model,locale,"missing H1")
        after=main_html[h1.end():]
        assert re.match(r'\s*(?:<div class="product-detail__lead"><p class="copy-muted">|<p\b[^>]*\bclass="[^"]*\bcopy-muted\b[^"]*"[^>]*>)',after),(model,locale,"intro not directly after H1")
        assert main_html.count('class="product-detail__lead"')<=1,(model,locale,"duplicate intro")
    count+=1
assert count==len(site.SERIES) and count>=93,count
print("XUYI_PRODUCT_DETAILS_TEMPLATE_REGRESSION_PASSED",count,"models")