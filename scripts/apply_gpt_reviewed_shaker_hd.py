#!/usr/bin/env python3
"""Replace only source-matched, reviewed shaker photos in static HTML.

Original R2 sources stay accessible and unchanged; no product specifications,
D1 rows or Cloudflare R2 object bytes are modified.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data/gpt-reviewed-shaker-hd-20261013.json"

def apply(dist):
    dist = Path(dist)
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1 or data.get("site") != "xuyi-drinkware-site":
        raise ValueError("Unknown approved image manifest")
    approved = data["approved"]
    if len(approved) != 6 or len({x["old"] for x in approved}) != 6:
        raise ValueError("Exactly six approved unique sources required")
    for item in approved:
        old, new = item["old"], item["new"]
        if not old.startswith("/media/ppt/slide-") or not new.startswith("/assets/sku-hd/"):
            raise ValueError("Image mapping outside reviewed namespace")
        image = ROOT / new.lstrip("/")
        if not image.is_file() or hashlib.sha256(image.read_bytes()).hexdigest() != item["publishedAssetSha256"]:
            raise ValueError("Reviewed asset changed or missing: " + new)
        if not (dist / new.lstrip("/")).is_file():
            raise FileNotFoundError("Release asset not copied: " + new)
    changed = Counter()
    for file in dist.rglob("*.html"):
        source = file.read_text(encoding="utf-8")
        updated = source
        for item in approved:
            old, new = item["old"], item["new"]
            count = updated.count(old)
            if count:
                updated = updated.replace(old, new)
                changed[old] += count
        if updated != source:
            file.write_text(updated, encoding="utf-8")
    if set(changed) != {x["old"] for x in approved}:
        raise ValueError("Approved source absent from published HTML: " + str(changed))
    for item in approved:
        for model in item["skuIds"]:
            for locale in ("", "es/", "pt/", "ru/", "tr/"):
                page = dist / locale / "products" / model / "index.html"
                if not page.is_file() or item["new"] not in page.read_text(encoding="utf-8"):
                    raise ValueError("SKU image/locale missing: " + str(page))
    for rejected in data["rejected"]:
        page = dist / "products" / rejected["skuIds"][0] / "index.html"
        if rejected["old"] not in page.read_text(encoding="utf-8"):
            raise ValueError("Rejected original accidentally removed: " + str(page))
    print("XUYI_GPT_APPROVED_SHAKERS", sum(changed.values()), "HTML URL substitutions")
    return sum(changed.values())

if __name__ == "__main__":
    apply(ROOT / "dist")