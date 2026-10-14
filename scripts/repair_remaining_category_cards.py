#!/usr/bin/env python3
"""Upgrade only shared jug/kids category cards; do not edit named SKU photos."""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REPAIRS={
 "large-capacity-water-jugs":("/media/ppt/slide-055.webp","/assets/editorial/large-capacity-plastic-jug.webp"),
 "kids-water-bottles":("/media/ppt/slide-030.webp","/assets/editorial/kids-plastic-bottle.webp")
}

def apply(dist):
    dist=Path(dist)
    results={}
    for category,(old,new) in REPAIRS.items():
        if not (dist/new.lstrip("/")).is_file():raise FileNotFoundError(new)
        pattern=re.compile(
            r'(<a class="category" href="/(?:es/|pt/|ru/|tr/)?collections/'
            +re.escape(category)+r'/"><div class="category__photo"><img src=")'
            +re.escape(old)+r'(")'
        )
        count=0
        for file in dist.rglob("index.html"):
            source=file.read_text(encoding="utf-8")
            changed,num=pattern.subn(lambda m:m.group(1)+new+m.group(2),source)
            if num:
                file.write_text(changed,encoding="utf-8")
                count+=num
        results[category]=count
    print("XUYI_VERIFIED_CATEGORY_UPGRADES",results,
          "legacy image swaps; later CMS images preserved")
    return results

if __name__=="__main__":apply(ROOT/"dist")