#!/usr/bin/env python3
"""No fabricated ratings; verified SKU-specific reviews survive five locales."""
from pathlib import Path
import json
import html
import re
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from product_reviews_source import at_product_source,published_reviews,render_visible,schema_properties,owner_schema_reviews

def nodes(content):
    found=[]
    for raw in re.findall(r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',content,re.I|re.S):
        obj=json.loads(raw)
        found.extend(x for x in obj.get("@graph",[obj]) if isinstance(x,dict) and x.get("@type")=="Product")
    return found

one={"id":"d55abf0c-71ca-4dd2-a3ab-a4107e62fd83","model":"2305","rating":5,"author":"Maria & Sons",
     "reviewDate":"2026-09-21","content":"Actual customer feedback & intact cartons on arrival.","status":"published"}
two={"id":"4c66bdd0-72ae-4ff0-ad18-6a3dba05d74d","model":"2305","rating":4,"author":"Buyer Test",
     "reviewDate":"2026-10-11","content":"Fits our stated packaging specifications for this shipment.","status":"published"}
draft={**one,"id":"ac66b235-2247-4b01-9487-039a82b83e27","rating":1,"status":"draft"}
other={**one,"id":"41cb7997-f0c2-47b5-9e22-3f67f276f1ba","model":"2291"}
malicious={**two,"id":"eb7b3e05-4cf4-4e7b-bce0-e9f33a92b4b3",
           "content":"A script tag <script>alert('x')</script> must render as text, never execute."}
assert published_reviews({}, "2305")==[]
assert published_reviews({"productReviews":[draft,other]},"2305")==[]
assert len(published_reviews({"productReviews":[one,one]},"2305"))==1
assert schema_properties([one])["review"]["reviewRating"]["ratingValue"]==5
assert "aggregateRating" not in schema_properties([one])
properties=schema_properties([one,two])
assert properties["aggregateRating"]["reviewCount"]==2
assert properties["aggregateRating"]["ratingValue"]==4.5
assert "offers" not in properties
assert "Maria &amp; Sons" in render_visible([one],"2305","en")
assert "&lt;script&gt;" in render_visible([malicious],"2305","en")
assert "<script>" not in render_visible([malicious],"2305","en")
transparent={"productReviews":[{**one,"model":"2306透明款"}]}
sample_html=('<html><head><script type="application/ld+json">'
             '{"@context":"https://schema.org","@graph":[{"@type":"Product",'
             '"name":"Transparent jug","sku":"2306 (Transparent Variant)"}]}'
             '</script></head><body><main>Real product body</main></body></html>')
transparent_html=at_product_source(sample_html,"2306透明款","en",transparent)
assert nodes(transparent_html)[0]["review"]["reviewRating"]["ratingValue"]==5
owner_schema_page=('<html><head><script type="application/ld+json">'+
                    json.dumps({"@context":"https://schema.org","@graph":[
                        {"@type":"Product","name":"Owner reviewed jug","sku":"2305",**schema_properties([one])}
                    ]})+
                    '</script></head><body><main>Owner product content.</main></body></html>')
owner_schema_rendered=at_product_source(owner_schema_page,"2305","en",{"productReviews":[one,two]})
assert nodes(owner_schema_rendered)[0]["review"]==schema_properties([one])["review"]
assert 'id="xuyi-customer-reviews"' in owner_schema_rendered
assert "Maria &amp; Sons" in owner_schema_rendered and "Buyer Test" not in owner_schema_rendered
assert owner_schema_reviews(owner_schema_page,"2305")==[{
    "id":"owner-schema-2305-0","rating":5,"author":"Maria & Sons",
    "reviewDate":"2026-09-21","content":"Actual customer feedback & intact cartons on arrival."
}]

injection_fixture=('<html><head><script type="application/ld+json">'
                  '{"@context":"https://schema.org","@graph":[{"@type":"Product",'
                  '"name":"Review injection fixture","sku":"2305"}]}'
                  '</script></head><body><main>Fixture product body</main></body></html>')
for loc in ("en","es","pt","ru","tr"):
    path=ROOT/"dist"/("products/2305/index.html" if loc=="en" else loc+"/products/2305/index.html")
    assert path.is_file(),path
    original=path.read_text("utf8")
    source={"productReviews":[one,two,draft,other]}
    # Isolated source page: exercise D1 review injection without a pre-existing owner schema.
    assert at_product_source(injection_fixture,"2305",loc,{"productReviews":[]})==injection_fixture
    generated=at_product_source(injection_fixture,"2305",loc,source)
    assert generated.count('id="xuyi-customer-reviews"')==1,(loc,"visible")
    assert generated.count('class="product-review"')==2,(loc,"draft or other model leaked")
    assert "Maria &amp; Sons" in generated and "4.5/5 ★" in generated
    assert at_product_source(generated,"2305",loc,source)==generated,"rebuild must be idempotent"
    products=nodes(generated)
    assert len(products)==1,(loc,products)
    prod=products[0]
    assert prod.get("sku")=="2305"
    assert len(prod["review"])==2 and prod["aggregateRating"]["reviewCount"]==2
    assert prod["aggregateRating"]["ratingValue"]==4.5
    assert not prod.get("offers"),"Do not invent commercial prices"
    assert all(x["author"]["@type"]=="Person" and x["reviewBody"] for x in prod["review"])
    assert all(x["datePublished"] in ("2026-09-21","2026-10-11") for x in prod["review"])

    # A real page may already own its Product review schema or visible CMS module.
    owner=owner_schema_reviews(original,"2305")
    if owner is not None:
        preserved=at_product_source(original,"2305",loc,source)
        assert owner_schema_reviews(preserved,"2305")==owner,(loc,"owner schema changed")
        assert preserved.count('class="product-review"')==len(owner),(loc,"owner review count changed")
        for item in owner:
            assert html.escape(item["author"]) in preserved,(loc,"owner author missing")
            assert html.escape(item["content"]).replace("\n","<br>") in preserved,(loc,"owner words missing")
    elif 'id="xuyi-customer-reviews"' in original:
        assert at_product_source(original,"2305",loc,source)==original,(loc,"owner body module overwritten")
    else:
        generated_real=at_product_source(original,"2305",loc,source)
        assert generated_real.count('class="product-review"')==2,(loc,"D1 reviews not injected")

    # A real CMS owner-authored module is authoritative; never duplicate it.
    modified=original.replace("</main>",'<section id="xuyi-customer-reviews">Owner-edited feedback</section></main>',1)
    assert at_product_source(modified,"2305",loc,source)==modified
    # Other models can never inherit testimonials via the global site cache.
    assert at_product_source(original,"2095",loc,source)==original

assert "productReviews" in (ROOT/"functions/api/build-snapshot.js").read_text("utf8")
assert "status='published'" in (ROOT/"functions/api/build-snapshot.js").read_text("utf8")
reviews_source=(ROOT/"functions/_shared/product-reviews.js").read_text("utf8")
assert "source_url" in reviews_source and "可核验的 HTTPS 评价来源" in reviews_source
assert "product_reviews_source import at_product_source" in (ROOT/"site_renderer.py").read_text("utf8")
assert "product_reviews_source import at_product_source" in (ROOT/"scripts/render_locales.py").read_text("utf8")
admin=(ROOT/"admin/index.html").read_text("utf8")
assert 'data-admin-target="reviews"' in admin and 'id="review-admin-panel"' in admin
assert '<script src="/assets/admin-reviews.js" defer></script>' in admin
print("XUYI_AUTHENTIC_SKU_REVIEWS_SOURCE_5_LOCALES_CMS_OWNER_AND_SCHEMA_PASS")
