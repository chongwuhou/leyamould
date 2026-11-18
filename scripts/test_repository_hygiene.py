"""Keep the repository focused on current generic entrypoints.

Historical Blog batch publishers, dated repair endpoints and dated live
verification scripts are intentionally removed. Dated JSON that is imported
by the current renderer is allowed; this guard checks entrypoints, not content
timestamps.
"""
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN=(
    re.compile(r"^scripts/(?:prepare_blog_(?:release|covers|images)|publish_blog_(?:batch|covers|images|translation_repair)|schedule_blog_batch)_20\d+"),
    re.compile(r"^scripts/(?:test_20\d+|test_blog_20\d+|verify_live_blog_20\d+)"),
    re.compile(r"^scripts/test_blog_(?:covers|index_order|localized_schedule|schedule|translation_repair)_20\d+"),
    re.compile(r"^functions/api/admin/blog-(?:batch|covers|images|index-(?:copy|heading)-cleanup|refresh|schedule|translation-repair)-20\d+"),
    re.compile(r"^functions/api/admin/(?:blog-seo-phase2-corrections|collection-seo-refresh|product-seo-(?:promotion|refresh))"),
)
REQUIRED=(
    "functions/api/admin/blog-batch.js",
    "functions/api/admin/blog-media.js",
    "scripts/build_release.py",
    "scripts/fetch_build_snapshot.py",
    "scripts/test_pages_functions_syntax.py",
    "docs/XUYI_OPERATIONAL_RUNBOOK_ZH.md",
)
paths=[p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]
bad=[path for path in paths if any(pattern.search(path) for pattern in FORBIDDEN)]
missing=[path for path in REQUIRED if not (ROOT/path).is_file()]
if bad:
    print("::error::forbidden historical entrypoints remain:")
    print("\n".join(bad))
    sys.exit(1)
if missing:
    raise SystemExit("missing generic entrypoint: "+", ".join(missing))
print("XUYI_REPOSITORY_HYGIENE_PASSED",len(paths),"files")
