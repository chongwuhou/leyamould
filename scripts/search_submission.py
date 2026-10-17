#!/usr/bin/env python3
"""XUYI prelaunch-safe IndexNow publication and search engine URL preparation.

No external submission is allowed when either the source launch gate or the
LIVE website is blocked. Supports Bing/Yandex/other IndexNow participants.
Google requires Search Console; Baidu requires its own verified account/API.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
ORIGIN="https://xuyibottles.com"
HOST="xuyibottles.com"
CONFIG=ROOT/"deployment/site.config.json"
INDEXNOW="https://api.indexnow.org/indexnow"
KEY_RE=re.compile(r"^[A-Za-z0-9-]{8,128}$")
NS="{http://www.sitemaps.org/schemas/sitemap/0.9}"

def approved():
    data=json.loads(CONFIG.read_text(encoding="utf-8"))
    if data["site"]["origin"]!=ORIGIN or data["cloudflare"]["pagesProjectName"]!="xuyi-drinkware-site":
        raise ValueError("Refusing search submission for another project")
    return data["site"]["indexingApproved"] is True

def sitemap_urls(xml):
    root=ET.fromstring(xml)
    if root.tag!=NS+"urlset":raise ValueError("Only actual canonical URL lists may be submitted")
    urls=[]
    for element in root.findall(NS+"url"):
        url=element.findtext(NS+"loc")
        parsed=urllib.parse.urlsplit(url or "")
        if parsed.scheme!="https" or parsed.netloc!=HOST or parsed.query or parsed.fragment:
            raise ValueError("Unapproved sitemap URL: "+str(url))
        if not parsed.path.startswith("/") or "/admin/" in parsed.path or "/api/" in parsed.path:
            raise ValueError("Private/invalid sitemap URL: "+str(url))
        urls.append(url)
    if not urls or len(urls)!=len(set(urls)):raise ValueError("Empty/duplicate sitemap")
    return urls

def create_manifest():
    """Build a hash for each actual released page, not a fake publication date."""
    urls=sitemap_urls((DIST/"sitemap.xml").read_bytes())
    hashes={}
    revision=json.loads((DIST/"build-meta.json").read_text(encoding="utf-8")).get("publishRevision")
    overflow={}
    storage=ROOT/"_local_ops"/"model-overflow"
    storage_manifest=storage/"manifest.json"
    if storage_manifest.is_file():
        bundles=json.loads(storage_manifest.read_text(encoding="utf-8"))
        if bundles.get("site")!="xuyi-drinkware-site":
            raise ValueError("Foreign R2 sitemap bundle")
        for row in bundles.get("objects",[]):
            data=json.loads((storage/row["key"]).read_text(encoding="utf-8"))
            if data.get("site")!="xuyi-drinkware-site":
                raise ValueError("Foreign R2 route bundle")
            overflow.update(data.get("routes",{}))
    for url in urls:
        route=url[len(ORIGIN):]
        page=DIST/route.lstrip("/")/"index.html"
        if route=="/":page=DIST/"index.html"
        if page.is_file():
            html=page.read_bytes()
        elif route in overflow:
            html=overflow[route].encode("utf-8")
        else:raise ValueError("Published sitemap URL is missing from Pages/R2: "+route)
        # D1 Blog's actual HTML is rendered by Functions; update its hash when
        # content is republished, not only when static fallback changes.
        extra=(":rev:"+str(revision)).encode() if route.startswith("/blog/") else b""
        hashes[url]=sha256(html+extra).hexdigest()
    if len(hashes)!=len(urls):
        raise ValueError("Missing IndexNow page hashes")
    manifest={"site":"xuyi-drinkware-site","origin":ORIGIN,"schemaVersion":1,
              "urls":hashes}
    (DIST/"search-submission-manifest.json").write_text(
        json.dumps(manifest,ensure_ascii=False,separators=(",",":"),sort_keys=True)+"\n",
        encoding="utf-8")
    return manifest

def key_file():
    """Root key is valid only for an explicitly approved public release."""
    key=os.environ.get("XUYI_INDEXNOW_KEY","").strip()
    if not approved() or not key:return None
    if not KEY_RE.fullmatch(key):raise ValueError("Invalid XUYI_INDEXNOW_KEY format")
    (DIST/(key+".txt")).write_text(key,encoding="utf-8")
    return key

def new_or_changed(old,current,*,first_launch=False):
    urls=current.get("urls",{})
    if first_launch:return sorted(urls)
    if not isinstance(old,dict) or old.get("site")!="xuyi-drinkware-site":
        raise ValueError("Missing previous verified manifest: refusing repeat bulk submission")
    old_urls=old.get("urls",{})
    return sorted(url for url,digest in urls.items() if old_urls.get(url)!=digest)

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"XUYI-Search-Submission/1.0",
                                           "Cache-Control":"no-cache"})
    with urllib.request.urlopen(req,timeout=25) as res:
        return res.read()

def verify_live():
    robots=fetch(ORIGIN+"/robots.txt?search_submit_verify=1").decode("utf-8","replace")
    if re.search(r"(?im)^Disallow:\s*/\s*$",robots):
        raise ValueError("Live robots.txt still blocks all crawlers")
    if "Sitemap: "+ORIGIN+"/sitemap.xml" not in robots:
        raise ValueError("Live robots.txt lacks production sitemap")
    head=fetch(ORIGIN+"/?search_submit_verify=1").decode("utf-8","replace").split("</head>",1)[0]
    if 'content="noindex' in head or 'content="index,follow"' not in head:
        raise ValueError("Live homepage is still noindex")
    meta=json.loads(fetch(ORIGIN+"/build-meta.json?search_submit_verify=1"))
    if meta.get("noindex") is not False or meta.get("pagesProject")!="xuyi-drinkware-site":
        raise ValueError("Live deployment has not approved indexing")
    return meta

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--build",action="store_true",help="make submission manifest and optional key file; no HTTP calls")
    parser.add_argument("--submit",action="store_true",help="notify IndexNow after verifying LIVE launch and key")
    parser.add_argument("--previous",default="_local_ops/previous-search-submission-manifest.json")
    parser.add_argument("--previous-robots",default="_local_ops/previous-robots.txt")
    args=parser.parse_args()
    if args.build:
        manifest=create_manifest()
        key=key_file()
        print("XUYI_SEARCH_MANIFEST_BUILT",len(manifest["urls"]),
              "indexingApproved",approved(),"indexNowKeyPublished",bool(key))
        return
    if not args.submit:
        print("XUYI_SUBMISSION_DRY_RUN_ONLY; use --build or --submit")
        return
    if not approved():
        print("XUYI_SUBMISSION_BLOCKED_BY_NOINDEX_GATE")
        return
    key=os.environ.get("XUYI_INDEXNOW_KEY","").strip()
    if not KEY_RE.fullmatch(key):
        print("XUYI_INDEXNOW_NOT_CONFIGURED: set the project-specific GitHub secret")
        return
    # Important: DO NOT send requests before verifying LIVE robots/meta,
    # root key ownership and an actual successful Cloudflare deployment.
    deployed=verify_live()
    secret_file=ORIGIN+"/"+key+".txt"
    if fetch(secret_file).decode("utf-8").strip()!=key:
        raise ValueError("IndexNow key not yet deployed on the production hostname")
    current=json.loads((DIST/"search-submission-manifest.json").read_text(encoding="utf-8"))
    old_file=ROOT/args.previous
    old=json.loads(old_file.read_text(encoding="utf-8")) if old_file.is_file() else None
    prev_robots=ROOT/args.previous_robots
    previous_crawl_blocked=(not prev_robots.is_file() or
        re.search(r"(?im)^Disallow:\s*/\s*$",prev_robots.read_text(encoding="utf-8")) is not None)
    # Never re-ping the entire website just because an older manifest
    # is absent. Only a verified prior manifest permits incremental submits.
    if old is None:
        print("XUYI_INDEXNOW_NO_VERIFIED_PREVIOUS_MANIFEST: skip bulk ping")
        return
    urls=new_or_changed(old,current,first_launch=False)
    # If the D1 build changed after this release, never submit stale snapshots.
    built=json.loads((DIST/"build-meta.json").read_text(encoding="utf-8"))
    if deployed.get("sourceRevision")!=built.get("sourceRevision"):
        raise ValueError("Remote deployment source revision mismatch")
    if not urls:
        print("XUYI_INDEXNOW_NO_NEW_OR_CHANGED_URLS")
        return
    if len(urls)>10000:raise ValueError("IndexNow batch exceeds protocol limit")
    payload={"host":HOST,"key":key,"keyLocation":secret_file,"urlList":urls}
    req=urllib.request.Request(INDEXNOW,data=json.dumps(payload).encode("utf-8"),
                               headers={"Content-Type":"application/json; charset=utf-8"},
                               method="POST")
    with urllib.request.urlopen(req,timeout=35) as response:
        status=response.status
    if status not in (200,202):raise RuntimeError("IndexNow failed with status "+str(status))
    print("XUYI_INDEXNOW_ACCEPTED",len(urls),"HTTP",status,
          "googleAndBaiduNeedSeparateVerifiedSubmission")

if __name__=="__main__":main()
