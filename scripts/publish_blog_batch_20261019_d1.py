#!/usr/bin/env python3
"""Publish reviewed 2026-10-19 XUYI Blog sources to Cloudflare D1 from GitHub Actions.
Insert-only articles and translations; guarded index updates; never overwrite CMS edits.
"""
import json, os, sys, urllib.error, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
BATCH=ROOT/"_local_ops/blog-batch-20261019"
ACCOUNT="a4032d0251103d6ef680b2aaddce1afc"
NAME="xuyi-drinkware-d1"
SLUGS=("can-you-put-hot-water-in-plastic-water-bottle","are-plastic-water-bottles-dishwasher-safe","why-does-reusable-water-bottle-smell-bad")
LOCALES=("es","pt","ru","tr")
BASE=f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/d1/database"

def planned():
    records=[]
    for slug in SLUGS:
        for suffix in ("post",*LOCALES):
            name=f"{slug}-{suffix}.sql"
            f=BATCH/name
            if not f.is_file():raise RuntimeError("Missing reviewed data "+name)
            sql=f.read_text("utf8").strip().splitlines()
            expected="INSERT INTO xuyi_blog_posts" if suffix=="post" else "INSERT INTO xuyi_translation_overrides"
            if len(sql)!=1 or not sql[0].startswith(expected) or "ON CONFLICT" not in sql[0]:
                raise RuntimeError("Unsafe D1 insert "+name)
            records.append((name,sql[0]))
    for locale in LOCALES:
        file=BATCH/f"index-{locale}.sql"
        if not file.is_file():raise RuntimeError("Missing localized index SQL")
        sql=file.read_text("utf8").strip().splitlines()
        if len(sql)!=len(SLUGS):raise RuntimeError("Invalid index statement count")
        for i,stmt in enumerate(sql):
            if not stmt.startswith("UPDATE xuyi_translation_overrides SET") or "ON CONFLICT" in stmt or f"resource_id='page:/blog/' AND locale='{locale}'" not in stmt or f"/blog/{SLUGS[i]}/" not in stmt or "instr(" not in stmt:
                raise RuntimeError("Unsafe D1 index update")
            records.append((f"index-{locale}-{i}",stmt))
    return records

def req(method,url,token,payload=None):
    headers={"Authorization":"Bearer "+token,"Accept":"application/json","User-Agent":"XUYI-Reviewed-Blog-Publisher/1.0"}
    data=None
    if payload is not None:
        data=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf8")
        headers["Content-Type"]="application/json"
    try:
        with urllib.request.urlopen(urllib.request.Request(url,data=data,headers=headers,method=method),timeout=55) as r:
            obj=json.load(r)
    except urllib.error.HTTPError as err:
        raise RuntimeError("Cloudflare D1 HTTP status "+str(err.code)+", verify XUYI D1 permission") from None
    if not isinstance(obj,dict) or not obj.get("success"):
        codes=[item.get("code") for item in obj.get("errors",[]) if isinstance(item,dict)] if isinstance(obj,dict) else []
        raise RuntimeError("D1 API reported failure "+str(codes))
    return obj["result"]

def main():
    records=planned()
    print("XUYI_D1_REVIEWED_STATEMENTS",len(records),flush=True)
    if "--dry-run" in sys.argv:
        print("DRY_RUN_NO_WRITE")
        return
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    if not token or os.environ.get("GITHUB_EVENT_NAME")!="push" or os.environ.get("GITHUB_REF")!="refs/heads/main" or os.environ.get("CLOUDFLARE_ACCOUNT_ID")!=ACCOUNT:
        raise SystemExit("Only XUYI GitHub main push can publish D1 records")
    database=req("GET",BASE+"?name="+NAME,token)
    if not isinstance(database,list):raise RuntimeError("Unexpected D1 database list")
    candidates=[row for row in database if row.get("name")==NAME and row.get("uuid")]
    if len(candidates)!=1:raise RuntimeError("Expected exactly one XUYI D1 database")
    endpoint=BASE+"/"+candidates[0]["uuid"]+"/query"
    def query(sql):
        response=req("POST",endpoint,token,{"sql":sql})
        if not isinstance(response,list) or not response or not all(entry.get("success") for entry in response):
            raise RuntimeError("D1 SQL execution failure")
        return response
    query("SELECT slug FROM xuyi_blog_posts WHERE 1=0")
    modified=0
    for name,sql in records:
        result=query(sql)
        changes=sum(int(item.get("meta",{}).get("changes",0)) for item in result)
        modified+=changes
        print("XUYI_D1_RECORD",name,"changes",changes,flush=True)
    quoted=",".join("'"+slug+"'" for slug in SLUGS)
    found=query("SELECT slug,status FROM xuyi_blog_posts WHERE slug IN ("+quoted+")")[0].get("results",[])
    if {row.get("slug") for row in found if row.get("status")=="published"}!=set(SLUGS):
        raise RuntimeError("D1 publication failed final three-post check")
    print("XUYI_D1_BATCH_CONFIRMED",len(SLUGS),"ARTICLES",len(LOCALES),"LANGUAGES","D1_CHANGES",modified)

if __name__=="__main__":main()
