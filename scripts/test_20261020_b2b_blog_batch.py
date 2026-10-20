"""Editorial and source-of-truth regression for 2026-10-20 purchasing guides."""
import html
import json
import os
import re
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
SLUGS=[
 "how-to-vet-plastic-water-bottle-factory-bulk-order",
 "mixed-color-size-water-bottle-wholesale-order",
 "custom-water-bottle-deposit-checklist"
]
LOCALES=("en","es","pt","ru","tr")
POSTS=json.loads((ROOT/"data/blog-guides-20261020.json").read_text("utf8"))
TRANSLATIONS=json.loads((ROOT/"data/blog-localized-copy-20261020.json").read_text("utf8"))["articles"]

assert len(POSTS)==3 and [p["slug"] for p in POSTS]==SLUGS
baseline=json.loads((ROOT/"data/blog-guides.json").read_text("utf8"))
all_known={p["slug"] for p in baseline+POSTS}
assert len(all_known)==len(baseline)+3,"Duplicate slugs"
assert all(post["title"].endswith("?") for post in POSTS),"Question-form B2B search intent"
for post in POSTS:
 slug=post["slug"]
 assert len(post["sections"])==7 and len(post["checklist"])==10 and len(post["faqs"])==4
 assert len(post["related"])==3 and all(x in all_known and x!=slug for x in post["related"])
 assert len(post["product_notes"])==3
 linked=[str(n["sku"]) for n in post["product_notes"]]
 assert len(set(linked))==3
 for note in post["product_notes"]:
  assert 0<=note["section"]<len(post["sections"])
  assert (ROOT/"dist"/"products"/str(note["sku"])/"index.html").is_file()
  assert all(note["text"][loc].count("{product}")==1 for loc in LOCALES)
  assert all(len(note["label"][loc])>5 for loc in LOCALES)
 matrix=post["buyerDecisionTable"]
 assert len(matrix["rows"])==6 and len(matrix["links"])==3
 assert sum(len(section["paragraph"].split()) for section in post["sections"])>700
 assert "MOQ" not in post["intro"] or "minimum" in post["intro"].lower() or "minimum" in post["description"].lower()
 assert (ROOT/"dist"/"blog"/slug/"index.html").is_file()
 for loc in LOCALES:
  page=ROOT/"dist"/loc/"blog"/slug/"index.html" if loc!="en" else ROOT/"dist"/"blog"/slug/"index.html"
  assert page.is_file(),(loc,slug)
  markup=page.read_text("utf8")
  assert "<h1" in markup and 'rel="canonical"' in markup
  assert re.search(r'<meta name="description" content="[^"]{20,}',markup)
  assert "noindex" not in markup.lower()
  if loc=="en":
   for sku in linked:
    assert '/products/'+sku+'/' in markup,(slug,sku)
  else:
   for sku in linked:
    assert '/'+loc+'/products/'+sku+'/' in markup,(loc,slug,sku)
  # Exactly 3 independently curated related reads within the article itself.
  for target in post["related"]:
   target_url=("/"+loc if loc!="en" else "")+"/blog/"+target+"/"
   assert target_url in markup,(loc,slug,target_url)
  assert markup.count('class="blog-related__item"')>=3,(slug,loc,"related")
  if loc!="en":
   t=TRANSLATIONS[slug][loc]
   assert html.escape(t["title"],quote=True) in markup
   assert all(len(t[f"sections.{i}.paragraph"])>=150 for i in range(7))

payload_file=ROOT/"_local_ops/blog-batch-20261020/payload.json"
if payload_file.is_file():
 payload=json.loads(payload_file.read_text("utf8"))
 assert len(payload["posts"])==3 and len(payload["translations"])==12 and len(payload["indexCards"])==12
 for item in payload["translations"]:
  body=item["mainHtml"]
  assert body.count('class="blog-editorial__product-link"')==3
  assert body.count('class="blog-related__item"')==3
  assert body.count("<details>")==4
  assert body.count('class="blog-buyer-matrix"')==1
  assert len(body)>6500

# The API insert is add-only. A D1 editor's later changes MUST win on conflict,
# with no forced article/translation replacement.
api=(ROOT/"functions/api/admin/blog-batch-20261020.js").read_text("utf8")
assert "ON CONFLICT(slug) DO NOTHING" in api
assert "ON CONFLICT(resource_id,locale) DO NOTHING" in api
assert "instr(json_extract(translated_json,'$.mainHtml'),?)=0" in api
assert "authorizedReviewedBlogBatchRequest" in api
workflow=(ROOT/".github/workflows/publish-xuyi.yml").read_text("utf8")
assert "scripts/prepare_blog_release_20261020.py" in workflow
assert "scripts/publish_blog_batch_20261020_d1.py" in workflow
assert "github.event.head_commit.message == 'Publish reviewed 2026-10-20 B2B procurement guides'" in workflow
print("XUYI_20261020_B2B_EDITORIAL_SOURCE_CMS_POLICY_15_PAGES_PASSED")
