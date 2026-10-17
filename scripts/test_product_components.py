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
    count+=1
assert count==len(site.SERIES) and count>=93,count
print("XUYI_PRODUCT_DETAILS_TEMPLATE_REGRESSION_PASSED",count,"models")
