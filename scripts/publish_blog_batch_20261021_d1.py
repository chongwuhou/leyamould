#!/usr/bin/env python3
"""Publish only the reviewed 2026-10-21 XUYI B2B batch via dedicated authenticated D1 endpoint."""
import json,os,sys,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
FILE=ROOT/"_local_ops/blog-batch-20261021/payload.json"
URL="https://xuyibottles.com/api/admin/blog-batch-20261021"
EXPECTED={"compare-oem-water-bottle-quotes-like-for-like",
          "wholesale-water-bottle-carton-label-3pl-retail-checklist",
          "custom-water-bottle-reorder-planning-lead-time-buffer"}
def main():
    p=json.loads(FILE.read_text("utf8"))
    assert {r["slug"] for r in p["posts"]}==EXPECTED
    assert len(p["translations"])==12 and len(p["indexCards"])==12
    if "--dry-run" in sys.argv:
        print("DRY_RUN_REVIEWED_B2B_20261021",sorted(EXPECTED));return
    if (os.environ.get("GITHUB_ACTIONS")!="true"
        or os.environ.get("GITHUB_EVENT_NAME")!="push"
        or os.environ.get("GITHUB_REF")!="refs/heads/main"
        or os.environ.get("GITHUB_REPOSITORY")!="chongwuhou/xuyi-drinkware-site"
        or os.environ.get("CLOUDFLARE_ACCOUNT_ID")!="a4032d0251103d6ef680b2aaddce1afc"):
        raise SystemExit("Publication is permitted only from the approved XUYI GitHub main workflow.")
    token=os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:raise SystemExit("Cloudflare deployment token is missing")
    body=json.dumps(p,ensure_ascii=False,separators=(",",":")).encode("utf8")
    req=urllib.request.Request(URL,data=body,method="POST",headers={
        "Authorization":"Bearer "+token,"Content-Type":"application/json",
        "Accept":"application/json","User-Agent":"XUYI-Reviewed-Blog-Publisher-20261021/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=90) as reply:response=json.load(reply)
    except urllib.error.HTTPError as err:
        try:message=json.loads(err.read(1000))["error"]
        except Exception:message="Unknown CMS response"
        raise RuntimeError("CMS refused publication: HTTP "+str(err.code)+" "+str(message)[:250]) from None
    if not response.get("success") or set(response.get("publishedSlugs",[]))!=EXPECTED:
        raise RuntimeError("D1 publication not fully confirmed")
    print("XUYI_20261021_D1_BATCH_CONFIRMED",
        "POSTS_INSERTED",response["postsInserted"],
        "TRANSLATIONS_INSERTED",response["translationsInserted"],
        "INDEX_CARDS_ADDED",response["indexCardsAdded"],
        "PUBLISH_REVISION",response["publishRevision"])
if __name__=="__main__":main()
