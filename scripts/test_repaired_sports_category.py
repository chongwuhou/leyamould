#!/usr/bin/env python3
"""No false use of original factory-photo slide for sports card visuals."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent.parent
NEW="/assets/editorial/sports-plastic-bottle.webp"
OLD="/media/ppt/slide-059.webp"
count=0
for file in (ROOT/"dist").rglob("index.html"):
    html=file.read_text(encoding="utf8")
    for m in re.finditer(
      r'<a class="category" href="/(?:es/|pt/|ru/|tr/)?collections/sports-water-bottles/">'
      r'<div class="category__photo"><img src="([^"]+)"',html):
        assert m.group(1)!=OLD,("Factory picture incorrectly shown as sports bottle",str(file))
        assert m.group(1)==NEW,(file,m.group(1))
        count+=1
assert count==50,("Reviewed sports cards incl. earlier 5 everyday-hydration",count)
assert (ROOT/"dist"/NEW.lstrip("/")).is_file()
for file in (ROOT/"dist").glob("**/products/*/index.html"):
    assert NEW not in file.read_text(encoding="utf8"),("SKU photo replaced",str(file))
print("XUYI_SPORTS_CATEGORY_IMAGE_SCOPE_PASSED",count,"cards, factory photos not globally overwritten")