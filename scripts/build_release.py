#!/usr/bin/env python3
"""XUYI Pages release builder, adapted from Demalong's build/deploy separation.

Run at repository root. No remote resources are written by this script.
The build writes only to dist/, never edits the tracked site HTML snapshots.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from admin_route import admin_path as resolve_admin_path

ROOT=Path(__file__).resolve().parent.parent
CONFIG=json.loads((ROOT/"deployment/site.config.json").read_text(encoding="utf-8"))
DIST=ROOT/"dist"

def fail(message):
    raise SystemExit(message)

def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if CONFIG["cloudflare"]["pagesProjectName"]!="xuyi-drinkware-site":
        fail("Refusing to target another Pages project")
    if CONFIG["cloudflare"]["d1Database"]!="xuyi-drinkware-d1":
        fail("Refusing to use another company's D1")
    if CONFIG["cloudflare"]["r2Bucket"]!="xuyi-drinkware-r2":
        fail("Refusing to use another company's R2")
    if CONFIG["site"]["origin"]!="https://xuyibottles.com":
        fail("Unexpected site origin")
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    env={**os.environ,"XUYI_OUTPUT_DIR":"dist","PYTHONDONTWRITEBYTECODE":"1"}
    snapshot=ROOT/"_local_ops"/"build-snapshot.json"
    if snapshot.is_file():
        state=json.loads(snapshot.read_text(encoding="utf-8"))
        if state.get("site")!="xuyi-drinkware-site":
            fail("Refusing non-XUYI build snapshot")
        env["XUYI_BUILD_SNAPSHOT"]=str(snapshot)
        env["XUYI_PUBLISH_REVISION"]=str(int(state.get("publishRevision",0)))
    subprocess.run([sys.executable,"build.py"],cwd=ROOT,env=env,check=True)
    # Keep static artifacts and Functions separate; Wrangler bundles sibling
    # functions/ during Pages deploy. Never publish source, backups or secrets.
    shutil.copytree(ROOT/"assets",DIST/"assets",ignore=shutil.ignore_patterns("*.md"))
    admin_slug=resolve_admin_path(state.get("adminPath","admin") if snapshot.is_file() else "admin")
    shutil.copytree(ROOT/"admin",DIST/admin_slug)
    subprocess.run([sys.executable,"scripts/render_locales.py"],cwd=ROOT,env=env,check=True)
    if snapshot.is_file():
        state=json.loads(snapshot.read_text(encoding="utf-8"))
        valid=[]
        for row in state.get("redirects",[]):
            src=row.get("source_path","");target=row.get("target_path","")
            code=int(row.get("status_code",301))
            if not (isinstance(src,str) and src.startswith("/") and " " not in src and "\n" not in src):
                continue
            if not (isinstance(target,str) and (target.startswith("/") or target.startswith("https://"))
                    and " " not in target and "\n" not in target):
                continue
            if code in (301,302):valid.append(f"{src} {target} {code}")
        if valid:(DIST/"_redirects").write_text("\n".join(valid)+"\n",encoding="utf-8")
    for name in ("favicon.svg","favicon.ico","favicon-16.png","favicon-32.png",
                 "apple-touch-icon.png","icon-192.png","icon-512.png",
                 "site.webmanifest","_headers"):
        shutil.copy2(ROOT/name,DIST/name)
    counts={}
    for path in DIST.rglob("*"):
        if path.is_file():
            group=path.relative_to(DIST).parts[0]
            counts[group]=counts.get(group,0)+1
    total=sum(counts.values())
    limit=CONFIG["build"]["hardLimitFiles"]
    if total>=limit:fail(f"Pages file hard stop: {total} >= {limit}")
    source_files=sorted((ROOT/"templates/site").glob("*.html"))
    templates={file.name:file_hash(file) for file in source_files}
    # Demalong V1.4 reports the true production data origin, not merely
    # whether a D1 API was reachable. Empty D1 tables mean source fallback.
    state=json.loads(snapshot.read_text(encoding="utf-8")) if snapshot.is_file() else {}
    sources={
        "brand":"cloudflare-d1:site_state.brand_config" if state.get("brand") else "source-fallback:brand",
        "navigation":"cloudflare-d1:site_navigation" if state.get("navigation") else "source-fallback:curated-navigation",
        "pageSeo":"cloudflare-d1:site_pages" if state.get("pages") else "source-fallback:page-metadata",
        "products":"cloudflare-d1:xuyi_product_content+source-catalog" if state.get("products") else "source-fallback:data/products.json",
        "pageBodies":"cloudflare-d1:xuyi_page_content" if state.get("pageBodies") else "source-fallback:python-page-modules",
        "locales":"cloudflare-d1:reviewed-translations" if state.get("translations") else "not-published:no-reviewed-translations"
    }
    metadata={
        "version":"XUYI source-templated static build v1",
        "siteOrigin":CONFIG["site"]["origin"],
        "pagesProject":CONFIG["cloudflare"]["pagesProjectName"],
        "generatedAt":datetime.now(timezone.utc).isoformat(),
        "sourceRevision":os.environ.get("GITHUB_SHA","local"),
        "publishRevision":int(env.get("XUYI_PUBLISH_REVISION","0")),
        "templateSet":"templates/site",
        "adminPath":admin_slug,
        "templateSha256":templates,
        "contentSources":sources,
        "fileCount":total,
        "fileBreakdown":counts,
        "noindex":not CONFIG["site"]["indexingApproved"]
    }
    (DIST/"build-meta.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if total>=CONFIG["build"]["warningFiles"]:
        print(f"WARNING: static file budget {total}")
    if not (DIST/"index.html").is_file() or not (DIST/admin_slug/"index.html").is_file():
        fail("Missing homepage or admin")
    print("DIST_BUILD_OK",f"files={total+1}",f"templates={len(templates)}",f"output={DIST}")

if __name__=="__main__":
    main()