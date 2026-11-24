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
assert meta["pagesProject"]=="leyamould"
assert meta["siteOrigin"]=="https://leyamould.com"
assert meta["templateSet"]=="templates/site" and len(meta["templateSha256"])>=10
CONFIG=json.loads((ROOT/"deployment/site.config.json").read_text(encoding="utf-8"))
INDEXABLE=CONFIG["site"].get("indexingApproved") is True
assert meta["noindex"] is (not INDEXABLE), "Release indexing flag does not match approved configuration"
assert meta["fileCount"]<19500
assert set(meta.get("contentSources",{}))=={"brand","navigation","pageSeo","products","pageBodies","pageCopy","blogPosts","commonCopy","modelReferences","locales"}, "D1/source origin metadata is incomplete"
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
        dynamic_blog_route = bool(re.fullmatch(r"/blog/[a-z0-9-]+/", urlsplit(url).path)) and (ROOT/"functions/blog/[[path]].js").is_file()
        if target and not (OUT/target).is_file() and not (OUT/target/"index.html").is_file() and not dynamic_blog_route:
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
    expected="https://leyamould.com/"+rel[:-len("index.html")]
    if not canon or canon.group(1)!=expected:broken.append((rel,"product canonical mismatch"))
for route in ["index.html","blog/index.html",ADMIN_PATH+"/index.html",
              "products/2095/index.html","products/5340/index.html",
              "capabilities/custom-molding/index.html","capabilities/custom-packaging/index.html",
              "collections/spray-water-bottles/index.html","collections/two-way-drinking-cups/index.html",
              "collections/titanium-vacuum-cups/index.html"]:
    if not (OUT/route).is_file():broken.append((route,"missing critical route"))
FACTORY_SOURCE_DOCUMENTS = {"puyunsm(1).pdf", "水杯最新产品.pptx"}
factory_catalog_pages=[]
for page in pages:
    rel=page.relative_to(OUT).as_posix()
    if not (rel.startswith("products/") and rel.endswith("/index.html")):
        continue
    content=page.read_text(encoding="utf-8")
    if any(source in content for source in FACTORY_SOURCE_DOCUMENTS):
        factory_catalog_pages.append((rel,content))
snapshot_path=ROOT/"_local_ops"/"build-snapshot.json"
expected_factory_models=set()
if snapshot_path.is_file():
    snapshot=json.loads(snapshot_path.read_text(encoding="utf-8"))
    expected_factory_models={str(row.get("model","")).lower() for row in snapshot.get("products",[])
        if isinstance(row,dict) and isinstance(row.get("content"),dict)
        and row["content"].get("newProduct") is True
        and row["content"].get("sourceDocument") in FACTORY_SOURCE_DOCUMENTS}
actual_factory_models={rel.split("/")[1].lower() for rel,_ in factory_catalog_pages}
if actual_factory_models!=expected_factory_models:
    broken.append(("factory catalog","published D1 source products differ from generated product pages",
        {"missing":sorted(expected_factory_models-actual_factory_models),"extra":sorted(actual_factory_models-expected_factory_models)}))
blog_snapshot=json.loads(snapshot_path.read_text(encoding="utf-8")) if snapshot_path.is_file() else {}
published_blog={row.get("slug") for row in blog_snapshot.get("blogPosts",[])
                if isinstance(row,dict) and row.get("status")=="published"
                and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",str(row.get("slug","")))}
blog_order=[str(row.get("slug")) for row in blog_snapshot.get("blogPosts",[])
            if isinstance(row,dict) and row.get("status")=="published"
            and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",str(row.get("slug","")))]
language_config=blog_snapshot.get("languages") if isinstance(blog_snapshot.get("languages"),dict) else {}
source_locale=str(language_config.get("sourceLocale") or "en")
manifest_path=OUT/"locale-manifest.json"
locale_manifest=json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
publishable_locales=[str(row.get("code")) for row in locale_manifest.get("locales",[])
                     if isinstance(row,dict) and str(row.get("code"))!=source_locale
                     and row.get("enabled") is not False and row.get("publishReady") is not False]
if not publishable_locales:
    publishable_locales=[str(row.get("code")) for row in language_config.get("languages",[])
                         if isinstance(row,dict) and str(row.get("code"))!=source_locale
                         and row.get("enabled") is not False and row.get("publishReady") is not False]
def localized_blog_order(content,locale):
    cards=re.findall(r'<article class="news-card">[\s\S]*?</article>',content,re.I)
    order=[]
    for card in cards:
        links=re.findall(r'href="/(?:[a-z0-9_-]+/)?blog/([a-z0-9]+(?:-[a-z0-9]+)*)/"',card,re.I)
        if len(links)!=3 or len(set(links))!=1:
            broken.append((locale,"invalid localized Blog card",links[:3]))
            return []
        order.append(links[0])
    return order
if not blog_order or len(blog_order)!=len(set(blog_order)):
    broken.append(("blog CMS","D1 published Blog order is missing or duplicated",len(blog_order)))
else:
    english_index=OUT/"blog"/"index.html"
    if not english_index.is_file():
        broken.append(("blog CMS","English Blog index missing",str(english_index.relative_to(OUT))))
    else:
        english_actual=localized_blog_order(english_index.read_text(encoding="utf-8"),"en")
        if english_actual!=blog_order:
            first=next((i for i,(expected,got) in enumerate(zip(blog_order,english_actual),1) if expected!=got),None)
            broken.append(("en","English Blog index order/count differs from D1 snapshot",first))
if not blog_order or len(blog_order)!=len(set(blog_order)):
    pass
elif not publishable_locales:
    broken.append(("blog CMS","No publish-ready localized Blog output found",None))
else:
    for locale in publishable_locales:
        localized_index=OUT/locale/"blog"/"index.html"
        if not localized_index.is_file():
            broken.append(("blog CMS","localized Blog index missing",str(localized_index.relative_to(OUT))))
            continue
        actual=localized_blog_order(localized_index.read_text(encoding="utf-8"),locale)
        if actual and actual!=blog_order:
            first=next((i for i,(expected,got) in enumerate(zip(blog_order,actual),1) if expected!=got),None)
            broken.append((locale,"localized Blog index order differs from D1 snapshot",first))
for slug in published_blog:
    if not (OUT/"blog"/slug/"index.html").is_file():
        broken.append(("blog CMS","published D1 article shell missing","/blog/"+slug+"/"))
for row in blog_snapshot.get("translations",[]):
    rid=row.get("resourceId","")
    loc=row.get("locale")
    match=re.fullmatch(r"page:(/blog/[a-z0-9-]+/)",rid) if isinstance(rid,str) else None
    if not match or loc not in {"es","pt","ru","tr"} or match.group(1)=="/blog/":
        continue
    slug=match.group(1).strip("/").split("/")[-1]
    if slug in published_blog and not (OUT/loc/"blog"/slug/"index.html").is_file():
        broken.append(("blog CMS","published translated article page missing",loc+match.group(1)))
for rel,content in factory_catalog_pages:
    for marker in ("Factory Catalog Source","Factory Catalog Page","Factory Catalog Capacity"):
        if marker not in content:broken.append((rel,"missing factory source/spec marker",marker))
admin_import=(ROOT/"assets/admin-content.js").read_text(encoding="utf-8")
product_api=(ROOT/"functions/api/admin/product-content.js").read_text(encoding="utf-8")
if 'action==="new-product-bulk"' not in admin_import:broken.append(("admin CMS","missing factory bulk import action"))
if ("createOnly:!selectedExisting" not in admin_import or "createOnly:true" not in admin_import
        or "if(p.createOnly===true)" not in product_api
        or "ON CONFLICT(model) DO NOTHING" not in product_api or "saved?.meta?.changes" not in product_api):
    broken.append(("admin CMS","create-only API protection missing"))
if 'crypto.subtle.digest("SHA-256"' not in admin_import or "imageSha256" not in admin_import:
    broken.append(("admin CMS","R2 source-image integrity check missing"))
if "imagePath=media.path" not in admin_import:
    broken.append(("admin CMS","uploaded R2 path is not persisted into the new product record"))
if "sourceSha256:manifest.sourceSha256" not in admin_import or "sourceImageSha256:row.imageSha256" not in admin_import:
    broken.append(("admin CMS","factory PDF/image provenance is not preserved"))
if "pending_manual_review" not in admin_import:
    broken.append(("admin CMS","replacement image review gate is missing"))
nav=json.loads((ROOT/"data/site-navigation-defaults.json").read_text(encoding="utf-8"))
nav_text=json.dumps(nav,ensure_ascii=False)
for slug in ("spray-water-bottles","two-way-drinking-cups","titanium-vacuum-cups"):
    if slug not in nav_text:broken.append(("navigation","missing new drinkware category",slug))
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


