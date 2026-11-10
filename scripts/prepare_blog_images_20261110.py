#!/usr/bin/env python3
"""Create the three 2026-11-10 reviewed Blog covers from unused source artwork.

The source images are existing XUYI editorial assets that were not assigned to
an earlier Blog cover. They are resized in the source tree before the R2 upload;
the result is an illustrative procurement visual, not a product or factory
claim.
"""
from hashlib import sha256
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SOURCES = (
    ("assets/blog/bottle-inspection-topics-20261013.webp", "assets/blog/plastic-water-bottle-quality-inspection-20261110.webp"),
    ("assets/blog/bottle-factory-rfq-template-20261016.webp", "assets/blog/wholesale-water-bottle-rfq-20261110.webp"),
    ("assets/blog/export-packing-topics-20261013.webp", "assets/blog/custom-water-bottle-export-packing-20261110.webp"),
)


def main():
    hashes = []
    for source, target in SOURCES:
        src, dest = ROOT / source, ROOT / target
        if not src.is_file() or src.stat().st_size < 30000:
            raise RuntimeError(f"Missing or undersized approved source: {src}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as original:
            image = ImageOps.fit(original.convert("RGB"), (1200, 800), Image.Resampling.LANCZOS)
            image.save(dest, "WEBP", quality=92, method=6)
        with Image.open(dest) as checked:
            if checked.format != "WEBP" or checked.size != (1200, 800):
                raise RuntimeError(f"Cover format or dimensions invalid: {dest}")
        if not 30000 <= dest.stat().st_size <= 350000:
            raise RuntimeError(f"Cover outside approved size range: {dest}")
        digest = sha256(dest.read_bytes()).hexdigest()
        hashes.append(digest)
        print("XUYI_20261110_COVER_READY", dest.name, dest.stat().st_size, digest)
    if len(set(hashes)) != 3:
        raise RuntimeError("Each 2026-11-10 article requires a distinct cover")


if __name__ == "__main__":
    main()