#!/usr/bin/env python3
"""Synthetic end-to-end XUYI manual SKU page and one approved translation.

Uses a temporary local build snapshot, never D1 or production. Restore original
snapshot and release artifact even if a synthetic assertion fails.
"""
from pathlib import Path
import json,subprocess,sys,re
ROOT=Path(__file__).resolve().parent.parent
snapshot=ROOT/"_local_ops/build-snapshot.json"
assert snapshot.is_file(),"Synthetic SKU E2E requires a locally fetched approved D1 snapshot"
original=snapshot.read_bytes()
data=json.loads(original.decode("utf-8"))
assert data.get("site")=="xuyi-drinkware-site"
model="bottle-qa-demo"
assert all(x.get("model")!=model for x in data.get("products",[]))
record={
 "newProduct":True,"category":"Plastic Sports Water Bottles",
 "name":"XUYI Synthetic Bottle QA Model",
 "material":"PP","capacity":"750ml",
 "description":"Synthetic, locally tested new-bottle record. This product does not exist for sale.",
 "image":"/media/ppt/slide-059.webp","colors":"","packing":"",
 "seoTitle":"Synthetic Test Bottle 750ml | XUYI Bottles",
 "seoDescription":"Synthetic fixture used only to validate the reusable bottle product template."
}
data.setdefault("products",[]).append({"model":model,"content":record})
locale="es"
main='<section class="section"><div class="shell"><h1>Botella de prueba sintética</h1><p>Modelo usado solamente para una prueba local de componentes compartidos y traducciones revisadas. No existe como producto de venta y no debe publicarse.</p></div></section>'
assert len(main)>120
data.setdefault("translations",[]).append({"locale":locale,"resourceId":"page:/products/"+model+"/","content":{
 "title":"Botella sintética de prueba | XUYI","description":"Esta página de prueba local verifica las traducciones de productos nuevos.","mainHtml":main
}})
def build():
 subprocess.run([sys.executable,"scripts/build_release.py"],cwd=ROOT,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
try:
 snapshot.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
 build()
 html=(ROOT/"dist/products"/model/"index.html").read_text(encoding="utf-8")
 assert "Synthetic Test Bottle 750ml | XUYI Bottles" in html
 assert 'href="https://xuyibottles.com/products/'+model+'/"' in html
 assert 'name="robots" content="noindex,nofollow"' in html
 assert '/media/ppt/slide-059.webp' in html
 assert "Submitted Capacity" in html
 assert "XUYI Synthetic Bottle QA Model" in html
 index=(ROOT/"dist/products/index.html").read_text(encoding="utf-8")
 assert 'href="/products/'+model+'/"' in index
 es=(ROOT/"dist/es/products"/model/"index.html").read_text(encoding="utf-8")
 assert "Botella de prueba sintética" in es
 assert '<html lang="es">' in es
 assert 'hreflang="en"' in es and 'hreflang="es"' in es
 for other in ("pt","ru","tr"):
  assert not (ROOT/"dist"/other/"products"/model/"index.html").exists()
 assert "bottle-qa-demo" in (ROOT/"dist/sitemap.xml").read_text(encoding="utf-8")
 print("XUYI_NEW_PRODUCT_END_TO_END_PASSED",model,"English and approved es only; no D1 changes")
finally:
 snapshot.write_bytes(original)
 build()
 assert not (ROOT/"dist/products"/model/"index.html").exists()
 print("XUYI_ORIGINAL_RELEASE_RESTORED")