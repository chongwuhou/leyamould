#!/usr/bin/env python3
"""Protect live URLs, layout, links, identity and SEO flags during template migration."""
from __future__ import annotations
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json
import re
import sys

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/"dist"
from admin_route import admin_path as resolve_admin_path
meta=json.loads((OUT/"build-meta.json").read_text(encoding="utf-8"))
ADMIN_PATH=resolve_admin_path(meta.get("adminPath","admin"))
assert meta["pagesProject"]=="xuyi-drinkware-site"
assert meta["siteOrigin"]=="https://xuyibottles.com"
assert meta["templateSet"]=="templates/site" and len(meta["templateSha256"])>=10
CONFIG=json.loads((ROOT/"deployment/site.config.json").read_text(encoding="utf-8"))
INDEXABLE=CONFIG["site"].get("indexingApproved") is True
assert meta["noindex"] is (not INDEXABLE), "Release indexing flag does not match approved configuration"
assert meta["fileCount"]<19500
assert set(meta.get("contentSources",{}))=={"brand","navigation","pageSeo","products","pageBodies","locales"}, "D1/source origin metadata is incomplete"
assert all(isinstance(v,str) and v for v in meta["contentSources"].values())

class LocalRefs(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.images=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if d.get("id"):self.ids.add(d["id"])
        if tag=="a" and d.get("href"):self.links.append(d["href"])
        if tag in ("script","link","img"):
            src=d.get("src") or d.get("href")
            if src and src.startswith("/"):self.images.append(src)

pages=sorted(OUT.rglob("*.html"))
broken=[]
for page in pages:
    rel=page.relative_to(OUT).as_posix()
    content=page.read_text(encoding="utf-8")
    refs=LocalRefs();refs.feed(content)
    if "<main" not in content or "</html>" not in content:
        broken.append((rel,"missing shell"))
    if rel!=ADMIN_PATH+"/index.html" and '<aside class="rail"' not in content:
        broken.append((rel,"missing shared rail"))
    if rel!=ADMIN_PATH+"/index.html":
        expected='<meta name="robots" content="'+(
            "noindex,follow" if rel=="404.html" and INDEXABLE else
            "index,follow" if INDEXABLE else "noindex,nofollow")+'">'
        if expected not in content:broken.append((rel,"indexing gate mismatch",expected))
    for url in refs.images:
        target=urlsplit(url).path.lstrip("/")
        if target.startswith(("media/","api/")):continue
        if not (OUT/target).is_file() and not (OUT/target/"index.html").is_file():
            broken.append((rel,"broken asset",url))
    for url in refs.links:
        if url.startswith("#"):continue
        if not url.startswith("/"):continue
        target=urlsplit(url).path.lstrip("/")
        if target.startswith(("media/","api/")):continue
        if target and not (OUT/target).is_file() and not (OUT/target/"index.html").is_file():
            broken.append((rel,"broken route",url))
# Demalong V1.4 quality gate: model pages need unique search snippets and
# self-referencing canonical URLs. A duplicated value blocks deployment.
product_titles={}
product_descriptions={}
for page in pages:
    rel=page.relative_to(OUT).as_posix()
    if not (rel.startswith("products/") and rel.endswith("/index.html")):
        continue
    content=page.read_text(encoding="utf-8")
    title=re.search(r"<title>([^<]+)</title>",content,re.I)
    desc=re.search(r'<meta name="description" content="([^"]+)"',content,re.I)
    canon=re.search(r'<link rel="canonical" href="([^"]+)"',content,re.I)
    for label,match,seen in (("title",title,product_titles),("description",desc,product_descriptions)):
        if not match:broken.append((rel,"missing product "+label));continue
        value=match.group(1).strip()
        if value in seen:broken.append((rel,"duplicate product "+label,seen[value]))
        seen[value]=rel
        slug=rel.split("/")[1]
        if slug.isdigit() and value.count(slug)!=1:
            broken.append((rel,"product model repeats in "+label,slug))
    expected="https://xuyibottles.com/"+rel[:-len("index.html")]
    if not canon or canon.group(1)!=expected:broken.append((rel,"product canonical mismatch"))
for route in ["index.html","blog/index.html",ADMIN_PATH+"/index.html",
              "products/2095/index.html","products/5340/index.html",
              "capabilities/custom-molding/index.html","capabilities/custom-packaging/index.html",
              "collections/spray-water-bottles/index.html","collections/two-way-drinking-cups/index.html",
              "collections/titanium-vacuum-cups/index.html"]:
    if not (OUT/route).is_file():broken.append((route,"missing critical route"))
factory_catalog_pages=[]
for page in pages:
    rel=page.relative_to(OUT).as_posix()
    if not (rel.startswith("products/") and rel.endswith("/index.html")):
        continue
    content=page.read_text(encoding="utf-8")
    if "puyunsm(1).pdf" in content:
        factory_catalog_pages.append((rel,content))
if factory_catalog_pages:
    if len(factory_catalog_pages)!=58:
        broken.append(("factory catalog","expected 58 published product pages",len(factory_catalog_pages)))
    for rel,content in factory_catalog_pages:
        for marker in ("Factory Catalog Source","Factory Catalog Page","Factory Catalog Capacity"):
            if marker not in content:broken.append((rel,"missing factory source/spec marker",marker))
if len(pages)<130:broken.append(("release","unexpected page loss",len(pages)))
if any("demalong" in x.read_text(encoding="utf-8").lower() for x in (OUT/"templates").rglob("*") if x.is_file()) if (OUT/"templates").exists() else False:
    broken.append(("release","DML brand leaked"))
for sensitive in ("build.py", "site_renderer.py", "product_content.py", "data/products.json", "_local_ops/build-snapshot.json", ".wrangler/config/default.toml"):
    if (OUT/sensitive).exists():broken.append((sensitive,"sensitive source included in public dist"))
for hidden in ("_local_ops", "functions", "templates", ".wrangler"):
    if (OUT/hidden).exists():broken.append((hidden,"private source tree included in public dist"))

if broken:
    print("SITE_RELEASE_ERRORS",len(broken),broken[:40]);sys.exit(1)
print("SITE_RELEASE_TESTS_PASSED",f"html={len(pages)}",f"assets={meta['fileCount']}",f"broken={len(broken)}")