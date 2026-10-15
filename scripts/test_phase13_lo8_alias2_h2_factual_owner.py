#!/usr/bin/env python3
"""Phase13: native LO8 and factory transparent aliases, owner-safe five locale H2."""
from pathlib import Path
from hashlib import sha256
import json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from site_renderer import SERIES
from product_content import details
from lo_catalog import detail as lo_detail
from sku_factual_sections import PEERS,FIFTH10,BASE,FOCUS,LANGS,section,apply,facts,material_annotation
from seo_structured_components import visible_faq,add_at_render
from product_material_performance import inject as inject_materials
ROOT=Path(__file__).resolve().parent.parent
by_slug={r["slug"]:r for r in SERIES.values()}
d1=json.loads((ROOT/"_local_ops/build-snapshot.json").read_text(encoding="utf8"))["translations"]
owner={(r["resourceId"][5:],r["locale"]):r["content"]["mainHtml"] for r in d1 if r.get("resourceId","").startswith("page:")}
assert len(PEERS)==90 and len(FIFTH10)==10 and len(BASE)==len(FOCUS)==90
seen=0
for slug,peer in FIFTH10.items():
 row=by_slug[slug];lo=slug.startswith("lo-")
 assert row["category"]==SERIES[peer]["category"]
 for lang in LANGS:
  if lo:
   assert ("/products/"+slug+"/",lang) not in owner,(slug,lang)
   original=lo_detail(row,lang)
  else:
   original=details(row) if lang=="en" else owner[("/products/"+slug+"/",lang)]
  updated=apply(original,row,lang)
  assert apply(updated,row,lang)==updated
  data=facts(row,lang,SERIES)
  assert data["sku"] and data["peer"] and data["mat"] not in ("To confirm","")
  if lo:
   assert any(w in data["dims"] for w in ("approx","aprox","прибл","yaklaşık"))
  for kind in ("design","faq"):
   old=section(original,kind);new=section(updated,kind)
   assert old and new,(slug,lang,kind)
   assert sha256(old[2].encode("utf8")).hexdigest()[:16]==BASE[slug][lang][kind]
   assert old[2]!=new[2] and data["sku"] in new[2] and data["peer"] in new[2]
   edit=old[2].replace('<div class="shell">','<div class="shell" data-cms-owner="yes">',1)
   customized=original[:old[0]]+edit+original[old[1]:]
   assert section(apply(customized,row,lang),kind)[2]==edit,(slug,lang,kind,"owner change lost")
   other="faq" if kind=="design" else "design"
   assert section(apply(customized,row,lang),other)[2]!=section(customized,other)[2]
  page=(ROOT/"dist"/("" if lang=="en" else lang)/"products"/slug/"index.html").read_text(encoding="utf8")
  assert page.count('data-sku-material="'+slug+'"')==1
  assert material_annotation(row,lang) in page
  assert 'data-sku-focus="'+slug+'"' in page
  for kind in ("design","faq"):assert section(page,kind)[2]==section(updated,kind)[2]
  visible=visible_faq(page)
  assert len(visible)==4 and all(data["sku"] in q for q,a in visible),(slug,lang,"FAQ")
  schemas=[z for txt in re.findall(r'<script type="application/ld\+json">(.*?)</script>',page,re.S)
    if isinstance((z:=json.loads(txt)),dict) and z.get("@type")=="FAQPage"]
  assert len(schemas)==1
  assert [(x["name"],x["acceptedAnswer"]["text"]) for x in schemas[0]["mainEntity"]]==visible
  seen+=1
# Simulated owner-selected native LO content must beat the earlier template.
lo=by_slug["lo-003"];base=lo_detail(lo,"es")
old=section(base,"faq")
custom='<section class="section section--soft"><div class="shell"><div class="faq-list"><details><summary>Pregunta del editor LO-003?</summary><p>Confirme en el ejemplar físico el embalaje.</p></details></div></div></section>'
body=base[:old[0]]+custom+base[old[1]:]
assert section(apply(body,lo,"es"),"faq")[2]==custom
html='<html><head></head><body><main id="main-content">'+apply(body,lo,"es")+'</main></body></html>'
assert visible_faq(add_at_render(html,"/es/products/lo-003/","es"))==[("Pregunta del editor LO-003?","Confirme en el ejemplar físico el embalaje.")]
mat=base.replace('<section class="section section--soft product-content">','<section class="section material-brief" id="material-performance"><div>Editor-owned material evidence</div></section><section class="section section--soft product-content">',1)
assert mat!=base and inject_materials(mat,lo,"es","/products/lo-003/")==mat
for sku in ("2506","5247","5248","G-01","G-03"):
 row=SERIES[sku]
 assert apply(details(row),row,"en")==details(row) and not material_annotation(row,"en")
assert by_slug["2306---"]["model"]=="2306透明款"
assert by_slug["2308---"]["model"]=="2308透明款"
assert by_slug["2306---"]["capacity"]=="1600ml" and by_slug["2308---"]["capacity"]=="2400ml"
future={**lo,"slug":"lo-new-2027","model":"LO-NEW"}
assert apply(base,future,"es")==base
print("XUYI_PHASE13_LO8_ALIAS2_H2_CMS_OWNER_FIVE_LOCALE_SCHEMA_PASSED",seen)