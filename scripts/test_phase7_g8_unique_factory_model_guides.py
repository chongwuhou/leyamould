#!/usr/bin/env python3
"""Verify eight actual G factory photo models: five-language buyer guides, no fabricated specs."""
from pathlib import Path
from hashlib import sha256
from html import unescape
import json,re,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES
from gallery_catalog import GALLERY,detail
from sku_unique_openings import editor_intro
from sku_unique_openings_phase2 import COPY,CATEGORY
LANGS=("en","es","pt","ru","tr")
GROUPS=json.loads((ROOT/"data/phase7-g8-buyer-guides-en.json").read_text(encoding="utf8"))["groups"]
BASE=json.loads((ROOT/"data/phase7-g8-gallery-template-baselines.json").read_text(encoding="utf8"))["hashes"]
SELECTED={sku:group for group,items in GROUPS.items() for sku in items}
INDEX={g["slug"]:g for g in GALLERY}
assert len(SELECTED)==8 and set(SELECTED)==set(INDEX)==set(BASE)
assert all(set(BASE[s])==set(LANGS[1:]) for s in SELECTED)
SNAP=json.loads((ROOT/"_local_ops/build-snapshot.json").read_text(encoding="utf8"))
D1={(r["resourceId"][5:],r["locale"]):r["content"]["mainHtml"]
    for r in SNAP["translations"] if r.get("resourceId","").startswith("page:")}
count=0
for sku,category in SELECTED.items():
    source=INDEX[sku]
    product=SERIES[source["model"]]
    assert product["slug"]==sku and product["category"]==CATEGORY[category]
    assert product.get("factoryModel") and product.get("galleryReference"),sku
    assert product["capacity"]=="To confirm" and product["material"]=="To confirm",sku
    assert len(source["images"])>=2
    assert set(COPY[sku])==set(LANGS)
    for locale in LANGS:
        paragraph=COPY[sku][locale]
        assert 100<=len(paragraph.split())<=150,(sku,locale,len(paragraph.split()))
        assert sku.casefold() in paragraph.casefold()
        assert not re.search(r'\d+(?:[.,]\d+)?\s*(?:ml|oz|cm|mm|lit(?:er|re))\b',paragraph,re.I),(sku,locale,"unverified capacity or dimensions")
        assert ("/products/"+sku+"/",locale) not in D1,(sku,locale,"source is not sole owner")
        body=detail(product,locale)
        if locale!="en":
            assert sha256(body.encode("utf8")).hexdigest()==BASE[sku][locale],(sku,locale,"G source template drift")
        revised=editor_intro(body,product,locale)
        assert revised!=body,(sku,locale,"buyer intro missing")
        assert paragraph in unescape(revised)
        assert editor_intro(revised,product,locale)==revised,(sku,locale,"duplicate injection")
        custom=body.replace('<nav class="breadcrumb">','<nav class="breadcrumb" data-owner-replaced="yes">',1)
        assert custom!=body
        if locale!="en":
            assert editor_intro(custom,product,locale)==custom,(sku,locale,"edited CMS translation overwritten")
        assert editor_intro(custom,product,locale,owner_edited=True)==custom
        path=ROOT/"dist"/("" if locale=="en" else locale)/"products"/sku/"index.html"
        rendered=path.read_text(encoding="utf8")
        matches=re.findall(r'<p\b(?=[^>]*data-pilot-intro="'+re.escape(sku)+r'")[^>]*>(.*?)</p>',rendered,re.S)
        assert len(matches)==1,(sku,locale,"missing or duplicate")
        assert unescape(re.sub(r"<[^>]*>","",matches[0]))==paragraph,(sku,locale,"wrong buyer text")
        # Current model's originally source-backed pictures stay linked.
        assert source["images"][0] in rendered,(sku,locale,"factory model photo missing")
        if sku=="g-05":
            depth=re.search(r'<section class="section product-g05-depth"[\s\S]*?</section>',rendered)
            assert depth,(sku,locale,"G-05 depth section missing")
            depth_text=re.sub(r'<[^>]+>',' ',unescape(depth.group()))
            assert len(depth_text.split())>=220,(sku,locale,"G-05 content too thin",len(depth_text.split()))

        count+=1
for lang in LANGS:
    leads=[COPY[sku][lang] for sku in SELECTED]
    assert len(set(leads))==8
    assert len(set(" ".join(t.split()[:16]).casefold() for t in leads))==8
fake={**SERIES["G-01"],"slug":"g-future-2027","model":"G-FUTURE"}
original='<h1>New approved model</h1><p class="copy-muted">Original</p>'
assert editor_intro(original,fake,"en")==original
print("XUYI_G8_FACTORY_PHOTO_BUYER_GUIDES_OWNER_SAFE",count,"locale pages")
