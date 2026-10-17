#!/usr/bin/env python3
"""Regression guard: revised Oct-17 covers, native clarity, and CMS edit precedence."""
from pathlib import Path
import json,sqlite3,re,struct,sys
ROOT=Path(__file__).resolve().parent.parent
GUIDES={g["slug"]:g for g in json.loads((ROOT/"data/blog-guides.json").read_text(encoding="utf8"))}
REPLACEMENTS={
 "water-bottle-sample-approval-checklist":("water-bottle-sample-approval-20261017.webp","water-bottle-sample-approval-photo-20261017.webp"),
 "water-bottle-capacity-sizes-wholesale":("water-bottle-capacity-guide-20261017.webp","water-bottle-capacity-comparison-photo-20261017.webp"),
 "replacement-water-bottle-lids-bulk":("replacement-water-bottle-lids-20261017.webp","replacement-water-bottle-lid-parts-photo-20261017.webp"),
}
new_names=[x[1] for x in REPLACEMENTS.values()]
assert len(set(new_names))==3
for slug,(old,new) in REPLACEMENTS.items():
 expected="/assets/blog/"+new
 assert GUIDES[slug]["cover"]==expected,(slug,GUIDES[slug]["cover"])
 art=ROOT/"assets/blog"/new;built=ROOT/"dist/assets/blog"/new
 assert art.is_file() and built.is_file(),slug
 assert art.read_bytes()==built.read_bytes(),slug
 # Read the VP8X/VP8 or VP8L dimensions with Pillow when available, without
 # resizing or any post-build image mutation.
 try:
  from PIL import Image
  with Image.open(art) as image:
   assert image.format=="WEBP" and image.size==(1512,1040),(slug,image.size)
 except ImportError:
  assert art.read_bytes()[:4]==b"RIFF" and art.read_bytes()[8:12]==b"WEBP"
 for locale in ("en","es","pt","ru","tr"):
  prefix="" if locale=="en" else locale+"/"
  blog=ROOT/"dist"/prefix/"blog"/slug/"index.html"
  index=ROOT/"dist"/prefix/"blog/index.html"
  for file in (blog,index):
   html=file.read_text(encoding="utf8")
   assert expected in html,(slug,locale,file)
   assert old not in html,(slug,locale,"old cover reintroduced")
  document=blog.read_text(encoding="utf8")
  assert '<meta property="og:image" content="https://xuyibottles.com'+expected+'"' in document,(slug,locale)
# Simulate an owner changing the cover in D1 before a historical maintenance
# patch: an exact old-value guard must not override that administrator edit.
db=sqlite3.connect(":memory:")
db.execute("CREATE TABLE xuyi_blog_posts(slug TEXT PRIMARY KEY,content_json TEXT)")
for slug,(old,new) in REPLACEMENTS.items():
 db.execute("INSERT INTO xuyi_blog_posts VALUES (?,?)",(slug,json.dumps({"cover":"/uploads/owner-replaced.webp"})))
 db.execute("UPDATE xuyi_blog_posts SET content_json=json_set(content_json,'$.cover',?) WHERE slug=? AND json_extract(content_json,'$.cover')=?",
             ("/assets/blog/"+new,slug,"/assets/blog/"+old))
 result=db.execute("SELECT json_extract(content_json,'$.cover') FROM xuyi_blog_posts WHERE slug=?",(slug,)).fetchone()[0]
 assert result=="/uploads/owner-replaced.webp",(slug,result)
print("BLOG_20261017_THREE_NATIVE_RESOLUTION_COVERS_AND_CMS_OWNER_PRIORITY_PASS")
