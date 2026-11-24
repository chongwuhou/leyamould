"""Ensure the published mould build has no legacy image host references."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "data/mould-legacy-media-manifest.json").read_text(encoding="utf-8"))
items = manifest.get("items", [])
assert len(items) >= 200, len(items)
assert all(str(row.get("target", "")).startswith("/media/page/") for row in items)
assert all(re.fullmatch(r"/media/page/[a-f0-9]{32}\.webp", str(row.get("target", ""))) for row in items)

source_pattern = re.compile(r"https://www\.cap-molds\.com[^\"'\s<>)]*?\.(?:jpg|jpeg|png|gif|webp)(?:\?[^\"'\s<>)]*)?", re.I)
for path in (ROOT / "mould_build.py", ROOT / "mould_category_pages.py", ROOT / "data/mould-page-bodies.json", ROOT / "data/mould-catalog.json"):
    assert not source_pattern.search(path.read_text(encoding="utf-8")), path

print(f"LEYA_LEGACY_MEDIA_CONTRACT_PASSED objects={len(items)}")
