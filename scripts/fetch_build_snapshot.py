#!/usr/bin/env python3
"""Read only the reviewed, public XUYI build inputs from its own D1.

Never serialize Cloudflare credentials. Require a functioning authorized API,
never silently build stale content when the authenticated fetch fails.
"""
import json
import os
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parent.parent
OUTPUT=ROOT/"_local_ops"/"build-snapshot.json"
def main():
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    if not token:raise SystemExit("XUYI build token unavailable")
    request=urllib.request.Request(
        "https://xuyibottles.com/api/build-snapshot",
        headers={"Authorization":"Bearer "+token,"Cache-Control":"no-store",
                 "User-Agent":"XUYI-CI-Build/1.0"})
    with urllib.request.urlopen(request,timeout=35) as response:
        payload=json.load(response)
    if payload.get("site")!="xuyi-drinkware-site" or payload.get("schemaVersion")!=1:
        raise RuntimeError("Build snapshot did not identify XUYI")
    if not isinstance(payload.get("pages"),list) or not isinstance(payload.get("products"),list):
        raise RuntimeError("Build snapshot schema missing")
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    print("XUYI_BUILD_INPUT_READY",
          "revision",payload.get("publishRevision"),
          "pages",len(payload["pages"]),
          "products",len(payload["products"]),
          "translations",len(payload.get("translations",[])))
if __name__=="__main__":main()
