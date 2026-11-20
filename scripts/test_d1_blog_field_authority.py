#!/usr/bin/env python3
"""Verify that reviewed Blog decision fields are present in published D1 snapshot."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "_local_ops" / "build-snapshot.json"
if not SNAPSHOT.is_file():
    raise SystemExit("Missing D1 build snapshot")
state = json.loads(SNAPSHOT.read_text(encoding="utf8"))
assert state.get("site") == "leyamould" and state.get("schemaVersion") == 1

sys.path.insert(0, str(ROOT))
from blog_catalog_source import load_guides

source_slugs = {str(row["slug"]) for row in load_guides(ROOT)}
base = json.loads((ROOT / "data/blog-buyer-decision-tables.json").read_text(encoding="utf8"))
source_slugs.update(str(slug) for slug in (base.get("articles") or {}))
published = {
    str(row.get("slug")): row
    for row in state.get("blogPosts", [])
    if isinstance(row, dict) and row.get("status") == "published"
}
missing = []
invalid = []
for slug in sorted(source_slugs):
    row = published.get(slug)
    table = row.get("buyerDecisionTable") if row else None
    if not row:
        missing.append(slug)
        continue
    if not isinstance(table, dict) or len(table.get("head") or []) != 3 or len(table.get("rows") or []) < 4:
        invalid.append(slug)
if missing or invalid:
    raise SystemExit("D1 Blog field authority failed: missing="+repr(missing)+" invalid="+repr(invalid))
print("XUYI_D1_BLOG_BUYER_FIELDS_AUTHORITY_PASSED", len(source_slugs), "source slugs", len(published), "published D1 rows")
