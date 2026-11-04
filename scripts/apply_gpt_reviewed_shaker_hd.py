#!/usr/bin/env python3
"""Replace only source-matched, reviewed shaker photos in static HTML.

Original R2 sources stay accessible and unchanged; no product specifications,
D1 rows or Cloudflare R2 object bytes are modified.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
from functools import lru_cache
import re

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data/gpt-reviewed-shaker-hd-20261013.json"

@lru_cache(maxsize=1)
def approved_manifest():
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schemaVersion")!=1 or data.get("site")!="xuyi-drinkware-site":
        raise ValueError("Unknown approved image manifest")
    approved=data.get("approved",[])
    if len(approved)!=6 or len({x.get("old") for x in approved})!=6:
        raise ValueError("Exactly six approved unique sources required")
    for item in approved:
        old,new=item["old"],item["new"]
        if not old.startswith("/media/ppt/slide-") or not new.startswith("/assets/sku-hd/"):
            raise ValueError("Image mapping outside reviewed namespace")
        image=ROOT/new.lstrip("/")
        if not image.is_file() or hashlib.sha256(image.read_bytes()).hexdigest()!=item["publishedAssetSha256"]:
            raise ValueError("Reviewed asset changed or missing: "+new)
    return approved

def approved_image_url(url):
    for item in approved_manifest():
        if url==item["old"]:
            return item["new"]
    return url

def apply_to_document(markup,route=None,locale=None):
    approved=approved_manifest()
    for item in approved:
        markup=markup.replace(item["old"],item["new"])
    if route:
        base=str(route or "/")
        if locale and locale!="en" and base.startswith("/"+locale+"/"):
            base=base[len(locale)+1:]
        product=re.search(r"/products/([^/]+)/",base)
        if product:
            slug=product.group(1)
            for item in approved:
                if slug in item["skuIds"]:
                    main=re.search(r'<img id="main-photo" src="([^"]+)"',markup)
                    if not main or main.group(1)==item["old"]:
                        raise ValueError("Invalid/unreplaced approved SKU source image: "+slug)
    return markup


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
    # The old media source may disappear when an editor replaces all
    # instances with a newer verified photo in D1. Never force the previous
    # approved asset back or fail a release just because its source vanished.
    for item in approved:
        for model in item["skuIds"]:
            for locale in ("", "es/", "pt/", "ru/", "tr/"):
                page = dist / locale / "products" / model / "index.html"
                if not page.is_file():
                    raise FileNotFoundError("SKU page/locale missing: " + str(page))
                body=page.read_text(encoding="utf-8")
                main=re.search(r'<img id="main-photo" src="([^"]+)"',body)
                if not main or not main.group(1).startswith(("/assets/","/media/")):
                    raise ValueError("Invalid SKU source image: " + str(page))
                if main.group(1)==item["old"]:
                    raise ValueError("Unreplaced legacy SKU source image: " + str(page))
    # Rejected images stay untouched by the pipeline, but an editor may
    # later upload an authentic updated model photo. Never require the
    # rejected, low-resolution original to stay on the site forever.
    print("XUYI_GPT_APPROVED_SHAKERS", sum(changed.values()), "HTML URL substitutions")
    return sum(changed.values())

if __name__ == "__main__":
    apply(ROOT / "dist")