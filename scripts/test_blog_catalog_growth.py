#!/usr/bin/env python3
"""Regression: future dated B2B articles must automatically create real routes."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from blog_catalog_source import load_guides
from site_renderer import ROOT,BLOG_POSTS,ARTICLES
from blog_editorial import GUIDES,BUYER_MATRICES
from build import blog_index
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
with TemporaryDirectory() as tmp:
 root=Path(tmp);data=root/"data";data.mkdir()
 base={"slug":"baseline","title":"Baseline title","description":"A validated source"}
 future={"slug":"new-future-topic","title":"New future buyer title","description":"A future approved source"}
 (data/"blog-guides.json").write_text(json.dumps([base]),encoding="utf8")
 (data/"blog-guides-20261102-1.json").write_text(json.dumps(future),encoding="utf8")
 (data/"blog-guides-20261102-not-approved.json").write_text("invalid",encoding="utf8")
 (data/"blog-scheduled-20261103-1.json").write_text(json.dumps({"slug":"scheduled-draft","title":"Scheduled draft","description":"Must stay out of the static catalog until D1 publishes it."}),encoding="utf8")
 assert [p["slug"] for p in load_guides(root)]==["baseline","new-future-topic"],"D1-scheduled drafts must not leak into the static public Blog catalogue"
 (data/"blog-guides-20261102-2.json").write_text(json.dumps(future),encoding="utf8")
 try:
  load_guides(root)
 except ValueError as exc:
  assert "Duplicate Blog slug" in str(exc)
 else:
  raise AssertionError("Duplicate future slug not rejected")
print("XUYI_BLOG_SOURCE_DYNAMIC_GROWTH_OK",len(BLOG_POSTS),"articles; 3 20261101 routes and future additions validated")