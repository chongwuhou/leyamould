#!/usr/bin/env python3
"""One-time reviewed 505 product×locale SEO migration to canonical Cloudflare D1.

The deployment uses a preapproved server-side allowlist; CI cannot submit
arbitrary text, and every old CMS row is compared before mutation.
"""
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import json
import os

SITE="https://xuyibottles.com/api/admin/product-seo-promotion-20261020"

def call(token,body=None):
    req=Request(SITE,data=json.dumps(body,separators=(",",":")).encode("utf8") if body else None,
        method="POST" if body else "GET",
        headers={"Authorization":"Bearer "+token,"Content-Type":"application/json",
                 "Accept":"application/json","User-Agent":"XUYI-Reviewed-Product-SEO-Promotion/1.0"})
    try:
        with urlopen(req,timeout=65) as result:return json.load(result)
    except HTTPError as err:
        raise RuntimeError("D1 promotion failed with HTTP "+str(err.code)+" "+err.read(500).decode("utf8","replace")) from None

def main():
    if os.environ.get("GITHUB_ACTIONS")!="true" or \
       os.environ.get("GITHUB_REPOSITORY")!="chongwuhou/xuyi-drinkware-site" or \
       os.environ.get("GITHUB_REF")!="refs/heads/main":
        raise RuntimeError("Only approved XUYI GitHub main may run this one-time D1 promotion")
    token=os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:raise RuntimeError("Missing credential")
    initial=call(token)
    total=initial["reviewed"]
    if total!=505:raise RuntimeError("Incorrect reviewed source plan")
    if initial["persisted"]==total:
        print("PRODUCT_SEO_ALREADY_PERSISTED",total,"NO_DUPLICATE_WRITE")
    else:
        for index in range(initial["batchCount"]):
            result=call(token,{"action":"batch","batchIndex":index})
            if result["persisted"]!=result["rows"]:
                raise RuntimeError("Batch "+str(index)+" contains an unresolved D1 edit; do not override it")
            if index%8==0 or index+1==initial["batchCount"]:
                print("PROMOTED_REVIEWED_BATCH",index+1,"OF",initial["batchCount"],
                      "RECORDS",result["rows"],"EXISTING_EDITS_PRESERVED",result["ownerEditsPreserved"])
    state=call(token)
    if state["persisted"]!=total or state["missing"]:
        raise RuntimeError("Final D1 review missing some approved product/locale titles")
    final=call(token,{"action":"finalize"})
    if not final.get("complete"):raise RuntimeError("Failed to queue SEO D1 revision")
    print("XUYI_PRODUCT_SEO_505_D1_AUTHORITY_READY",
          "ROWS",state["persisted"],"PUBLISH_REVISION",final["revision"])

if __name__=="__main__":main()
