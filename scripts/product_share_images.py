#!/usr/bin/env python3
"""Use the exact reviewed Product JSON-LD photo for OG/Twitter sharing.

No invented products, availability, price, rating or image. Do not alter the
existing gallery, image file, canonical or page body.
"""
from pathlib import Path
import json
import re
import html

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "https://xuyibottles.com"


def apply(dist):
    dist = Path(dist)
    count = 0
    preserved = 0
    eligible = 0
    for file in sorted(dist.rglob("index.html")):
        relative = file.relative_to(dist).as_posix()
        if not re.fullmatch(r"(?:(?:es|pt|ru|tr)/)?products/[^/]+/index\.html", relative):
            continue
        eligible += 1
        source = file.read_text(encoding="utf-8")
        head, divider, body = source.partition("</head>")
        if not divider:
            raise ValueError("Product document missing head: " + relative)
        product = None
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', head, re.S):
            data = json.loads(raw)
            for node in data.get("@graph", [data]):
                if node.get("@type") == "Product":
                    if product is not None:
                        raise ValueError("Ambiguous Product JSON-LD: " + relative)
                    product = node
        if product is None:
            raise ValueError("Product JSON-LD missing: " + relative)
        images = product.get("image") or []
        image = images[0] if isinstance(images, list) and images else images if isinstance(images, str) else ""
        if not image.startswith(ORIGIN + "/"):
            raise ValueError("Unsafe or absent original Product image: " + relative)
        # CMS editor images always outrank historical auto-generated previews.
        # Re-running a release step must neither duplicate tags nor reject
        # an owner-selected OG/Twitter image.
        if (re.search(r'<meta\s+property="og:image"', head) or
                re.search(r'<meta\s+name="twitter:image"', head)):
            preserved += 1
            continue
        url = html.escape(image, quote=True)
        additions = (
            '<meta property="og:image" content="' + url + '">'
            '<meta name="twitter:card" content="summary_large_image">'
            '<meta name="twitter:image" content="' + url + '">'
        )
        file.write_text(head + additions + divider + body, encoding="utf-8")
        count += 1
    # The catalog may expand without altering this release rule.
    if eligible < 505:
        raise ValueError("Baseline published Product pages unexpectedly missing: " + str(eligible))
    print("XUYI_EXACT_PRODUCT_SHARE_IMAGES", count, "new;", preserved, "owner/existing previews preserved;", eligible, "product pages")
    return count


if __name__ == "__main__":
    apply(ROOT / "dist")
