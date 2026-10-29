#!/usr/bin/env python3
"""Deterministic XUYI-owned editorial photo crops for the three 2026-10-29 guides.

Generate in source assets before every release build, not post-process dist.
Photographs are generic category illustrations, never alleged exact-SKU photos.
"""
from pathlib import Path
from PIL import Image, ImageOps
from hashlib import sha256
ROOT = Path(__file__).resolve().parent.parent
SOURCES = (
    ("assets/curated-hd/outdoor-lifestyle.webp", "assets/blog/warehouse-staff-hydration-20261029.webp"),
    ("assets/curated-hd/customizable-assortment.webp", "assets/blog/airport-station-travel-retail-20261029.webp"),
    ("assets/curated-hd/gradient-sports.webp", "assets/blog/coworking-member-welcome-bottles-20261029.webp"),
)
def main():
    hashes = []
    for source, target in SOURCES:
        src = ROOT / source
        dest = ROOT / target
        assert src.is_file() and src.stat().st_size > 30000, src
        dest.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as original:
            assert original.width >= 1200 and original.height >= 1000
            photo = ImageOps.fit(original.convert("RGB"), (1200, 800), Image.Resampling.LANCZOS)
            photo.save(dest, "WEBP", quality=95, method=6)
            if dest.stat().st_size <= 30000:
                photo.save(dest, "WEBP", lossless=True, method=6)
        with Image.open(dest) as review:
            assert review.size == (1200, 800) and review.format == "WEBP"
        assert dest.stat().st_size > 30000, dest
        hashes.append(sha256(dest.read_bytes()).hexdigest())
    assert len(set(hashes)) == 3
    print("XUYI_20261029_THREE_DISTINCT_OWNED_COVER_PHOTOS_READY")
if __name__ == "__main__":
    main()