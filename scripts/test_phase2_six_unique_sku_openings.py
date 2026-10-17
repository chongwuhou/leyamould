#!/usr/bin/env python3
"""Twenty second-wave real source-specific models x five languages, CMS precedence and no duplication."""
from pathlib import Path
import hashlib,html,json,re,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from sku_unique_openings import editor_intro
from sku_unique_openings_phase2 import COPY,CATEGORY,EN,OWNER,SELECTED_GROUP
from site_renderer import SERIES
from product_slug_fix import route as canonical_product_route
langs=("en","es","pt","ru","tr")
assert len(COPY)>=48 and {"sports","kids","jugs"}.issubset(EN)
assert set("2511 2310 2319 2410 2280 2302 2512 2513 2514 2209 2311 2402 2109 2409 2413 2350 2250 2270 2416 2305".split()).issubset(COPY)
snapshot=json.loads((ROOT/"_local_ops/build-snapshot.json").read_text(encoding="utf8"))
d1={(canonical_product_route(v["resourceId"][5:]),v["locale"]):v["content"]["mainHtml"]
    for v in snapshot["translations"]
    if v.get("resourceId","").startswith("page:") and v["locale"] in langs[1:]}
assert len(set(COPY))==len(COPY)
D1_SKUS=tuple(sku for sku in COPY if not sku.startswith(("lo-","g-")))
assert len(D1_SKUS)+sum(sku.startswith(("lo-","g-")) for sku in COPY)==len(COPY) # G/LO template-owned translated bodies tested separately
for sku in D1_SKUS:
 paragraphs=COPY[sku]
 row=next(r for r in SERIES.values() if r["slug"]==sku)
 assert row["category"]==CATEGORY[SELECTED_GROUP[sku]]
 assert set(paragraphs)==set(langs)
 for locale,copy in paragraphs.items():
  count=len(copy.split())
  assert 100<=count<=150,(sku,locale,count)
  assert sku in copy
  page=ROOT/"dist"/("" if locale=="en" else locale)/"products"/sku/"index.html"
  data=page.read_text(encoding="utf8")
  matches=re.findall(r'<p\b(?=[^>]*data-pilot-intro="'+sku+r'")[^>]*>(.*?)</p>',data,re.S)
  assert len(matches)==1,(sku,locale,len(matches))
  assert html.unescape(re.sub(r"<[^>]*>","",matches[0]))==copy,(sku,locale)
  assert data.find("<h1")<data.find('data-pilot-intro="'+sku+'"')
  if locale!="en":
   source=d1[("/products/"+sku+"/",locale)]
   assert hashlib.sha256(source.encode("utf8")).hexdigest()==OWNER[sku][locale]
   rewritten=editor_intro(source,row,locale)
   assert rewritten!=source and copy in html.unescape(rewritten)
   assert editor_intro(rewritten,row,locale)==rewritten
   owner_revised=source.replace("<nav class=", '<nav data-owner-changed="yes" class=',1)
   assert owner_revised!=source
   assert editor_intro(owner_revised,row,locale)==owner_revised
   assert editor_intro(source,row,locale,owner_edited=True)==source
for locale in langs:
 leads=[COPY[sku][locale] for sku in D1_SKUS]
 assert len(set(leads))==len(leads)
 # Different facts and framing beyond the SKU and numerical capacity.
 starts=[" ".join(COPY[sku][locale].split()[:16]).lower() for sku in D1_SKUS]
 assert len(set(starts))==len(starts)
new={**SERIES["2511"],"slug":"new-factory-model-2027","model":"NEW-2027"}
original='<h1>Future</h1><p class="copy-muted">Source text</p>'
assert editor_intro(original,new,"en")==original
print("PHASE2_TO_PHASE5_D1_SOURCE_COPY_PASSED",len(D1_SKUS)*len(langs),"localized routes")
