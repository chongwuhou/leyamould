#!/usr/bin/env python3
"""Generic, idempotent backfill of reviewed Blog fields into XUYI D1.

This is a migration utility, not a build input. It reads the currently reviewed
source registries only to seed missing D1 fields, never replaces owner values.
"""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MATRIX_FILE = re.compile(r"blog-buyer-decision-tables(?:-20\\d{6})?\\.json$")
GUIDE_FILE = re.compile(r"blog-guides(?:-20\\d{6}(?:-\\d+)?)?\\.json$")

def add_table(tables, slug, value, source):
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise SystemExit("Invalid Blog slug in "+source+": "+str(slug))
    if not isinstance(value, dict):
        raise SystemExit("Invalid buyerDecisionTable in "+source+": "+slug)
    old = tables.get(slug)
    if old is not None and old != value:
        raise SystemExit("Conflicting buyerDecisionTable sources for "+slug)
    tables[slug] = value

tables = {}
for path in sorted((ROOT / "data").glob("blog-buyer-decision-tables*.json")):
    if not MATRIX_FILE.fullmatch(path.name):
        continue
    payload = json.loads(path.read_text(encoding="utf-8"))
    for slug, value in (payload.get("articles") or {}).items():
        add_table(tables, slug, value, path.name)
for path in sorted((ROOT / "data").glob("blog-guides*.json")):
    if not GUIDE_FILE.fullmatch(path.name):
        continue
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload if isinstance(payload, list) else [payload]
    for row in rows:
        if isinstance(row, dict) and row.get("buyerDecisionTable") is not None:
            add_table(tables, row.get("slug"), row.get("buyerDecisionTable"), path.name)

if not tables:
    raise SystemExit("No reviewed Blog buyer decision tables found")
origin = os.environ.get("SITE_ORIGIN", "https://xuyibottles.com").rstrip("/")
token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
if not token:
    raise SystemExit("CLOUDFLARE_API_TOKEN is required; it is never printed")
payload = {"blogBuyerDecisionTables": [
    {"slug": slug, "buyerDecisionTable": tables[slug]}
    for slug in sorted(tables)
]}
request = Request(
    origin + "/api/admin/cms-source-migration",
    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    headers={
        "authorization": "Bearer " + token,
        "content-type": "application/json",
        "x-xuyi-publish-intent": "explicit-owner-approval",
    },
    method="POST",
)
try:
    with urlopen(request, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
except HTTPError as error:
    body = error.read().decode("utf-8", "replace")
    raise SystemExit("D1 migration rejected with HTTP "+str(error.code)+": "+body[:1000])
except URLError as error:
    raise SystemExit("D1 migration network failure: "+str(error.reason))
print("XUYI_D1_BLOG_SOURCE_FIELD_MIGRATION", json.dumps({
    "sourceTables": len(tables),
    "updated": result.get("updated"),
    "skipped": result.get("skipped"),
    "publishRevision": result.get("publishRevision"),
}, ensure_ascii=False))
