#!/usr/bin/env python3
"""Reuse Demalong's managed-template contract; test XUYI navigation without D1 writes."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import site_renderer as site

names=("shell","header","footer","sidebar","home","listing","content","static","product-card","category-card","page-intro","catalog-filter","catalog-pagination","faq-list","product-spec","product-thumbnails","product-benefit","product-overview")
for name in names:
    template=site.read_template(name)
    assert template, name
    if name!="catalog-pagination":assert "{{" in template, name
    assert (Path("templates/site")/(name+".html")).exists()
assert '<section class="page-intro">' in site.intro("FAQ","FAQ","Questions")
assert '<div class="filterbar">' in site.filters()
assert '<div class="pagination">' in site.pagination()
assert '<div class="faq-list">' in site.faq_html([("Question?","Answer")])
assert '<table class="spec">' in site.render_template("product-spec",ROWS="<tr><th>Model</th></tr>")
assert 'class="product-detail__thumbs"' in site.render_template("product-thumbnails",ITEMS="test")
assert 'class="section product-overview"' in site.render_template("product-overview",BREADCRUMB="",MAIN_PHOTO="",THUMBNAILS="",MODEL="2095",NAME="Sample",LEAD="Test",SPECS="",SLUG="2095")
header=site.header()
assert 'id="mobile-navigation"' in header
assert 'id="menu-products"' in header
assert 'data-language-switch' in header
assert 'data-mega-toggle' in header
original=site.BUILD_STATE.get("navigation")
try:
    site.BUILD_STATE["navigation"]=[
      {"id":"home","url":"/","label":"Home","parent_id":"","sort_order":10},
      {"id":"products","url":"/products/","label":"Products","parent_id":"","sort_order":20},
      {"id":"sample-extra","url":"/faq/","label":"Sample Options",
       "parent_id":"","sort_order":75,"new_window":False}
    ]
    changed=site.header()
    assert "Sample Options" not in header
    assert changed.count(">Sample Options</a>")==2, "Custom D1 nav must reach desktop and mobile"
    assert '<div class="mega" id="menu-products">' in changed
finally:
    if original is None: site.BUILD_STATE.pop("navigation",None)
    else: site.BUILD_STATE["navigation"]=original
print("XUYI_SHARED_TEMPLATES_NAV_REGRESSION_PASSED",len(names),"templates")