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
    subprocess.run([sys.executable,"build.py"],cwd=ROOT,env=env,check=True)
    # Keep static artifacts and Functions separate; Wrangler bundles sibling
    # functions/ during Pages deploy. Never publish source, backups or secrets.
    shutil.copytree(ROOT/"assets",DIST/"assets",ignore=shutil.ignore_patterns("*.md"))
    shutil.copytree(ROOT/"admin",DIST/"admin")
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
    source_files=[ROOT/"templates/site"/f"{n}.html" for n in ("header","footer","sidebar","shell")]
    templates={file.name:file_hash(file) for file in source_files}
    metadata={
        "version":"XUYI source-templated static build v1",
        "siteOrigin":CONFIG["site"]["origin"],
        "pagesProject":CONFIG["cloudflare"]["pagesProjectName"],
        "generatedAt":datetime.now(timezone.utc).isoformat(),
        "sourceRevision":os.environ.get("GITHUB_SHA","local"),
        "publishRevision":int(os.environ.get("XUYI_PUBLISH_REVISION","0")),
        "templateSet":"templates/site",
        "templateSha256":templates,
        "fileCount":total,
        "fileBreakdown":counts,
        "noindex":not CONFIG["site"]["indexingApproved"]
    }
    (DIST/"build-meta.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if total>=CONFIG["build"]["warningFiles"]:
        print(f"WARNING: static file budget {total}")
    if not (DIST/"index.html").is_file() or not (DIST/"admin/index.html").is_file():
        fail("Missing homepage or admin")
    print("DIST_BUILD_OK",f"files={total+1}",f"templates={len(templates)}",f"output={DIST}")

if __name__=="__main__":
    main()