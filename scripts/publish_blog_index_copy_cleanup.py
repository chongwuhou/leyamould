#!/usr/bin/env python3
"""Run the reviewed multilingual Blog index/copy cleanup through D1."""
import json,os,urllib.error,urllib.request
ORIGIN=os.environ.get("SITE_ORIGIN","https://xuyibottles.com").rstrip("/")
ENDPOINT=ORIGIN+"/api/admin/blog-index-copy-cleanup-20261117"
BATCH_ID="2026-11-17-blog-index-copy-cleanup"
EXPECTED_RECORDS=12
def main():
    if os.environ.get("GITHUB_EVENT_NAME")!="push" or os.environ.get("GITHUB_REF")!="refs/heads/main":
        raise SystemExit("Only the XUYI main push may write this reviewed cleanup.")
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    if not token: raise SystemExit("Missing existing CLOUDFLARE_API_TOKEN GitHub Actions secret")
    req=urllib.request.Request(ENDPOINT,data=json.dumps({"batchId":BATCH_ID}).encode(),method="POST",
        headers={"Authorization":"Bearer "+token,"Accept":"application/json","Content-Type":"application/json",
                 "User-Agent":"XUYI-D1-Blog-Index-Copy-Cleanup/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=90) as response: result=json.load(response)
    except urllib.error.HTTPError as error:
        raise SystemExit("XUYI cleanup HTTP "+str(error.code)+": "+error.read().decode("utf-8","replace")[:500])
    if not isinstance(result,dict) or not result.get("success") or result.get("batchId")!=BATCH_ID:
        raise SystemExit("XUYI D1 cleanup rejected: "+str(result))
    if int(result.get("checkedRecords",0))!=EXPECTED_RECORDS or int(result.get("remainingLegacyFragments",-1))!=0:
        raise SystemExit("XUYI D1 cleanup final check failed: "+str(result))
    print("XUYI_D1_BLOG_INDEX_COPY_CLEANUP_CONFIRMED",
          "CHECKED_RECORDS",result.get("checkedRecords"),
          "UPDATED_RECORDS",result.get("updatedRecords"),
          "PUBLISH_REVISION",result.get("publishRevision"),flush=True)
if __name__=="__main__": main()
