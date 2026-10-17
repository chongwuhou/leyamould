#!/usr/bin/env python3
import json,tempfile
from pathlib import Path
from plan_model_overflow import plan,RETIRED_SOURCE_PATHS

with tempfile.TemporaryDirectory(prefix="xuyi-overflow-") as folder:
 root=Path(folder)
 def fresh(*,new_locale=False):
  d=root/"dist"
  for f in sorted(d.rglob("*"),reverse=True) if d.exists() else []:
   if f.is_file():f.unlink()
  for i in range(8):
   slug=f"25{i:02d}"
   for name in ("", "es","pt","ru","tr")+ (("fr",) if new_locale else ()):
    f=d/name/"products"/slug/"index.html"
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(f"<html lang='{name or 'en'}'>model {slug}</html>",encoding="utf8")
  for extra in ("index.html","about/index.html","assets/site.js","admin/index.html"):
   f=d/extra;f.parent.mkdir(parents=True,exist_ok=True);f.write_text("SAFE",encoding="utf8")
  return d
 d=fresh()
 stable=plan(d,root/"out1",switch_at=50,target=44,hard_stop=65)
 assert stable["mode"]=="static" and stable["modelCount"]==0
 assert len(list(d.rglob("*/index.html")))>=40
 assert json.loads((d/"_routes.json").read_text())["include"]==[
   "/api/*","/blog/*","/media/*",*RETIRED_SOURCE_PATHS]
 d=fresh()
 changed=plan(d,root/"out2",switch_at=36,target=25,hard_stop=65)
 assert changed["mode"]=="hybrid" and changed["modelCount"]>=3
 assert changed["localizedPageCount"]==changed["modelCount"]*4
 assert (d/"admin/index.html").read_text()=="SAFE"
 assert (d/"index.html").read_text()=="SAFE"
 assert (d/"assets/site.js").read_text()=="SAFE"
 assert "/products/*" in json.loads((d/"_routes.json").read_text())["include"]
 for item in changed["objects"]:
  file=root/"out2"/item["key"]
  bundle=json.loads(file.read_text(encoding="utf8"))
  assert bundle["site"]=="xuyi-drinkware-site"
  assert len(bundle["routes"])==5
  for route in bundle["routes"]:
   assert not (d/route.lstrip("/")/"index.html").exists()
 # A sixth locale is accepted by the storage planner using actual published
 # folders, not a copied four-language enum.
 d=fresh(new_locale=True)
 six=plan(d,root/"out3",switch_at=36,target=25,hard_stop=70)
 assert six["mode"]=="hybrid"
 assert six["localizedPageCount"]==six["modelCount"]*5
 assert "/fr/products/*" in json.loads((d/"_routes.json").read_text())["include"]
 assert any("/fr/products/" in route for route in six["routes"])
 print("XUYI_R2_OVERFLOW_PLANNER_TESTS_PASSED",changed["modelCount"],"models",
       changed["localizedPageCount"],"localized pages")
