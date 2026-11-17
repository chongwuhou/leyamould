#!/usr/bin/env python3
"""Apply the reviewed phase-two multilingual semantic corrections through D1/CMS."""
import json, os, sys, urllib.error, urllib.request

ORIGIN=os.environ.get("SITE_ORIGIN","https://xuyibottles.com").rstrip("/")
ENDPOINT=ORIGIN+"/api/admin/blog-seo-phase2-corrections"
EXPECTED_RECORDS=6
BATCH_ID="2026-11-17-blog-seo-phase2-translation-semantics-v2"

def request_write(token):
    body=json.dumps({"batchId":BATCH_ID},ensure_ascii=False,separators=(",",":")).encode("utf-8")
    req=urllib.request.Request(ENDPOINT,data=body,method="POST",headers={
        "Authorization":"Bearer "+token,
        "Accept":"application/json",
        "Content-Type":"application/json",
        "User-Agent":"XUYI-D1-Blog-SEO-Phase2-Repair/1.0"
    })
    try:
        with urllib.request.urlopen(req,timeout=90) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail=error.read().decode("utf-8","replace")[:500]
        raise SystemExit("XUYI Blog SEO phase-two repair HTTP "+str(error.code)+": "+detail)

def main():
    if "--dry-run" in sys.argv:
        print("XUYI_BLOG_SEO_PHASE2_REPAIR_PLAN",BATCH_ID,"RECORDS",EXPECTED_RECORDS,"NO_WRITE")
        return
    if os.environ.get("GITHUB_EVENT_NAME")!="push" or os.environ.get("GITHUB_REF")!="refs/heads/main":
        raise SystemExit("Only the XUYI GitHub main push may write this reviewed D1 repair.")
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    if not token:
        raise SystemExit("Missing existing CLOUDFLARE_API_TOKEN GitHub Actions secret")
    result=request_write(token)
    if not isinstance(result,dict) or not result.get("success") or result.get("batchId")!=BATCH_ID:
        raise SystemExit("XUYI D1 Blog SEO phase-two repair rejected: "+str(result))
    if int(result.get("checkedRecords",0))!=EXPECTED_RECORDS or int(result.get("remainingEnglishFragments",-1))!=0:
        raise SystemExit("XUYI D1 Blog SEO phase-two final check failed: "+str(result))
    revision=str(int(result.get("publishRevision",0)))
    output=os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output,"a",encoding="utf-8") as stream:
            stream.write("revision="+revision+"\n")
    print("XUYI_D1_BLOG_SEO_PHASE2_REPAIR_CONFIRMED",
          "CHECKED_RECORDS",result.get("checkedRecords"),
          "UPDATED_RECORDS",result.get("updatedRecords"),
          "CHANGED_OCCURRENCES",result.get("changedOccurrences"),
          "PUBLISH_REVISION",revision,flush=True)

if __name__=="__main__":
    main()
