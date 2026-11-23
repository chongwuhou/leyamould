#!/usr/bin/env python3
"""Validate the LEYA MOULD public R2 reference index emitted for a release."""
from pathlib import Path
import json
import re
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r2_usage_index import inventory

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
INDEX = DIST / "r2-usage-index.json"
META = DIST / "build-meta.json"

assert INDEX.is_file(), "Build must emit the release media usage index"
assert META.is_file(), "Build must emit build metadata before the media index"
data = json.loads(INDEX.read_text(encoding="utf-8"))
meta = json.loads(META.read_text(encoding="utf-8"))
assert data.get("site") == "leyamould" and data.get("schemaVersion") == 1
assert data.get("publishRevision") == meta.get("publishRevision")
refs = data.get("references")
assert isinstance(refs, dict)
media_path = re.compile(r"^/media/(?:ppt|excel|group|gallery|capability|blog|product|page|shared)/[A-Za-z0-9._-]+\.(?:webp|png|jpg|jpeg)$", re.I)
assert all(media_path.fullmatch(path) for path in refs), "Only approved LEYA media paths may be indexed"
assert all("../" not in location for locations in refs.values() for location in locations)
assert all(isinstance(locations, list) and locations for locations in refs.values())

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "index.html").write_text('<img src="/media/page/' + "a" * 32 + '.webp">', encoding="utf-8")
    sub = root / "es"
    sub.mkdir()
    (sub / "index.html").write_text('<img src="/media/page/' + "a" * 32 + '.webp">', encoding="utf-8")
    result = inventory(root)
    assert result["/media/page/" + "a" * 32 + ".webp"] == ["/", "/es/"]

print("LEYA_R2_USAGE_INDEX_PASSED", len(refs), "media references; revision", data["publishRevision"])

