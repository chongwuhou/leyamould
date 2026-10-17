#!/usr/bin/env python3
"""Source-rendered SEO checks: live Q/A, category cards and real SKU material."""
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"scripts"))
from seo_structured_components import visible_faq,actual_product_cards,add_at_render
from source_catalog_capacity_oz import verified_source_material,current_baseline,pre_render_verified_meta,catalog_volume_numbers
from site_renderer import SERIES
from cms_seo_curation_guard import snapshot
from copy import deepcopy

D=ROOT/"dist"
countfaq=countlists=countmaterials=0
for lang in ("en","es","pt","ru","tr"):
    prefix="" if lang=="en" else lang+"/"
    for obj in SERIES.values():
        file=D/prefix/"products"/obj["slug"]/"index.html"
        assert file.is_file(),file
        page=file.read_text(encoding="utf8")
        nodes=[json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>',page,re.S)]
        faq=[s for s in nodes if s.get("@type")=="FAQPage"]
        values=visible_faq(page)
        assert len(faq)==int(bool(values)),(lang,obj["slug"],values)
        if values:
            entity=faq[0]
            assert entity["inLanguage"]==lang
            assert [x["name"] for x in entity["mainEntity"]]==[q for q,a in values]
            assert [x["acceptedAnswer"]["text"] for x in entity["mainEntity"]]==[a for q,a in values]
            assert add_at_render(page,"/"+prefix+"products/"+obj["slug"]+"/",lang)==page
            countfaq+=1
        title=re.search(r"<title>(.*?)</title>",page).group(1)
        material=verified_source_material(obj)
        if material and catalog_volume_numbers(obj) and current_baseline(lang,obj) and "透明款" not in str(obj["model"]):
            assert material in title,(lang,obj["slug"],material,title)
            countmaterials+=1
    for kind in ("sports-water-bottles","kids-water-bottles","large-capacity-water-jugs","plastic-shaker-bottles"):
        route="/"+prefix+"collections/"+kind+"/"
        page=(D/route.lstrip("/")/"index.html").read_text(encoding="utf8")
        nodes=[json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>',page,re.S)]
        lists=[x for x in nodes if x.get("@type")=="ItemList"]
        urls=actual_product_cards(page)
        assert len(lists)==1 and len(urls)==lists[0]["numberOfItems"],(lang,kind)
        assert [x["url"] for x in lists[0]["itemListElement"]]==["https://xuyibottles.com"+url for url in urls]
        assert add_at_render(page,route,lang)==page
        countlists+=1

# CMS writer wins: the shared pre-render function cannot reapply default title
# once any owner-supplied SEO field is different from its versioned baseline.
snap=snapshot()
editable=deepcopy(snap)
match=next(item for item in editable["pages"] if item.get("route")=="/products/2095/")
match["seo_title"]="OWNER selected product title"
row=SERIES["2095"]
sample='<html><head><title>OWNER selected product title</title><meta name="description" content="Approved owner summary"></head><body></body></html>'
assert not current_baseline("en",row,editable)
assert pre_render_verified_meta(sample,"en",row,editable)==sample

# Synthetic changed CMS body wins over old FAQs.
test='<html><head></head><body><main><div class="faq-list"><details><summary>What is the owner selected lid?</summary><p>The exact selection is checked by the product manager.</p></details></div></main></body></html>'
added=add_at_render(test,"/products/test-model/","en")
assert "owner selected lid?" in added and added.count("FAQPage")==1
assert add_at_render(added,"/products/test-model/","en")==added
print("XUYI_SOURCE_PRODUCT_FAQ_COLLECTION_ITEMLIST_MATERIAL_PASSED",countfaq,countlists,countmaterials)
