#!/usr/bin/env python3
"""2026-11-07 B2B publication sources: strict shape, distinct media, real links."""
import hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
DAY="20261107"
posts=[json.loads((ROOT/f"data/blog-guides-{DAY}-{i}.json").read_text(encoding="utf8")) for i in (1,2,3)]
trans=[json.loads((ROOT/f"data/blog-localized-copy-{DAY}-{i}.json").read_text(encoding="utf8")) for i in (1,2,3)]
covers=json.loads((ROOT/f"data/blog-images-reviewed-{DAY}.json").read_text(encoding="utf8"))["images"]
assert len(posts)==len(covers)==3
assert len({p["slug"] for p in posts})==3
assert len({c["sha256"] for c in covers})==3
for post,copy in zip(posts,trans):
 assert post["updated"]=="2026-11-07"
 assert len(post["sections"])==7 and all(len(x["paragraph"])>=650 for x in post["sections"])
 assert len(post["checklist"])==10 and len(post["faqs"])==4 and len(post["product_notes"])==3
 assert len({n["sku"] for n in post["product_notes"]})==3
 assert len(post["related"])==len(set(post["related"]))==3 and post["slug"] not in post["related"]
 assert set(copy)=={"es","pt","ru","tr"}
 for loc,row in copy.items():
  assert len(row["sections"])==7 and all(len(s[1])>230 for s in row["sections"])
  assert len(row["checklist"])==10 and len(row["faqs"])==4
  assert len(row["matrix"]["rows"])==6 and len(row["inline"])==2
  for note in post["product_notes"]:
   assert note["text"][loc].count("{product}")==1
 cover=next(c for c in covers if c["slug"]==post["slug"])
 path=ROOT/cover["source"]
 assert post["cover"]==cover["cover"]
 assert path.exists()
 buf=path.read_bytes()
 assert 30000<=len(buf)<=350000
 assert hashlib.sha256(buf).hexdigest()==cover["sha256"]
 with Image.open(path) as image:
  assert image.format=="WEBP" and image.size==(1200,800)
print("XUYI_20261107_THREE_B2B_POST_SOURCES_FIVE_LOCALES_AND_MEDIA_PASS")