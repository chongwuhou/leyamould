"""Validate source-rendered image variants and owner CMS override behavior."""
from html import unescape
from pathlib import Path
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
MANIFEST = ROOT / "_local_ops" / "responsive-image-manifest.json"
sys.path.insert(0, str(ROOT))
from responsive_image_render import enhance_source_markup, LEGACY_REPLACED_SOURCES


def attrs(tag):
    return {k.lower(): unescape(v) for k, v in
            re.findall(r'\b([\w-]+)="([^"]*)"', tag)}


def main():
    assert MANIFEST.is_file(), "Image source manifest missing"
    manifest = json.loads(MANIFEST.read_text(encoding="utf8"))
    assert len(manifest) >= 20, "Too few source images; check upstream R2"
    count = 0
    pages = 0
    referenced = set()
    for page in DIST.rglob("*.html"):
        if "admin" in page.relative_to(DIST).parts:
            continue
        pages += 1
        for tag in re.findall(r"<img\b[^>]*>", page.read_text(encoding="utf8"), re.I):
            a = attrs(tag)
            if "srcset" not in a:
                continue
            count += 1
            source = a.get("src", "").split("?", 1)[0]
            item = manifest.get(source)
            assert item, ("Srcset must come from current source", str(page), source)
            expected = [(entry["url"], entry["w"]) for entry in item["variants"]]
            actual = []
            for part in a["srcset"].split(","):
                bits = part.strip().split()
                assert len(bits) == 2 and bits[1].endswith("w"), (source, "malformed srcset")
                actual.append((bits[0], int(bits[1][:-1])))
                referenced.add(bits[0])
            assert actual == expected, (source, actual, expected)
            assert a.get("sizes"), ("No sizes", source)
            assert a.get("width") and a.get("height"), ("No reserved geometry", source)
    assert count >= 100, ("Too few responsive page images", count)
    for src in referenced:
        assert (DIST / src.lstrip("/")).is_file(), ("Missing derived image", src)

    # Simulate an owner updating a source image. Never reinstate stale metadata.
    os.environ["XUYI_RESPONSIVE_MANIFEST"] = str(MANIFEST)
    sample = next(iter(manifest))
    markup = f'<img src="{sample}" alt="Owner ALT" loading="lazy">'
    enhanced = enhance_source_markup(markup)
    assert f'src="{sample}"' in enhanced and 'alt="Owner ALT"' in enhanced
    assert "srcset=" in enhanced
    owner_image = '<img src="/media/product/owner-updated-20261020.webp" alt="Owner update">'
    assert enhance_source_markup(owner_image) == owner_image
    authored = f'<img src="{sample}" alt="Owner" width="400" height="300" srcset="/assets/owner-480.webp 480w" sizes="100vw">'
    retained = enhance_source_markup(authored)
    assert retained == authored, ("Owner dimensions/srcset changed", retained)
    assert enhance_source_markup(enhanced) == enhanced, "Renderer must be idempotent"
    js = (ROOT / "assets/site.js").read_text(encoding="utf8")
    assert "img.removeAttribute('srcset')" in js
    assert "large.removeAttribute('srcset')" in js
    for original in LEGACY_REPLACED_SOURCES:
        expected = f'<img src="{original}" alt="Approved picture">'
        assert enhance_source_markup(expected) == expected, (
            "Historical approved image replacement would leave a stale srcset", original
        )
    print("XUYI_RESPONSIVE_RELEASE_OK", pages, "pages", count,
          "source-rendered image refs", len(referenced), "referenced variants",
          len(manifest), "sources")


if __name__ == "__main__":
    main()
