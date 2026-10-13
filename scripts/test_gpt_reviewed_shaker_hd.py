#!/usr/bin/env python3
"""Guard reviewed assets, exact SKUs, five locales and social image metadata."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
data = json.loads((ROOT / "data/gpt-reviewed-shaker-hd-20261013.json").read_text(encoding="utf-8"))
assert len(data["approved"]) == 6 and len(data["rejected"]) == 4
assert {x["old"].split("/")[-1] for x in data["approved"]} == {f"slide-{i:03d}.webp" for i in range(91,97)}
for item in data["approved"]:
    original, new = item["old"], item["new"]
    blob = (ROOT / new.lstrip("/")).read_bytes()
    assert blob[:4] == b"RIFF" and blob[8:12] == b"WEBP"
    assert hashlib.sha256(blob).hexdigest() == item["publishedAssetSha256"]
    assert min(item["candidateDimensions"]) >= 900
    assert (DIST / new.lstrip("/")).is_file()
    for locale in ("", "es/", "pt/", "ru/", "tr/"):
        for sku in item["skuIds"]:
            file = DIST / locale / "products" / sku / "index.html"
            content = file.read_text(encoding="utf-8")
            assert original not in content, (file, "old same-scene source still referenced")
            assert re.search(r'<img id="main-photo" src="'+re.escape(new)+r'"', content), (file, "main photo")
            assert f'<meta property="og:image" content="https://xuyibottles.com{new}">' in content, (file, "OG image")
            assert '"image":["https://xuyibottles.com'+new+'"' in content or \
                '"image": ["https://xuyibottles.com'+new+'"' in content, (file, "Product schema")
for item in data["rejected"]:
    for model in item["skuIds"]:
        content = (DIST / "products" / model / "index.html").read_text(encoding="utf-8")
        assert item["old"] in content, (model, "Rejected source unexpectedly changed")
print("XUYI_SIX_GPT_REVIEWED_SHAKERS_FIVE_LOCALES_PASS")