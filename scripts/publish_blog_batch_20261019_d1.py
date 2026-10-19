#!/usr/bin/env python3
"""Publish the reviewed XUYI Blog batch through the site's authenticated D1 CMS binding."""
import json, os, sys, urllib.error, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
BATCH=ROOT/"_local_ops/blog-batch-20261019"
ACCOUNT="a4032d0251103d6ef680b2aaddce1afc"
SLUGS=("can-you-put-hot-water-in-plastic-water-bottle","are-plastic-water-bottles-dishwasher-safe","why-does-reusable-water-bottle-smell-bad")
LOCALES=("es","pt","ru","tr")

def planned():
    for slug in SLUGS:
        for suffix in ("post",*LOCALES):
            name=f"{slug}-{suffix}.sql"
            f=BATCH/name
            if not f.is_file():raise RuntimeError("Missing reviewed data "+name)
            sql=f.read_text("utf8").strip().splitlines()
            expected="INSERT INTO xuyi_blog_posts" if suffix=="post" else "INSERT INTO xuyi_translation_overrides"
            if len(sql)!=1 or not sql[0].startswith(expected) or "ON CONFLICT" not in sql[0]:
                raise RuntimeError("Unsafe D1 insert "+name)
    for locale in LOCALES:
        file=BATCH/f"index-{locale}.sql"
        if not file.is_file():raise RuntimeError("Missing localized index SQL")
        sql=file.read_text("utf8").strip().splitlines()
        if len(sql)!=len(SLUGS):raise RuntimeError("Invalid index statement count")
        for i,stmt in enumerate(sql):
            if not stmt.startswith("UPDATE xuyi_translation_overrides SET") or "ON CONFLICT" in stmt or f"resource_id='page:/blog/' AND locale='{locale}'" not in stmt or f"/blog/{SLUGS[i]}/" not in stmt or "instr(" not in stmt:
                raise RuntimeError("Unsafe D1 index update")
    manifest=BATCH/"payload.json"
    if not manifest.is_file():raise RuntimeError("Missing reviewed CMS payload; run prepare_blog_release_20261019.py first")
    payload=json.loads(manifest.read_text(encoding="utf8"))
    if {x.get("slug") for x in payload.get("posts",[])}!=set(SLUGS):
        raise RuntimeError("Reviewed payload article set mismatch")
    if len(payload.get("translations",[]))!=len(SLUGS)*len(LOCALES) or len(payload.get("indexCards",[]))!=len(SLUGS)*len(LOCALES):
        raise RuntimeError("Reviewed payload translation/index counts mismatch")
    return payload

def req(url,token,payload):
    headers={"Authorization":"Bearer "+token,"Accept":"application/json","User-Agent":"XUYI-Reviewed-Blog-Publisher/1.0","Content-Type":"application/json"}
    data=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf8")
    try:
        with urllib.request.urlopen(urllib.request.Request(url,data=data,headers=headers,method="POST"),timeout=90) as response:
            obj=json.load(response)
    except urllib.error.HTTPError as err:
        detail=""
        try:
            body=json.loads(err.read().decode("utf8"))
            message=body.get("error","") if isinstance(body,dict) else ""
            if message:detail=" ("+str(message)[:300]+")"
        except Exception:
            pass
        raise RuntimeError("XUYI reviewed CMS HTTP status "+str(err.code)+detail) from None
    if not isinstance(obj,dict) or not obj.get("success"):
        raise RuntimeError("XUYI reviewed CMS rejected the batch: "+str(obj.get("error","unknown error") if isinstance(obj,dict) else "invalid response"))
    return obj

def main():
    payload=planned()
    print("XUYI_REVIEWED_BATCH",len(payload["posts"]),"ARTICLES",len(payload["translations"]),"TRANSLATIONS",len(payload["indexCards"]),"INDEX_CARDS",flush=True)
    if "--dry-run" in sys.argv:
        print("DRY_RUN_NO_WRITE")
        return
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    if not token:
        raise SystemExit("Missing existing CLOUDFLARE_API_TOKEN GitHub Actions secret")
    if os.environ.get("GITHUB_EVENT_NAME")!="push" or os.environ.get("GITHUB_REF")!="refs/heads/main" or os.environ.get("CLOUDFLARE_ACCOUNT_ID")!=ACCOUNT:
        raise SystemExit("Only XUYI GitHub main push can publish reviewed D1 records")
    origin=os.environ.get("SITE_ORIGIN","https://xuyibottles.com").rstrip("/")
    result=req(origin+"/api/admin/blog-batch",token,payload)
    print("XUYI_D1_BATCH_CONFIRMED",len(result["publishedSlugs"]),"ARTICLES",
          len(LOCALES),"LANGUAGES","POSTS_INSERTED",result["postsInserted"],
          "TRANSLATIONS_INSERTED",result["translationsInserted"],
          "INDEX_CARDS_ADDED",result["indexCardsAdded"],
          "PUBLISH_REVISION",result["publishRevision"],flush=True)

if __name__=="__main__":main()
