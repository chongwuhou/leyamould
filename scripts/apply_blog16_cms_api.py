#!/usr/bin/env python3
"""Write real 16 English article bodies through XUYI authenticated D1 CMS API."""
import json
import os
import urllib.request
import urllib.error
from publish_existing_blog_interlinks_d1 import POSTS,curate

ORIGIN="https://xuyibottles.com"
def call(path,token,payload=None):
    req=urllib.request.Request(
        ORIGIN+path,
        data=json.dumps(payload,ensure_ascii=False).encode("utf8") if payload is not None else None,
        headers={"Authorization":"Bearer "+token,"Content-Type":"application/json",
                 "Cache-Control":"no-store","User-Agent":"XUYI-editor-reviewed-CMS/1"},
        method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(req,timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError("XUYI protected CMS endpoint rejected request HTTP "+str(exc.code)) from exc
def main():
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    if not token:raise RuntimeError("XUYI CMS secret unavailable")
    state=call("/api/build-snapshot",token)
    if state.get("site")!="xuyi-drinkware-site" or state.get("schemaVersion")!=1:
        raise RuntimeError("Wrong D1 build snapshot")
    rows={x["route"]:x["mainHtml"] for x in state["pageBodies"]}
    batch=[]
    for slug in POSTS:
        route="/blog/"+slug+"/"
        if route not in rows:raise RuntimeError("Missing published English CMS body "+slug)
        original=rows[route]
        updated=curate(original,slug)
        batch.append({"slug":slug,"original":original,"updated":updated})
    if len(batch)!=16:raise RuntimeError("Unexpected reviewed article count")
    result=call("/api/admin/english-blog-editorial",token,{"action":"publish-reviewed-16-english-cms","articles":batch})
    if not (result.get("saved") is True or result.get("alreadyApplied") is True):
        raise RuntimeError("CMS did not confirm English blog editorial changes")
    print("XUYI_CMS_ENGLISH_16_ARTICLE_BODIES_SAVED",result.get("updated",0),
          "already_applied",bool(result.get("alreadyApplied")))
if __name__=="__main__":
    main()