#!/usr/bin/env python3
"""Build the isolated LEYA MOULD static release.

This release step deliberately packages only this repository's templates,
assets and admin UI.  A post-seed rebuild keeps the static revision aligned
with the current D1 publish revision.  Cloudflare bindings and business data remain owned by
the LEYA D1/R2 project; no remote API is called here.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
CONFIG = json.loads((ROOT / "deployment/site.config.json").read_text(encoding="utf-8"))


def copy_tree(source: Path, target: Path, ignore=None) -> None:
    if source.exists():
        shutil.copytree(source, target, dirs_exist_ok=True, ignore=ignore)


def source_revision() -> str:
    """Return the real source revision in GitHub, Pages, or local builds."""
    for name in ("LEYA_RELEASE_SHA", "GITHUB_SHA", "CF_PAGES_COMMIT_SHA", "CF_PAGES_COMMIT_HASH", "COMMIT_SHA"):
        value = str(os.environ.get(name) or "").strip()
        if value and value.lower() != "local":
            return value
    try:
        value = subprocess.check_output(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if value:
            return value
    except (OSError, subprocess.CalledProcessError):
        pass
    return "local"


def main() -> None:
    if CONFIG["cloudflare"]["pagesProjectName"] != "leyamould":
        raise SystemExit("Refusing to target another Pages project")
    if CONFIG["cloudflare"]["d1Database"] != "leyamould-d1":
        raise SystemExit("Refusing to use another D1 database")
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    env = {**os.environ, "LEYA_OUTPUT_DIR": "dist", "PYTHONDONTWRITEBYTECODE": "1"}
    subprocess.run([sys.executable, "build.py"], cwd=ROOT, env=env, check=True)
    copy_tree(ROOT / "assets", DIST / "assets", ignore=shutil.ignore_patterns("*.md"))
    copy_tree(ROOT / "admin", DIST / "admin")
    for name in ("favicon.svg", "favicon.ico", "favicon-192.png", "favicon-16.png", "favicon-32.png", "apple-touch-icon.png", "icon-192.png", "icon-512.png", "site.webmanifest", "_headers"):
        source = ROOT / name
        if source.is_file():
            shutil.copy2(source, DIST / name)
    # Ensure admin is never indexed and add a stable, local header policy.
    admin = DIST / "admin" / "index.html"
    if admin.is_file():
        content = admin.read_text(encoding="utf-8")
        if 'name="robots"' not in content:
            content = content.replace("<head>", '<head><meta name="robots" content="noindex,nofollow">', 1)
        admin.write_text(content, encoding="utf-8")
    static_files = [p for p in DIST.rglob("*") if p.is_file()]
    breakdown = {}
    for path in static_files:
        group = path.relative_to(DIST).parts[0]
        breakdown[group] = breakdown.get(group, 0) + 1
    templates = {}
    for path in sorted((ROOT / "templates/site").glob("*.html")):
        templates[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    snapshot = ROOT / "_local_ops/build-snapshot.json"
    state = json.loads(snapshot.read_text(encoding="utf-8")) if snapshot.is_file() else {}
    # CI/Pages builds must never silently publish a clean checkout with empty
    # business data. Local visual work can still opt out by omitting the flag.
    if str(os.environ.get("LEYA_REQUIRE_D1_SNAPSHOT", "")).lower() in {"1", "true", "yes"}:
        if not snapshot.is_file() or state.get("site") != "leyamould":
            raise SystemExit("Refusing production build without an authenticated LEYA D1 snapshot")
    fallback_models = json.loads((ROOT / "data/mould-models.json").read_text(encoding="utf-8")) if (ROOT / "data/mould-models.json").is_file() else {"models": []}
    model_reference_rows = state.get("modelReferences") if isinstance(state.get("modelReferences"), list) else []
    model_reference_count = len(model_reference_rows) if model_reference_rows else len([row for row in fallback_models.get("models", []) if isinstance(row, dict)])
    manifest = json.loads((DIST / "locale-manifest.json").read_text(encoding="utf-8"))
    sources = {
        "brand": "cloudflare-d1:site_state.brand_config" if state.get("brand") else "source-fallback:LEYA company profile",
        "navigation": "cloudflare-d1:site_navigation filtered to mould routes" if state.get("navigation") else "source-fallback:data/mould-catalog.json",
        "pageSeo": "cloudflare-d1:site_pages" if state.get("pages") else "source-fallback:mould source renderer",
        "products": "cloudflare-d1:mould product content" if state.get("products") else "source-fallback:data/mould-catalog.json",
        "productSeo": "cloudflare-d1:xuyi_product_seo plus reviewed D1 product fields" if state.get("productSeo") else "source-fallback:effective product metadata only",
        "pageBodies": "cloudflare-d1:page content" if state.get("pageBodies") else "source-fallback:mould source renderer",
        "pageCopy": "cloudflare-d1:site_state.page_copy" if state.get("pageCopy") else "source-fallback:mould structured page copy",
        "blogPosts": "cloudflare-d1:blog posts" if state.get("blogPosts") else "source-fallback:empty reviewed resources",
        "translations": "cloudflare-d1:xuyi_translation_overrides and localized D1 records" if state.get("translations") else "source-fallback:locale renderer copy",
        "commonCopy": "cloudflare-d1:site_state.common_copy" if state.get("commonCopy") else "source-fallback:mould renderer copy",
        "mediaAlts": "cloudflare-d1:xuyi_media_alt" if state.get("mediaAlts") else "source-fallback:reviewed media manifest",
        "productReviews": "cloudflare-d1:xuyi_product_reviews" if state.get("productReviews") else "source-fallback:no published reviews",
        "youtubeVideos": "cloudflare-d1:leya_youtube_videos" if state.get("youtubeVideos") else "source-fallback:reviewed YouTube registry",
        "modelReferences": "cloudflare-d1:leya_model_references" if model_reference_rows else "source-fallback:data/mould-models.json",
        "locales": "deployment/site.config.json + D1 publish-ready filter",
    }
    meta = {
        "version": "LEYA mould source-templated static build v1",
        "localizationFrameworkVersion": CONFIG["localizationFrameworkVersion"],
        "publishedLocales": [row["code"] for row in manifest["locales"]],
        "siteOrigin": CONFIG["site"]["origin"],
        "pagesProject": CONFIG["cloudflare"]["pagesProjectName"],
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        # GitHub Actions and Cloudflare Pages both expose a commit SHA.  The
        # git fallback keeps direct/local builds auditable instead of silently
        # labelling a checked-out source tree as "local".
        "sourceRevision": source_revision(),
        "publishRevision": int(state.get("publishRevision", 0) or 0),
        "templateSet": "templates/site",
        "adminPath": "admin",
        "templateSha256": templates,
        "contentSources": sources,
        "fileCount": len(static_files) + 1,
        "fileBreakdown": breakdown,
        "modelReferenceCount": model_reference_count,
        "staticModelCount": model_reference_count if not model_reference_rows else 0,
        "contentCounts": {
            "pages": len(state.get("pages") or []),
            "pageBodies": len(state.get("pageBodies") or []),
            "products": len(state.get("products") or []),
            "productSeo": len(state.get("productSeo") or []),
            "translations": len(state.get("translations") or []),
            "blogPosts": len(state.get("blogPosts") or []),
            "modelReferences": len(state.get("modelReferences") or []),
            "mediaAlts": len(state.get("mediaAlts") or []),
            "productReviews": len(state.get("productReviews") or []),
            "youtubeVideos": len(state.get("youtubeVideos") or []),
        },
        "noindex": not CONFIG["site"]["indexingApproved"],
    }
    (DIST / "build-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Keep the standalone Pages build entry point equivalent to the canonical
    # workflow: a Git-integrated build must also publish the protected-media
    # reference index, not just the HTML assets.
    from r2_usage_index import generate as generate_r2_usage_index
    media_references, media_locations = generate_r2_usage_index(DIST, ROOT / "_local_ops/model-overflow")
    final_files = [path for path in DIST.rglob("*") if path.is_file()]
    final_breakdown = {}
    for path in final_files:
        group = path.relative_to(DIST).parts[0]
        final_breakdown[group] = final_breakdown.get(group, 0) + 1
    meta["fileCount"] = len(final_files)
    meta["fileBreakdown"] = final_breakdown
    (DIST / "build-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("DIST_BUILD_OK", f"files={len(final_files)}", f"locales={','.join(meta['publishedLocales'])}", f"mediaReferences={media_references}", f"mediaLocations={media_locations}", f"output={DIST}")


if __name__ == "__main__":
    main()




