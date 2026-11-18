#!/usr/bin/env python3
"""Regression: future dated B2B articles must automatically create real routes."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from blog_catalog_source import load_guides
from site_renderer import ROOT,BLOG_POSTS,ARTICLES,BUILD_STATE,render_d1_blog_index
from blog_editorial import GUIDES,BUYER_MATRICES
from build import blog_index,blog_index_rows
from sitemap_modification import source_lastmod

expected={
 "homeware-store-reusable-water-bottles-wholesale",
 "tennis-club-team-water-bottles-bulk-buying",
 "functional-training-gym-member-bottles-wholesale"
}
assert expected.issubset(BLOG_POSTS)
assert expected.issubset(GUIDES)
assert expected.issubset(BUYER_MATRICES)
assert set(BLOG_POSTS)==set(GUIDES)==set(BUYER_MATRICES)
assert len(ARTICLES)==len(BLOG_POSTS)
body=blog_index()
for slug in expected:
 assert '/blog/'+slug+'/' in body
 assert source_lastmod("/blog/"+slug+"/")=="2026-11-01",slug
 assert source_lastmod("/pt/blog/"+slug+"/")=="2026-11-01",slug
# A static build with a live D1 snapshot must render the full published D1
# catalogue, including CMS-only articles not yet in the source registry.
static_slug=ARTICLES[0][0]
static_post=BLOG_POSTS[static_slug]
previous=BUILD_STATE.get("blogPosts")
BUILD_STATE["blogPosts"]=[
 {"slug":"cms-only-published-guide","status":"published",
  "title":"CMS-only published buyer guide","description":"A complete CMS article description for the catalogue regression.",
  "cover":"/media/blog/cms-only-published-guide.webp","group":"BUYER RESOURCES"},
 {"slug":static_slug,"status":"published","title":static_post["title"],
  "description":static_post["description"],"cover":static_post["cover"],"group":static_post["group"]}
]
rows=blog_index_rows()
assert [row["slug"] for row in rows[:2]]==["cms-only-published-guide",static_slug]
assert len({row["slug"] for row in rows})==len(rows)
assert len(rows)==len(ARTICLES)+1

# Owner-edited D1 page bodies may use a different wrapper. The renderer must
# still inject every published D1 card without replacing the owner content.
owner_body='<section class="owner-copy"><p>Owner-managed introduction.</p></section>'
owner_rendered=render_d1_blog_index(owner_body)
assert "Owner-managed introduction." in owner_rendered
assert owner_rendered.count('class="news-card"')==len(BUILD_STATE["blogPosts"])

legacy_body='<div class="owner-cards"><article class="news-card">stale card</article></div>'
legacy_rendered=render_d1_blog_index(legacy_body)
assert legacy_rendered.count('class="news-card"')==len(BUILD_STATE["blogPosts"])
assert "stale card" not in legacy_rendered

if previous is None:BUILD_STATE.pop("blogPosts",None)
else:BUILD_STATE["blogPosts"]=previous
with TemporaryDirectory() as tmp:
 root=Path(tmp);data=root/"data";data.mkdir()
 base={"slug":"baseline","title":"Baseline title","description":"A validated source"}
 future={"slug":"new-future-topic","title":"New future buyer title","description":"A future approved source"}
 (data/"blog-guides.json").write_text(json.dumps([base]),encoding="utf8")
 (data/"blog-guides-20261102-1.json").write_text(json.dumps(future),encoding="utf8")
 (data/"blog-guides-20261102-not-approved.json").write_text("invalid",encoding="utf8")
 (data/"blog-scheduled-draft.json").write_text(json.dumps({"slug":"scheduled-draft","title":"Scheduled draft","description":"Must stay out of the static catalog until D1 publishes it."}),encoding="utf8")
 assert [p["slug"] for p in load_guides(root)]==["baseline","new-future-topic"],"D1-scheduled drafts must not leak into the static public Blog catalogue"
 (data/"blog-guides-20261102-2.json").write_text(json.dumps(future),encoding="utf8")
 try:
  load_guides(root)
 except ValueError as exc:
  assert "Duplicate Blog slug" in str(exc)
 else:
  raise AssertionError("Duplicate future slug not rejected")
print("XUYI_BLOG_SOURCE_DYNAMIC_GROWTH_OK",len(BLOG_POSTS),"articles; 3 20261101 routes and future additions validated")

