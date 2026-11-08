#!/usr/bin/env python3
"""XUYI Pages release builder with a separate build/deploy process.

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

# The release process imports post-build enrichers that themselves import
# site_renderer. Load the authenticated D1 snapshot before any project module
# can import site_renderer, not only in child build.py processes.
ROOT=Path(__file__).resolve().parent.parent
_EARLY_SNAPSHOT=ROOT/"_local_ops"/"build-snapshot.json"
if _EARLY_SNAPSHOT.is_file():
    _EARLY_STATE=json.loads(_EARLY_SNAPSHOT.read_text(encoding="utf-8"))
    if _EARLY_STATE.get("site")=="xuyi-drinkware-site":
        os.environ["XUYI_BUILD_SNAPSHOT"]=str(_EARLY_SNAPSHOT)
        os.environ["XUYI_PUBLISH_REVISION"]=str(int(_EARLY_STATE.get("publishRevision",0)))

from admin_route import admin_path as resolve_admin_path
from plan_model_overflow import plan as plan_model_overflow
from site_redirects import redirect_lines
from r2_usage_index import generate as generate_r2_reference_index
from search_submission import create_manifest as create_search_manifest, key_file as create_indexnow_key

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
        # Post-build enrichers import site_renderer in this same process.
        # Keep them on the exact D1 snapshot used by build.py and render_locales.py.
        os.environ["XUYI_BUILD_SNAPSHOT"]=str(snapshot)
        os.environ["XUYI_PUBLISH_REVISION"]=env["XUYI_PUBLISH_REVISION"]
    # Generate display-only, content-addressed images from authoritative
    # sources. Originals in R2, asset files, and owner CMS selections remain.
    from prepare_responsive_images import prepare as prepare_responsive
    image_manifest,image_stage=prepare_responsive(snapshot)
    env["XUYI_RESPONSIVE_MANIFEST"]=str(image_manifest)
    subprocess.run([sys.executable,"build.py"],cwd=ROOT,env=env,check=True)
    # Keep static artifacts and Functions separate; Wrangler bundles sibling
    # functions/ during Pages deploy. Never publish source, backups or secrets.
    shutil.copytree(ROOT/"assets",DIST/"assets",ignore=shutil.ignore_patterns("*.md"))
    admin_slug=resolve_admin_path(state.get("adminPath","admin") if snapshot.is_file() else "admin")
    shutil.copytree(ROOT/"admin",DIST/admin_slug)
    subprocess.run([sys.executable,"scripts/render_locales.py"],cwd=ROOT,env=env,check=True)
    shutil.copytree(image_stage,DIST/"assets"/"responsive",dirs_exist_ok=True)
    # Product SEO metadata, hreflang, structured data, editorial imagery,
    # contextual links and social previews are source-rendered before each page write.
    # The locale registry adds reciprocal alternates only for non-product routes.    # Do not run the obsolete product_share_images dist mutator.
    # Contextual social previews and image dimensions are source-rendered
    # before each page write; never mutate the finished dist tree.
    # Curated category snippets and related Blog links are source-rendered.
    # Product SEO titles and descriptions are written by the shared source
    # renderers with per-field D1 ownership checks; do not mutate dist metadata.
    # Product capacities, approximate US fl-oz size classes, custom-material inquiry panels,
    # gradient notes and product-card search terms are source-rendered in the
    # shared English and localized renderers before files enter dist.
    # Model comparisons, product actions, homepage FAQ schema, blog bylines and
    # social-image dimensions are injected in shared renderers before each write.
    # llms.txt remains a separate optional navigation artifact, not a ranking claim.
    from verified_trust_technical_seo import build_llms
    build_llms(DIST)
    # Compile redirects from authority-controlled sources BEFORE deployment:
    # approved D1 redirects first, plus only the five proven slug-format fixes
    # across published locales. Never overwrite a CMS owner-authored redirect.
    state=json.loads(snapshot.read_text(encoding="utf-8")) if snapshot.is_file() else {}
    valid=redirect_lines(state.get("redirects",[]))
    from product_slug_fix import source_redirects
    from locale_registry import approved_locales
    prefixes=[entry["pathPrefix"] for entry in approved_locales(state)]
    seen={line.split(" ",1)[0] for line in valid}
    valid += [line for line in source_redirects(prefixes) if line.split(" ",1)[0] not in seen]
    if valid:(DIST/"_redirects").write_text("\n".join(valid)+"\n",encoding="utf-8")
    for name in ("favicon.svg","favicon.ico","favicon-16.png","favicon-32.png",
                 "apple-touch-icon.png","icon-192.png","icon-512.png",
                 "site.webmanifest","_headers"):
        shutil.copy2(ROOT/name,DIST/name)
    # Never drop static model HTML unless the bundling planner produced all
    # corresponding locale HTML and a validated manifest for R2 synchronization.
    overflow_dir=ROOT/"_local_ops"/"model-overflow"
    if overflow_dir.exists():shutil.rmtree(overflow_dir)
    overflow=plan_model_overflow(DIST,overflow_dir,
        switch_at=int(CONFIG["build"]["warningFiles"]),target=int(CONFIG["build"].get("overflowTargetFiles",15500)),
        hard_stop=int(CONFIG["build"]["hardLimitFiles"]))
    # No verification key is published while noindex remains active. When
    # launch is approved, the key must come from a GitHub Actions secret.
    indexnow_key=create_indexnow_key()
    counts={}
    for path in DIST.rglob("*"):
        if path.is_file():
            group=path.relative_to(DIST).parts[0]
            counts[group]=counts.get(group,0)+1
    total=sum(counts.values())
    limit=CONFIG["build"]["hardLimitFiles"]
    if total+3>=limit:fail(f"Pages file hard stop: {total+3} >= {limit}")
    source_files=sorted((ROOT/"templates/site").glob("*.html"))
    templates={file.name:file_hash(file) for file in source_files}
    # The production snapshot reports the true data origin, not merely
    # whether a D1 API was reachable. Empty D1 tables mean source fallback.
    state=json.loads(snapshot.read_text(encoding="utf-8")) if snapshot.is_file() else {}
    sys.path.insert(0,str(ROOT))
    from locale_registry import approved_locales
    from home_banner_config import for_locale
    # Preload only the LCP hero of a locale homepage. The old /* rule made
    # every product/article preload FOUR unrelated carousel images, hurting
    # crawl performance. Never hardcode image URLs or language prefixes here.
    home_headers=[]
    for language in approved_locales(state):
        prefix=language["pathPrefix"]
        home_url="/"+prefix+"/" if prefix else "/"
        first=for_locale(state,language["code"])[0]
        image=first["img"]
        if not image.startswith(("/media/","/assets/")) or ".." in image:
            fail("Unsafe homepage preload image: "+image)
        prepared=json.loads(image_manifest.read_text(encoding="utf-8")).get(image)
        variants=(prepared or {}).get("variants") or []
        if variants:
            srcset=", ".join(v["url"]+" "+str(v["w"])+"w" for v in variants)
            home_headers.extend([home_url,'  Link: <'+variants[-1]["url"]+'>; rel="preload"; as="image"; imagesrcset="'+srcset+'"; imagesizes="(max-width: 760px) 92vw, 48vw"'])
        else:
            home_headers.extend([home_url,'  Link: <'+image+'>; rel="preload"; as="image"'])
    # Every filename contains an immutable hash of its original image bytes.
    # Do not apply immutable caching to mutable /media/ or editor-uploaded URLs.
    home_headers.extend([
        "/admin/*",
        "  Cache-Control: no-store, max-age=0, must-revalidate",
        "/assets/admin-*",
        "  Cache-Control: no-store, max-age=0, must-revalidate",
        "/assets/xuyi-admin-bridge.js",
        "  Cache-Control: no-store, max-age=0, must-revalidate",
        "/assets/responsive/*",
        "  Cache-Control: public, max-age=31536000, immutable",
    ])
    (DIST/"_headers").write_text("\n".join(home_headers)+"\n",encoding="utf-8")
    # A saved D1 Banner image must exist in the published static artifact.
    # /media references are verified by the authenticated CMS before saving.
    sys.path.insert(0,str(ROOT))
    from home_banner_config import config_for
    for slide in config_for(state)["slides"]:
        path=slide["img"]
        if path.startswith("/assets/") and not (DIST/path.lstrip("/")).is_file():
            fail("Missing homepage banner asset: "+path)
    sources={
        "brand":"cloudflare-d1:site_state.brand_config" if state.get("brand") else "source-fallback:brand",
        "navigation":"cloudflare-d1:site_navigation" if state.get("navigation") else "source-fallback:curated-navigation",
        "pageSeo":"cloudflare-d1:site_pages" if state.get("pages") else "source-fallback:page-metadata",
        "products":"cloudflare-d1:xuyi_product_content+source-catalog" if state.get("products") else "source-fallback:data/products.json",
        "pageBodies":"cloudflare-d1:xuyi_page_content" if state.get("pageBodies") else "source-fallback:python-page-modules",
        "blogPosts":"cloudflare-d1:xuyi_blog_posts" if state.get("blogPosts") else "source-fallback:static-editorial-guides",
        "locales":"cloudflare-d1:reviewed-translations" if state.get("translations") else "not-published:no-reviewed-translations"
    }
    metadata={
        "version":"XUYI source-templated static build v1",
        "localizationFrameworkVersion":CONFIG["localizationFrameworkVersion"],
        "publishedLocales":[l["code"] for l in json.loads(
           (DIST/"locale-manifest.json").read_text(encoding="utf-8"))["locales"]],
        "siteOrigin":CONFIG["site"]["origin"],
        "pagesProject":CONFIG["cloudflare"]["pagesProjectName"],
        "generatedAt":datetime.now(timezone.utc).isoformat(),
        "sourceRevision":os.environ.get("GITHUB_SHA","local"),
        "publishRevision":int(env.get("XUYI_PUBLISH_REVISION","0")),
        "templateSet":"templates/site",
        "adminPath":admin_slug,
        "templateSha256":templates,
        "contentSources":sources,
        "fileCount":total+3, # includes build-meta, R2 usage and search hash manifest
        "fileBreakdown":counts,
        "modelPageStorageMode":overflow["mode"],
        "projectedStaticFileCountBeforeOverflow":overflow["projectedStaticFileCountBeforeOverflow"],
        "staticModelCount":overflow["catalogModelCount"]-overflow["modelCount"],
        "overflowModelCount":overflow["modelCount"],
        "overflowLocalizedPageCount":overflow["localizedPageCount"],
        "modelOverflowSwitchAt":int(CONFIG["build"]["warningFiles"]),
        "modelStaticTarget":int(CONFIG["build"].get("overflowTargetFiles",15500)),
        "noindex":not CONFIG["site"]["indexingApproved"]
    }
    (DIST/"build-meta.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    refs,uses=generate_r2_reference_index(DIST,overflow_dir)
    print("XUYI_R2_REFERENCE_INDEX",refs,"images",uses,"uses")
    search_manifest=create_search_manifest()
    print("XUYI_SEARCH_URLS_PREPARED",len(search_manifest["urls"]),
          "indexingApproved",CONFIG["site"]["indexingApproved"],
          "indexNowKeyPublished",bool(indexnow_key))
    if total>=CONFIG["build"]["warningFiles"]:
        print(f"WARNING: static file budget {total}")
    if not (DIST/"index.html").is_file() or not (DIST/admin_slug/"index.html").is_file():
        fail("Missing homepage or admin")
    print("DIST_BUILD_OK",f"files={total+3}",f"templates={len(templates)}",f"output={DIST}")

if __name__=="__main__":
    main()