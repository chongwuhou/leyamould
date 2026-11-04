#!/usr/bin/env python3
"""Source-release SEO gate: real visible FAQ, company bylines, image dimensions.

Tests dynamic published routes. No synthetic Offer, reviews, employee or price.
Actual approved D1 SKU reviews are permitted only if visible and identical.
"""
from pathlib import Path
import html
import json
import os
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
SNAPSHOT=ROOT/"_local_ops/build-snapshot.json"
if SNAPSHOT.is_file():os.environ["XUYI_BUILD_SNAPSHOT"]=str(SNAPSHOT)
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES
from product_reviews_source import published_reviews,schema_properties,owner_schema_reviews
STATE=json.loads(SNAPSHOT.read_text("utf8")) if SNAPSHOT.is_file() else {}
MODELS_BY_SLUG={str(p["slug"]):str(p["model"]) for p in SERIES.values()}
from product_slug_fix import route as canonical_product_route
OWNER_BODIES={}
for row in STATE.get("pageBodies",[]):
    if isinstance(row,dict):OWNER_BODIES[(str(row.get("route")),"en")]=str(row.get("mainHtml",""))
for row in STATE.get("translations",[]):
    if not isinstance(row,dict):continue
    resource_id=str(row.get("resourceId",""));locale=str(row.get("locale",""));fields=row.get("content") or {}
    if not resource_id.startswith("page:") or locale not in LANGS or not isinstance(fields,dict):continue
    route=canonical_product_route(resource_id[5:])
    if route.startswith("/products/"):
        OWNER_BODIES.setdefault((route,locale),str(fields.get("mainHtml","")))
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
        post=[v for obj in objs for v in (obj.get("@graph",[]) if isinstance(obj,dict) and isinstance(obj.get("@graph"),list) else [obj]) if isinstance(v,dict) and v.get("@type")=="BlogPosting"]
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
        assert product.get("name") and product.get("sku")
        images=product.get("image",[])
        assert all("/excel/" not in path for path in images),(lang,route)
        assert product["potentialAction"]["@type"]=="CommunicateAction"
        action_url=product["potentialAction"]["target"]["urlTemplate"]
        assert "contact/?model=" in action_url and "#inquiry" in action_url,(lang,route,action_url)
        assert "offers" not in product,(lang,route,"invented price/offer")
        model=MODELS_BY_SLUG.get(route.parent.name)
        assert model,(lang,route,"review model must exist in canonical product data")
        canonical_sku=str(product.get("sku","")).replace(" (Transparent Variant)","透明款")
        assert canonical_sku==str(model),(lang,route,"Product SKU must equal canonical model",product.get("sku"),model)
        approved=published_reviews(STATE,model)
        owner_body=OWNER_BODIES.get(("/products/"+route.parent.name+"/",lang),"")
        owner_review=re.search(r'<section\b[^>]*\bid="xuyi-customer-reviews"[^>]*>.*?</section>',owner_body,re.S)
        # The Product JSON-LD may itself be an owner-controlled CMS field.
        # The renderer preserves it and mirrors those same reviews visibly.
        owner_schema=owner_schema_reviews(markup,model)
        if owner_schema == [] and not owner_review:
            assert product.get("aggregateRating") and not product.get("review"),(lang,route,"owner aggregate-only schema was changed")
            assert 'id="xuyi-customer-reviews"' not in markup,(lang,route,"aggregate-only owner schema must not fabricate review cards")
        elif owner_review or owner_schema is not None:
            section_match=owner_review or re.search(r'<section\b[^>]*\bid="xuyi-customer-reviews"[^>]*>.*?</section>',markup,re.S)
            if owner_review:
                assert owner_body.count('id="xuyi-customer-reviews"')==1
            if owner_schema:
                assert section_match,(lang,route,"owner Product review schema needs a visible review module")
            owner_section=section_match.group(0) if section_match else ""
            if owner_section:
                assert owner_section in markup and markup.count('id="xuyi-customer-reviews"')==1,(lang,route,"owner review module missing/doubled")
            visible=[]
            for card in re.findall(r'<article class="product-review">(.*?)</article>',owner_section,re.S):
                rating=re.search(r'aria-label="([1-5]) out of 5 stars"',card)
                author=re.search(r'<strong>(.*?)</strong>',card,re.S)
                review_date=re.search(r'<time datetime="([0-9]{4}-[0-9]{2}-[0-9]{2})"',card)
                body=re.search(r'<p class="product-review__text">(.*?)</p>',card,re.S)
                assert rating and author and review_date and body,(lang,route,"invalid owner review card")
                visible.append((int(rating.group(1)),html.unescape(author.group(1)),review_date.group(1),
                                html.unescape(body.group(1)).replace("<br>","\n")))
            schema_raw=product.get("review")
            if isinstance(schema_raw,dict):schema_raw=[schema_raw]
            schema_rows=[]
            for item in (schema_raw or []):
                author=item.get("author")
                author=author.get("name") if isinstance(author,dict) else author
                schema_rows.append((item.get("reviewRating",{}).get("ratingValue"),author,
                                    item.get("datePublished"),item.get("reviewBody")))
            if schema_rows:
                assert schema_rows==visible,(lang,route,"Product schema must match owner review content")
            if owner_schema is not None:
                assert visible==[(x["rating"],x["author"],x["reviewDate"],x["content"]) for x in owner_schema],(lang,route,"owner Product schema not rendered visibly")
            aggregate=product.get("aggregateRating")
            if aggregate and visible:
                assert aggregate.get("reviewCount")==len(visible) and aggregate.get("ratingValue")==round(sum(row[0] for row in visible)/len(visible),2),(lang,route,"aggregate rating must match owner review content")
        elif not approved:
            assert not any(field in product for field in ("review","aggregateRating")),(lang,route,"fabricated reviews")
            assert 'id="xuyi-customer-reviews"' not in markup,(lang,route,"unapproved visible feedback")
        else:
            props=schema_properties(approved)
            assert product.get("review")==props["review"],(lang,route,"rating/body mismatch with D1")
            assert product.get("aggregateRating")==props.get("aggregateRating"),(lang,route,"invented aggregate")
            assert markup.count('id="xuyi-customer-reviews"')==1,(lang,route,"review must be visible")
            assert markup.count('class="product-review"')==len(approved),(lang,route,"public count mismatch")
            for record in approved:
                assert html.escape(record["author"]) in markup,(lang,route,"customer name not visible")
                assert html.escape(record["content"]).replace("\n","<br>") in markup,(lang,route,"customer words not visible")
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