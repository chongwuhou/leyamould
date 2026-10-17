#!/usr/bin/env python3
"""Reviewed photos must appear in all jug/kids category cards, not model pages."""
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from repair_remaining_category_cards import REPAIRS
DIST=ROOT/"dist"
counts={name:0 for name in REPAIRS}
for file in DIST.rglob("index.html"):
    document=file.read_text(encoding="utf-8")
    for name,(old,new) in REPAIRS.items():
        pattern=(r'<a class="category" href="/(?:es/|pt/|ru/|tr/)?collections/'
                 +re.escape(name)+r'/"><div class="category__photo"><img src="([^"]+)"')
        for match in re.finditer(pattern,document):
            assert match.group(1)==new,(str(file),name,match.group(1))
            counts[name]+=1
    if "/products/" in file.as_posix():
        main=document.split('<main id="main-content">',1)[-1].split("</main>",1)[0]
        assert all(new not in main for old,new in REPAIRS.values()),str(file)
assert counts=={name:50 for name in REPAIRS},counts
print("XUYI_REVIEWED_JUG_KIDS_CATEGORY_CARDS_PASSED",counts)
