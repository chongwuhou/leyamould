#!/usr/bin/env python3
"""LO product publication gate: evidence, localization, SEO, links and images."""
import json
from pathlib import Path
import re
import sys
from html import unescape

ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
data=json.loads((ROOT/"data/lo-products.json").read_text(encoding="utf8"))
items=data["products"]
assert len(items)==8
assert {p["model"] for p in items}=={"LO-%03d"%n for n in range(1,9)}
langs=("en","es","pt","ru","tr")
titles={}
descriptions={}
links_seen=set()
for lang in langs:
    prefix="" if lang=="en" else lang+"/"
    listing=(DIST/prefix/"products/index.html").read_text(encoding="utf8")
    assert listing.count('data-product-card')>=101,(lang,"catalog item count")
    def card_urls(page):
        return [re.search(r'\bhref="([^"]+)"',m.group(0)).group(1)
                for m in re.finditer(r'<a\b[^>]*\bdata-product-card\b[^>]*>',page,re.I)]
    expected_lo=["/"+prefix+"products/lo-%03d/"%n for n in range(1,9)]
    listing_urls=card_urls(listing)
    assert listing_urls[:8]==expected_lo,(lang,"LO products must appear on the first page")
    assert len(listing_urls)==len(set(listing_urls)) and len(listing_urls)>=101,(lang,"duplicate/missing product")
    assert listing.count('data-new-product="true"')==8,(lang,"new arrivals marker")
    assert listing.count('class="product-card__new"')==8,(lang,"visible new arrivals badge")
    for product in items:
        model=product["model"]
        slug=product["slug"]
        assert model.lower()==slug
        assert product["material"]=="PC+PP",model
        assert len(product["images"])==3
        for im in product["images"]:
            assert im.startswith("/assets/lo/") and (DIST/im.lstrip("/")).is_file(),im
        detail_images=product.get("detailImages",[])
        assert [im["purpose"] for im in detail_images]==["lifestyle","design"],(model,"missing real product-detail panels")
        for detail in detail_images:
            assert detail["src"].startswith("/assets/lo/detail/") and (DIST/detail["src"].lstrip("/")).is_file(),detail
            assert detail["width"]==720 and detail["height"]>1500,(model,detail)
        doc=(DIST/prefix/"products"/slug/"index.html").read_text(encoding="utf8")
        head,main=doc.split("</head>",1)
        title=unescape(re.search(r"<title>([^<]+)</title>",head).group(1))
        desc=unescape(re.search(r'<meta name="description" content="([^"]+)"',head).group(1))
        assert title==product["locales"][lang]["seoTitle"],(model,lang,"title mismatch")
        assert desc==product["locales"][lang]["seoDescription"],(model,lang,"description mismatch")
        assert model in title and model in desc,(model,lang)
        assert len(title)<=90 and 60<=len(desc)<=180,(model,lang)
        assert title not in titles.setdefault(lang,set()),(model,lang,"duplicate title")
        assert desc not in descriptions.setdefault(lang,set()),(model,lang,"duplicate description")
        titles[lang].add(title);descriptions[lang].add(desc)
        assert doc.count("<h1>")==1 and product["locales"][lang]["title"] in doc
        assert 'id="material-performance"' in doc
        assert 'class="product-detail__thumbs"' in doc
        assert 'class="faq-list"' in doc
        assert "BPA" in main and "100" in main
        assert "PC+PP" in main
        assert "certified BPA-free" not in main.lower()
        assert "100°C rated" not in main.lower()
        assert all(im in doc for im in product["images"])
        assert doc.count('id="product-detail-photos"')==1,(lang,model)
        assert doc.count('class="lo-photo-details__figure"')==2,(lang,model)
        assert all(im["src"] in doc for im in detail_images),(lang,model,"missing long-form detail photos")
        assert "水杯_" not in doc and "/images/水杯" not in doc
        url="/"+prefix+"products/"+slug+"/"
        assert 'href="'+url+'"' in listing,(lang,model,"missing product card")
        for langcode in langs:
            translated=("" if langcode=="en" else "/"+langcode)+"/products/"+slug+"/"
            assert 'hreflang="'+langcode+'" href="https://xuyibottles.com'+translated+'"' in head,(lang,model,langcode)
        assert "https://xuyibottles.com"+url in head,(model,lang,"canonical")
        for im in product["images"]:
            assert doc.count(im)>=1
        links_seen.add(url)
    for category in {p["category"] for p in items}:
        from sys import path
        sys.path.insert(0,str(ROOT))
        from site_renderer import CAT
        folder=CAT[category][1]
        category_html=(DIST/prefix/"collections"/folder/"index.html").read_text(encoding="utf8")
        cat_urls=card_urls(category_html)
        new_urls=["/"+prefix+"products/"+p["slug"]+"/" for p in items if p["category"]==category]
        assert cat_urls[:len(new_urls)]==new_urls,(lang,folder,"new models buried after old category cards")
        assert len(cat_urls)==len(set(cat_urls)),(lang,folder,"duplicate cards")
        for product in items:
            if product["category"]==category:
                assert '/'+prefix+'products/'+product["slug"]+'/' in category_html,(lang,folder,product["model"])
sitemap=(DIST/"sitemap.xml").read_text(encoding="utf8")
assert sitemap.count("<loc>")>=755
assert len(links_seen)==40
for path in ("build.py","site_renderer.py","data/products.json"):
    assert not (DIST/path).exists()
config=json.loads((ROOT/"deployment/site.config.json").read_text(encoding="utf8"))
assert type(config["site"]["indexingApproved"]) is bool
css=(DIST/"assets/site.css").read_text(encoding="utf8")
# Long-form detail visuals need edge-to-edge responsive width without cropped
# photos. The lower request-quote CTA must keep the shared white-on-red button
# styling, not inherit the red color of an ordinary inline text link.
assert re.search(r'\.lo-photo-details__stack\s*\{[^}]*width:100vw;[^}]*max-width:100vw;[^}]*margin-inline:calc\(50% - 50vw\)',css)
assert re.search(r'\.lo-photo-details__figure img\s*\{[^}]*width:100%;height:auto;object-fit:contain',css)
assert '.product-content__cta a:not(.button){color:var(--red)}' in css
assert '.product-content__cta a{color:var(--red)}' not in css
print("XUYI_LO_LAUNCH_PASSED 8 models x 5 languages, 24 local photos, SEO/schema/catalog, explicit indexing gate followed")