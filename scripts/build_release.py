#!/usr/bin/env python3
"""Build the isolated LEYA MOULD static release.

This release step deliberately packages only this repository's templates,
assets and admin UI.  Cloudflare bindings and business data remain owned by
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
    for name in ("favicon.svg", "favicon.ico", "favicon-16.png", "favicon-32.png", "apple-touch-icon.png", "icon-192.png", "icon-512.png", "site.webmanifest", "_headers"):
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
    manifest = json.loads((DIST / "locale-manifest.json").read_text(encoding="utf-8"))
    sources = {
        "brand": "cloudflare-d1:site_state.brand_config" if state.get("brand") else "source-fallback:LEYA company profile",
        "navigation": "cloudflare-d1:site_navigation filtered to mould routes" if state.get("navigation") else "source-fallback:data/mould-catalog.json",
        "pageSeo": "cloudflare-d1:site_pages" if state.get("pages") else "source-fallback:mould source renderer",
        "products": "cloudflare-d1:mould product content" if state.get("products") else "source-fallback:data/mould-catalog.json",
        "pageBodies": "cloudflare-d1:page content" if state.get("pageBodies") else "source-fallback:mould source renderer",
        "blogPosts": "cloudflare-d1:blog posts" if state.get("blogPosts") else "source-fallback:empty reviewed resources",
        "locales": "deployment/site.config.json + D1 publish-ready filter",
    }
    meta = {
        "version": "LEYA mould source-templated static build v1",
        "localizationFrameworkVersion": CONFIG["localizationFrameworkVersion"],
        "publishedLocales": [row["code"] for row in manifest["locales"]],
        "siteOrigin": CONFIG["site"]["origin"],
        "pagesProject": CONFIG["cloudflare"]["pagesProjectName"],
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceRevision": os.environ.get("GITHUB_SHA", "local"),
        "publishRevision": int(state.get("publishRevision", 0) or 0),
        "templateSet": "templates/site",
        "adminPath": "admin",
        "templateSha256": templates,
        "contentSources": sources,
        "fileCount": len(static_files) + 1,
        "fileBreakdown": breakdown,
        "staticModelCount": 0,
        "noindex": not CONFIG["site"]["indexingApproved"],
    }
    (DIST / "build-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("DIST_BUILD_OK", f"files={len(static_files)+1}", f"locales={','.join(meta['publishedLocales'])}", f"output={DIST}")


if __name__ == "__main__":
    main()

