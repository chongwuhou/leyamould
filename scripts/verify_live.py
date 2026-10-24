#!/usr/bin/env python3
"""Live smoke test for the XUYI custom domain, not a fake availability claim."""
import json
import urllib.request
import urllib.error
from time import time_ns

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
 "/api/admin/pages":401,
 "/api/admin/brand-config":401,
 "/api/admin/site-config":401,
 "/api/admin/product-content":401,
 "/api/admin/page-content":401,
 "/api/admin/page-translations":401,
 "/api/build-snapshot":401,
 "/api/publish-state":401,
 # Check BOTH original URLs and cache-busted URLs: the original URLs once
 # leaked source content under an old Cloudflare deployment and can remain cached.
 # Pages' explicit source-file tombstones intentionally return 410 Gone.
 # A missing legacy path (404) is equally safe; 200 must still fail.
 "/build.py":(404,410),
 "/site_renderer.py":(404,410),
 "/data/products.json":(404,410),
 "/build.py?xuyi_source_exposure_probe=1":(404,410),
 "/site_renderer.py?xuyi_source_exposure_probe=1":(404,410),
 "/data/products.json?xuyi_source_exposure_probe=1":(404,410),
}
failed=[]
for path,expected in cases.items():
 try:
  req=urllib.request.Request(BASE+path+("?blog_header_ci="+str(time_ns()) if path=="/blog/" else ""),headers={"User-Agent":"XUYI-site-preflight/1.0","Cache-Control":"no-cache"})
  with urllib.request.urlopen(req,timeout=20) as resp:
   status=resp.status
   if path=="/blog/" and status==200:
    markup=resp.read().decode("utf-8","replace")
    if 'Sourcing Knowledge Center' in markup or markup.count('<h1')!=1:
     failed.append((path,"duplicate legacy Blog heading on live site"))
   if path=="/build-meta.json":
    meta=json.load(resp)
    if meta.get("pagesProject")!="xuyi-drinkware-site" or meta.get("templateSet")!="templates/site":
     failed.append((path,"wrong release identity"))
 except urllib.error.HTTPError as exc:status=exc.code
 except Exception as exc:
  failed.append((path,type(exc).__name__))
  continue
 print(path,status)
 if status not in (expected if isinstance(expected,tuple) else (expected,)):
  failed.append((path,status,expected,"Purge stale Cloudflare CDN cache for this exact URL" if path in ("/build.py","/site_renderer.py","/data/products.json") and status==200 else "status mismatch"))
if failed:raise SystemExit("XUYI LIVE AUDIT FAILED: "+repr(failed))
print("XUYI LIVE AUDIT PASSED",len(cases),"URLs")