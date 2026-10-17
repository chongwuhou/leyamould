#!/usr/bin/env python3
"""Validate the deployed R2 reference map across XUYI locales and JS assets."""
from pathlib import Path
import sys,json, tempfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from r2_usage_index import inventory
root=Path(__file__).resolve().parent.parent
dist=root/"dist"
file=dist/"r2-usage-index.json"
assert file.exists(),"Build must emit the release media usage index"
data=json.loads(file.read_text(encoding="utf8"))
assert data["site"]=="xuyi-drinkware-site" and data["schemaVersion"]==1
assert data["publishRevision"]>=0 and data["references"]
refs=data["references"]
assert "/media/ppt/slide-059.webp" in refs,"Older images used by source pages are protected"
# The homepage's duplicated packaging thumbnail has a new reviewed cover,
# but the original factory image must stay attached to its own buying guide.
assert "/blog/wholesale-plastic-water-bottle-buying-guide/" in refs["/media/ppt/slide-059.webp"]
assert "/ru/blog/wholesale-plastic-water-bottle-buying-guide/" in refs["/media/ppt/slide-059.webp"]
assert all(all("../" not in x for x in group) for group in refs.values())
with tempfile.TemporaryDirectory() as tmp:
 dest=Path(tmp)
 (dest/"index.html").write_text('<img src="/media/page/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.webp">',encoding="utf8")
 sub=dest/"es";sub.mkdir()
 (sub/"index.html").write_text('<img src="/media/page/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.webp">',encoding="utf8")
 result=inventory(dest)
 assert result["/media/page/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.webp"]==["/","/es/"]
print("XUYI_R2_USAGE_INDEX_PASSED",len(refs),"images across deployed pages; locales and mock verified")
