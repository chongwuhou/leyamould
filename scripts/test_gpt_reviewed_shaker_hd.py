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
            hero=re.search(r'<img id="main-photo" src="([^"]+)"',content)
            assert hero and hero.group(1)!=original,(file,"legacy low-res source still used for main SKU")
            main_image=hero.group(1)
            assert main_image.startswith(("/media/","/assets/")),(file,"invalid CMS main image")
            # A later editor-chosen social preview can differ from the catalog
            # product hero; never reject a CMS-approved first-party OG image.
            og = re.findall(r'<meta property="og:image" content="([^"]+)"', content.split("</head>",1)[0])
            twitter = re.findall(r'<meta name="twitter:image" content="([^"]+)"', content.split("</head>",1)[0])
            assert len(og)<=1 and len(twitter)<=1 and (og or twitter),(file,"social preview missing/duplicated")
            assert all(u.startswith("https://leyamould.com/") for u in og+twitter),(file,"invalid social preview")
            assert '"image":["https://leyamould.com'+main_image+'"' in content or \
                '"image": ["https://leyamould.com'+main_image+'"' in content, (file, "Product schema must match selected model photo")
# Rejected source images may be replaced with real, approved SKU photos by the
# owner without being forced back to an outdated image in this release test.
print("XUYI_SIX_GPT_REVIEWED_SHAKERS_FIVE_LOCALES_PASS")
