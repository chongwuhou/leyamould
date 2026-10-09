#!/usr/bin/env python3
"""Live smoke test for the XUYI custom domain, not a fake availability claim."""
import json
import urllib.request
import urllib.error

BASE="https://xuyibottles.com"
cases={
 "/":200,
 "/blog/":200,
 "/capabilities/custom-molding/":200,
 "/products/2095/":200,
 "/admin/":200,
 "/assets/site.css":200,
 "/build-meta.json":200,
 "/api/admin/publish":401,
 "/api/admin/blog":401,
 "/api/publish-state":401,
 "/build.py?xuyi_source_exposure_probe=1":404,
 "/site_renderer.py?xuyi_source_exposure_probe=1":404,
 "/data/products.json?xuyi_source_exposure_probe=1":404,
}
failed=[]
for path,expected in cases.items():
 try:
  req=urllib.request.Request(BASE+path,headers={"User-Agent":"XUYI-site-preflight/1.0","Cache-Control":"no-cache"})
  with urllib.request.urlopen(req,timeout=20) as resp:
   status=resp.status
   if path=="/build-meta.json":
    meta=json.load(resp)
    if meta.get("pagesProject")!="xuyi-drinkware-site" or meta.get("templateSet")!="templates/site":
     failed.append((path,"wrong release identity"))
 except urllib.error.HTTPError as exc:status=exc.code
 except Exception as exc:
  failed.append((path,type(exc).__name__))
  continue
 print(path,status)
 if status!=expected:failed.append((path,status,expected))
if failed:raise SystemExit("XUYI LIVE AUDIT FAILED: "+repr(failed))
print("XUYI LIVE AUDIT PASSED",len(cases),"URLs")