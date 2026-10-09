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
meta=json.loads((OUT/"build-meta.json").read_text(encoding="utf-8"))
assert meta["pagesProject"]=="xuyi-drinkware-site"
assert meta["siteOrigin"]=="https://xuyibottles.com"
assert meta["templateSet"]=="templates/site" and len(meta["templateSha256"])>=10
assert meta["noindex"] is True
assert meta["fileCount"]<19500

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
    if rel!="admin/index.html" and '<aside class="rail"' not in content:
        broken.append((rel,"missing shared rail"))
    if '<meta name="robots" content="noindex,nofollow">' not in content and rel!="admin/index.html":
        broken.append((rel,"robots unexpectedly indexable"))
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
for route in ["index.html","blog/index.html","admin/index.html",
              "products/2095/index.html","products/5340/index.html",
              "capabilities/custom-molding/index.html","capabilities/custom-packaging/index.html"]:
    if not (OUT/route).is_file():broken.append((route,"missing critical route"))
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