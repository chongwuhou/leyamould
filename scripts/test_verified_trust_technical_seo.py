#!/usr/bin/env python3
"""Source-release SEO gate: real visible FAQ, company bylines, image dimensions.

Tests dynamic published routes. No synthetic Offer, reviews, employee or price.
"""
from pathlib import Path
import html
import json
import re
import sys
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from verified_trust_technical_seo import (
    LANGS,ORIGIN,faq_from_visible,image_dimensions,improve_home,improve_article,
    improve_product,improve_og,checked_image_size
)

DIST=ROOT/"dist"
faq_count=blog_count=product_count=og_count=0
for lang,prefix in LANGS.items():
    home=DIST/prefix/"index.html"
    page=home.read_text(encoding="utf8")
    visibles=faq_from_visible(page)
    assert visibles and len(visibles)==5,(lang,"missing visible FAQ")
    graphs=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',page,re.S)]
    faq=[x for x in graphs if x.get("@type")=="FAQPage"]
    assert len(faq)==1,(lang,"home FAQ graph count",len(faq))
    node=faq[0]
    assert node["inLanguage"]==lang and node["url"]==ORIGIN+"/"+prefix
    assert [(q["name"],q["acceptedAnswer"]["text"]) for q in node["mainEntity"]]==visibles
    assert improve_home(page,lang)==(page,0),(lang,"home FAQ double appended")
    assert 'id="customer-brands"' in page,(lang,"brand marks unintentionally removed")
    faq_count+=1

    for route in sorted((DIST/prefix/"blog").glob("*/index.html")):
        markup=route.read_text(encoding="utf8")
        assert markup.count('class="blog-author-byline"')==1,(lang,route)
        match=re.search(r'<p class="blog-author-byline"><a rel="author" href="([^"]+)">',markup)
        assert match and match.group(1)=="/"+prefix+"about/",(lang,route)
        assert (DIST/prefix/"about/index.html").is_file()
        objs=[json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>',markup,re.S)]
        post=[v for obj in objs for v in obj.get("@graph",[]) if v.get("@type")=="BlogPosting"]
        assert len(post)==1,(lang,route)
        author=post[0]["author"]
        assert author["@type"]=="Organization" and author["name"]=="XUYI Bottles"
        assert author["url"]==ORIGIN+"/"+prefix+"about/"
        assert improve_article(markup,lang)==(markup,0),(lang,route,"idempotence")
        blog_count+=1

    for route in sorted((DIST/prefix/"products").glob("*/index.html")):
        markup=route.read_text(encoding="utf8")
        objs=[json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>',markup,re.S)]
        products=[v for obj in objs for v in obj.get("@graph",[]) if v.get("@type")=="Product"]
        assert len(products)==1,(lang,route)
        product=products[0]
        assert product.get("name") and product.get("sku") and product.get("image")
        assert product["potentialAction"]["@type"]=="CommunicateAction"
        assert str(product.get("sku")) in product["potentialAction"]["target"]["urlTemplate"]
        assert not any(field in product for field in ("offers","review","aggregateRating")),(lang,route,"fabricated commerce data")
        assert improve_product(markup,lang)==(markup,0),(lang,route,"idempotence")
        product_count+=1

for f in DIST.rglob("index.html"):
    if "admin" in f.relative_to(DIST).parts[:1]:continue
    text=f.read_text(encoding="utf8")
    head=text.partition("</head>")[0]
    m=re.search(r'<meta property="og:image" content="([^"]+)"',head)
    if not m:continue
    dims=image_dimensions(m.group(1))
    if dims:
        w=re.search(r'<meta property="og:image:width" content="([^"]+)"',head)
        h=re.search(r'<meta property="og:image:height" content="([^"]+)"',head)
        assert w and h and (int(w.group(1)),int(h.group(1)))==dims,(f,dims)
        assert improve_og(text)==(text,0),f
        og_count+=1

content=(DIST/"llms.txt").read_text(encoding="utf8")
assert content.startswith("# XUYI Bottles")
assert len(content.splitlines())>20
assert "https://xuyibottles.com/blog/tritan-vs-pp-petg-pc/" in content
assert "Prices, MOQ, materials" in content
for label,url in re.findall(r'- \[([^\]]+)\]\((https://xuyibottles.com/[^\)]+)\)',content):
    target=url[len(ORIGIN):]
    assert (DIST/target.lstrip("/")/"index.html").is_file(),(label,url)
assert faq_count==5 and blog_count>=80 and product_count>=505,(faq_count,blog_count,product_count)
assert og_count>=150,og_count
print("XUYI_TRUST_TECHNICAL_SEO_GATE_PASSED",json.dumps({
    "homeFAQ":faq_count,"visibleOrgBlogBylines":blog_count,"honestQuoteActions":product_count,
    "verifiedOgImageDimensions":og_count,"llmsText":True
},sort_keys=True))