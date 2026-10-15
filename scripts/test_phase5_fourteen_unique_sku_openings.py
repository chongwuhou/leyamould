#!/usr/bin/env python3
"""Phase five: 14 reviewed SKU intros in 5 locales; source facts & owner-edit priority."""
from pathlib import Path
from hashlib import sha256
from html import unescape
import json,re,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES
from product_slug_fix import route as canonical_product_route
from sku_unique_openings import editor_intro
from sku_unique_openings_phase2 import COPY,SELECTED_GROUP,CATEGORY
LANGS=("en","es","pt","ru","tr")
CATEGORIES=json.loads((ROOT/"data/phase5-next14-openings-en.json").read_text(encoding="utf8"))["groups"]
BASELINES=json.loads((ROOT/"data/phase5-next14-d1-baselines.json").read_text(encoding="utf8"))["hashes"]
SELECTED={slug:group for group,entries in CATEGORIES.items() for slug in entries}
EXPECTED=set("2470 2400-transparent 2401-transparent 2212 2400 2099 2100 5299 5340 8563 2307-transparent 2306-transparent 2308-transparent 6252".split())
assert len(SELECTED)==14 and set(SELECTED)==EXPECTED
assert set(BASELINES)==EXPECTED and all(len(v)==4 for v in BASELINES.values())
STATE=json.loads((ROOT/"_local_ops/build-snapshot.json").read_text(encoding="utf8"))
D1={(canonical_product_route(r["resourceId"][5:]),r["locale"]):r["content"]["mainHtml"]
    for r in STATE["translations"] if r.get("resourceId","").startswith("page:")}
records=[]
for sku,group in SELECTED.items():
 row=next(r for r in SERIES.values() if r["slug"]==sku)
 assert row["category"]==CATEGORY[group],(sku,group)
 assert set(COPY[sku])==set(LANGS)
 for lang in LANGS:
  content=COPY[sku][lang]
  assert 100<=len(content.split())<=150,(sku,lang,len(content.split()))
  assert sku in content,(sku,lang)
  assert "spor şapkalar" not in content.casefold()
  route="/products/"+sku+"/"
  source=D1.get((route,lang)) if lang!="en" else None
  if lang!="en":
   assert isinstance(source,str),(sku,lang,"missing D1 source")
   digest=sha256(source.encode("utf8")).hexdigest()
   expected=BASELINES[sku][lang]
   if digest!=expected:
    # If the real owner changed the CMS body, do not revert it or demand a
    # stale intro marker in the subsequently generated page.
    assert editor_intro(source,row,lang)==source,(sku,lang,"owner edit overwritten")
   else:
    result=editor_intro(source,row,lang)
    assert content in unescape(result),(sku,lang,"intro missing in upstream body")
    assert editor_intro(result,row,lang)==result,(sku,lang,"not idempotent")
    owner=source.replace("<nav class=", '<nav data-fifth-owner-edit="true" class=',1)
    assert owner!=source
    assert editor_intro(owner,row,lang)==owner,(sku,lang,"CMS owner precedence")
    assert editor_intro(source,row,lang,owner_edited=True)==source
  dest=ROOT/"dist"/("" if lang=="en" else lang)/"products"/sku/"index.html"
  doc=dest.read_text(encoding="utf8")
  matches=re.findall(r'<p\b(?=[^>]*data-pilot-intro="'+re.escape(sku)+r'")[^>]*>(.*?)</p>',doc,re.S)
  if lang=="en" or (source and sha256(source.encode("utf8")).hexdigest()==BASELINES[sku][lang]):
   assert len(matches)==1,(sku,lang,"render missing")
   assert unescape(re.sub(r"<[^>]*>","",matches[0]))==content,(sku,lang,"wrong content")
  else:
   assert len(matches)<=1
  records.append((sku,lang,content))
for lang in LANGS:
 intros=[body for sku,l,body in records if l==lang]
 assert len(set(intros))==14,(lang,"duplicate buyer intro")
 starts=[" ".join(v.split()[:18]).casefold() for v in intros]
 assert len(set(starts))==14,(lang,"templated opening")
new={**next(x for x in SERIES.values() if x["slug"]=="2470"),"slug":"next-new-factory-model-2027","model":"NEW-2027"}
assert editor_intro('<h1>Future</h1><p class="copy-muted">Existing</p>',new,"en")=='<h1>Future</h1><p class="copy-muted">Existing</p>'
print("XUYI_PHASE5_14_UNIQUE_SKU_FIVE_LOCALES_CMS_PASSED",len(records),"routes")