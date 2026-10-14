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
    subprocess.run([sys.executable,"build.py"],cwd=ROOT,env=env,check=True)
    # Keep static artifacts and Functions separate; Wrangler bundles sibling
    # functions/ during Pages deploy. Never publish source, backups or secrets.
    shutil.copytree(ROOT/"assets",DIST/"assets",ignore=shutil.ignore_patterns("*.md"))
    admin_slug=resolve_admin_path(state.get("adminPath","admin") if snapshot.is_file() else "admin")
    shutil.copytree(ROOT/"admin",DIST/admin_slug)
    subprocess.run([sys.executable,"scripts/render_locales.py"],cwd=ROOT,env=env,check=True)
    from repair_localized_blog_thumbnails import apply as repair_localized_blog_thumbnails
    repair_localized_blog_thumbnails(DIST)
    # Final, explicit buyer-landing SEO curation follows D1 reviewed HTML.
    # It does not rewrite CMS data or any translated product specifications.
    from polish_priority_seo import apply as polish_priority_seo
    polish_priority_seo(DIST)
    # Replace only reviewed generic-category and OEM editorial images.
    # Original catalog product photos and R2 objects remain untouched.
    from reviewed_editorial_images import apply as replace_reviewed_editorial_images
    replace_reviewed_editorial_images(DIST)
    from reviewed_lowres_editorial_round2 import apply as replace_lowres_round2
    replace_lowres_round2(DIST)
    # slide-059 contains machinery, not sports bottles. Repair only the
    # explicitly named Sports Water Bottles category cards.
    from repair_mismatched_sports_category import apply as repair_sports_cards
    repair_sports_cards(DIST)
    from repair_remaining_category_cards import apply as repair_remaining_categories
    repair_remaining_categories(DIST)
    from fix_primary_image_placements import apply as fix_primary_image_placements
    fix_primary_image_placements(DIST)
    # Exact, editorially mapped inbound links for previously isolated
    # application/feature pages, across all five reviewed languages.
    from buyer_journey_internal_links import apply as curate_buyer_journey_links
    curate_buyer_journey_links(DIST)
    # Six visually audited plastic-shaker scenes only; R2 originals immutable.
    from apply_gpt_reviewed_shaker_hd import apply as apply_gpt_reviewed_shaker_hd
    apply_gpt_reviewed_shaker_hd(DIST)
    # Share previews mirror actual schema product photos, never guessed SKUs.
    from product_share_images import apply as apply_product_share_images
    apply_product_share_images(DIST)
    # Exact page illustrations only; no new photos and no unrelated generic
    # preview images on privacy and contact pages.
    from contextual_share_metadata import apply as add_contextual_share_metadata
    add_contextual_share_metadata(DIST)
    from curated_buyer_seo_round2 import apply as apply_curated_buyer_seo_round2
    apply_curated_buyer_seo_round2(DIST)
    # Replace excessively generic long localized snippets using model-specific
    # catalog facts, without inventing price, stock, tests or certifications.
    from curated_catalog_meta_clarity import apply as clarify_localized_catalog_meta
    clarify_localized_catalog_meta(DIST)
    # Source-reviewed ml/fl oz search wording, real gradient color details
    # and an explicitly CONDITIONAL BPA material-verification prompt on home.
    # Preserve later CMS titles/descriptions and original factory model IDs.
    from verified_capacity_gradient_en import apply as add_verified_capacity_gradient
    add_verified_capacity_gradient(DIST)
    # Every real capacity in every current/future source-backed model receives
    # its US-fluid-ounce counterpart, all 5 locales, search snippets/cards
    # and a conditional Tritan/BPA-free CUSTOMIZATION inquiry (not certification).
    # User-authored CMS SEO fields are protected by checked-in D1 fingerprints.
    from source_catalog_capacity_oz import apply as apply_all_volume_and_custom_materials
    apply_all_volume_and_custom_materials(DIST)
    # Comparisons only from the 85 catalog entries with verified numeric data.
    # G-series ARE factory models, but their detailed source specs are pending.
    from model_catalog_buyer_comparison import apply as add_model_catalog_comparisons
    add_model_catalog_comparisons(DIST)
    from curated_application_feature_answers import apply as improve_application_feature_answers
    improve_application_feature_answers(DIST)
    if snapshot.is_file():
        state=json.loads(snapshot.read_text(encoding="utf-8"))
        valid=redirect_lines(state.get("redirects",[]))
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
    # Demalong V1.4 reports the true production data origin, not merely
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
        home_headers.extend([home_url,'  Link: <'+image+'>; rel="preload"; as="image"'])
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