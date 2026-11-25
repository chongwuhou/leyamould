#!/usr/bin/env python3
"""Read only the reviewed, public LEYA MOULD build inputs from its own D1.

Never serialize Cloudflare credentials. Require a functioning authorized API,
never silently build stale content when the authenticated fetch fails.
"""
import json
import os
import subprocess
from pathlib import Path
import urllib.request
import urllib.error
import time

ROOT=Path(__file__).resolve().parent.parent
OUTPUT=ROOT/"_local_ops"/"build-snapshot.json"

def read_d1_translations():
    """Read page translations directly from D1 when an older live Function
    returns a filtered snapshot. This is an authenticated read-only query;
    it never seeds, migrates, or writes the database.
    """
    account_id=os.environ.get("CLOUDFLARE_ACCOUNT_ID","")
    if not account_id:
        raise SystemExit("LEYA Cloudflare account unavailable")
    command=("SELECT resource_id,locale,translated_json "
             "FROM xuyi_translation_overrides "
             "WHERE resource_id LIKE 'page:%' "
             "ORDER BY locale,resource_id")
    result=subprocess.run(
        ["npx","--yes","wrangler@4.148.0","d1","execute","leyamould-d1",
         "--remote","--command",command,"--json"],
        check=True,capture_output=True,text=True,
        env={**os.environ,"CLOUDFLARE_ACCOUNT_ID":account_id},
        timeout=120,
    )
    raw=json.loads(result.stdout)
    rows=[]
    for batch in raw if isinstance(raw,list) else [raw]:
        if not isinstance(batch,dict):
            continue
        for row in batch.get("results",[]):
            if not isinstance(row,dict):
                continue
            try:
                content=json.loads(row.get("translated_json") or "{}")
            except (TypeError,json.JSONDecodeError):
                content={}
            rows.append({
                "resourceId":str(row.get("resource_id") or ""),
                "locale":str(row.get("locale") or ""),
                "content":content if isinstance(content,dict) else {},
            })
    if not rows:
        raise RuntimeError("Read-only D1 translation query returned no rows")
    return rows

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
    payload.setdefault("modelReferences",[])
    # The deployed Function may still be the previous revision while this
    # source build is running. Complete only the translation slice from the
    # same D1 database, using a read-only query, so the strict gate never
    # falls back to repository or renderer copy.
    if len(payload.get("translations",[])) < 57:
        payload["translations"]=read_d1_translations()
        print("LEYA_TRANSLATIONS_READ_DIRECT_D1",len(payload["translations"]),flush=True)
    if payload.get("site")!="leyamould" or payload.get("schemaVersion")!=1:
        raise RuntimeError("Build snapshot did not identify LEYA MOULD")
    if (not isinstance(payload.get("pages"),list)
            or not isinstance(payload.get("products"),list)
            or not isinstance(payload.get("blogPosts"),list)
            or not isinstance(payload.get("modelReferences"),list)):
        raise RuntimeError("Build snapshot schema missing required pages/products/blogPosts/modelReferences")
    audit = payload.get("modelReferenceAudit")
    if not isinstance(audit, dict) or not isinstance(audit.get("publishedIssues"), list):
        # The currently deployed Function may predate the audit field.  Do
        # not weaken the gate or use a fallback: derive the same fail-closed
        # audit from the published rows so the first backend rollout reports
        # the real data problem instead of a schema mismatch.
        issues=[]
        for row in payload["modelReferences"]:
            if not isinstance(row,dict):
                issues.append({"slug":"unknown","issues":["row"]})
                continue
            source_url=str(row.get("sourceUrl") or row.get("source_url") or "")
            source_image=str(row.get("sourceImage") or row.get("source_image") or "")
            image=str(row.get("image") or row.get("imagePath") or row.get("image_path") or "")
            row_issues=[]
            if not source_url.lower().startswith("https://"): row_issues.append("source_url")
            if not source_image.lower().startswith("https://"): row_issues.append("source_image")
            if not image.startswith("/media/"): row_issues.append("r2_image")
            if row_issues: issues.append({"slug":str(row.get("slug") or "unknown"),"issues":row_issues})
        audit={"total":len(payload["modelReferences"]),"published":len(payload["modelReferences"]),"draft":0,"publishedIssues":issues}
        payload["modelReferenceAudit"]=audit
    if int(audit.get("total",0) or 0)!=112 or len(payload["modelReferences"])!=112:
        raise RuntimeError("D1 model reference gate requires exactly 112 published models; got total="+str(audit.get("total",0))+" snapshot="+str(len(payload["modelReferences"])))
    if audit["publishedIssues"]:
        categories=sorted({issue for row in audit["publishedIssues"] for issue in (row.get("issues") or [])})
        print("LEYA_MODEL_REFERENCE_GATE_BLOCKED", "total", audit.get("total",0), "published", audit.get("published",0), "issues", len(audit["publishedIssues"]), "categories", ",".join(categories), flush=True)
        raise RuntimeError("Published D1 model references failed the review gate")
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    print("LEYA_BUILD_INPUT_READY",
          "revision",payload.get("publishRevision"),
          "pages",len(payload["pages"]),
          "products",len(payload["products"]),
          "blogPosts",len(payload["blogPosts"]),
          "modelReferences",len(payload["modelReferences"]),
          "modelDrafts",int(audit.get("draft",0) or 0),
          "translations",len(payload.get("translations",[])))
if __name__=="__main__":main()

