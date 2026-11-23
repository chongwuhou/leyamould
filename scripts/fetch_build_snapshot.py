#!/usr/bin/env python3
"""Read only the reviewed, public LEYA MOULD build inputs from its own D1.

Never serialize Cloudflare credentials. Require a functioning authorized API,
never silently build stale content when the authenticated fetch fails.
"""
import json
import os
from pathlib import Path
import urllib.request
import urllib.error
import time

ROOT=Path(__file__).resolve().parent.parent
OUTPUT=ROOT/"_local_ops"/"build-snapshot.json"
def main():
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    if not token:raise SystemExit("LEYA build token unavailable")
    request=urllib.request.Request(
        "https://leyamould.com/api/build-snapshot",
        headers={"Authorization":"Bearer "+token,"Cache-Control":"no-store",
                 "User-Agent":"LEYA-CI-Build/1.0"})
    # Transient Cloudflare D1/Pages 429/5xx can occur while publishing.
    # Retry the same authenticated read, with bounded backoff. Never use a
    # prior local snapshot as a fallback or retry authorization failures.
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request,timeout=35) as response:
                payload=json.load(response)
            break
        except urllib.error.HTTPError as err:
            if err.code not in (429,500,502,503,504) or attempt==4:
                raise
            pause=(5,10,15,20)[attempt]
            print("LEYA_SNAPSHOT_TRANSIENT_RETRY",attempt+1,"HTTP",err.code,flush=True)
            time.sleep(pause)
        except (TimeoutError,urllib.error.URLError):
            if attempt==4:raise
            pause=(5,10,15,20)[attempt]
            print("LEYA_SNAPSHOT_NETWORK_RETRY",attempt+1,flush=True)
            time.sleep(pause)
    # First rollout may read the old live Function revision before the new
    # build-snapshot endpoint is deployed. The follow-up build consumes D1 blogPosts.
    payload.setdefault("blogPosts",[])
    if payload.get("site")!="leyamould" or payload.get("schemaVersion")!=1:
        raise RuntimeError("Build snapshot did not identify LEYA MOULD")
    if (not isinstance(payload.get("pages"),list)
            or not isinstance(payload.get("products"),list)
            or not isinstance(payload.get("blogPosts"),list)):
        raise RuntimeError("Build snapshot schema missing required pages/products/blogPosts")
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    print("LEYA_BUILD_INPUT_READY",
          "revision",payload.get("publishRevision"),
          "pages",len(payload["pages"]),
          "products",len(payload["products"]),
          "blogPosts",len(payload["blogPosts"]),
          "translations",len(payload.get("translations",[])))
if __name__=="__main__":main()

