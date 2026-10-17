#!/usr/bin/env python3
"""Keep workshop photography out of generic sports-bottle category cards.

The original PPT slide-059 is a factory/press photo. It must not be used as
the image for a link explicitly labelled Sports Water Bottles.
This reuses a previously reviewed generic plastic-sports-bottle image.
Only a category card image tag is edited. SKU product photos, factory
photos on legitimate manufacturing pages, and all model data stay intact.
"""
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
OLD="/media/ppt/slide-059.webp"
NEW="/assets/editorial/sports-plastic-bottle.webp"
PATTERN=re.compile(
 r'(<a class="category" href="/(?:es/|pt/|ru/|tr/)?collections/sports-water-bottles/">'
 r'<div class="category__photo"><img src=")'+re.escape(OLD)+r'(")'
)


def apply(dist):
    dist=Path(dist)
    if not (dist/NEW.lstrip("/")).is_file():
        raise FileNotFoundError("Missing reviewed sports image "+NEW)
    changed=0
    for f in dist.rglob("index.html"):
        html=f.read_text(encoding="utf-8")
        replaced,count=PATTERN.subn(lambda m:m.group(1)+NEW+m.group(2),html)
        if count:
            f.write_text(replaced,encoding="utf-8")
            changed+=count
    print("XUYI_SPORTS_CARD_FACTORY_PHOTO_MISMATCH_FIXED",changed,
          "legacy image swaps; later CMS image replacements preserved")
    return changed


if __name__=="__main__":
    apply(ROOT/"dist")
