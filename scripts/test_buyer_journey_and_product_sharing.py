#!/usr/bin/env python3
"""Five-language buyer paths, orphan checks and authentic product share images."""
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from buyer_journey_internal_links import PATHWAYS, LOCALES, TEXT
from product_share_images import ORIGIN

DIST = ROOT / "dist"
pages = {
    "/" + file.relative_to(DIST).as_posix().removesuffix("index.html"): file
    for file in DIST.rglob("index.html")
    if file.relative_to(DIST).as_posix() != "admin/index.html"
}
assert len(pages) >= 755, ("Published page baseline shrank",len(pages))


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.inbound = []

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        self.tags.append(tag)
        if tag == "a" and fields.get("href"):
            self.inbound.append((fields["href"], tuple(self.tags)))

    def handle_endtag(self, tag):
        for index in range(len(self.tags) - 1, -1, -1):
            if self.tags[index] == tag:
                self.tags = self.tags[:index]
                break


body_sources = defaultdict(set)
for route, file in pages.items():
    markup = file.read_text(encoding="utf-8")
    links = Links()
    links.feed(markup)
    for url, tags in links.inbound:
        if not url.startswith("/") or url.startswith("//"):
            continue
        destination = urlsplit(url).path
        if destination not in pages or destination == route:
            continue
        if "main" in tags and not any(x in tags for x in ("nav", "header", "footer")):
            body_sources[destination].add(route)

snapshot=json.loads((ROOT/"_local_ops/build-snapshot.json").read_text(encoding="utf-8"))
dynamic_blog_routes={
    "/blog/"+str(post.get("slug"))+"/"
    for post in snapshot.get("blogPosts",[])
    if post.get("status")=="published" and post.get("slug")
}
# Published D1 article details may also have reviewed locale overrides. Their
# inbound contextual route is the CMS-owned locale Blog index, so treat those
# locale details exactly like their English D1 source route instead of
# requiring a second hard-coded body link from another static page.
published_blog_slugs={
    str(post.get("slug"))
    for post in snapshot.get("blogPosts",[])
    if post.get("status")=="published" and post.get("slug")
}
for row in snapshot.get("translations",[]):
    resource=str(row.get("resourceId") or "")
    locale=str(row.get("locale") or "")
    match=re.fullmatch(r"page:/blog/([^/]+)/",resource)
    if match and locale in {"es","pt","ru","tr"} and match.group(1) in published_blog_slugs:
        dynamic_blog_routes.add("/"+locale+"/blog/"+match.group(1)+"/")
runtime=(ROOT/"functions/blog/[[path]].js").read_text(encoding="utf-8")
assert 'listBlogPosts(db,"published")' in runtime and "posts.map(blogCard)" in runtime
# D1-only articles are linked by the live CMS-owned /blog/ listing, not the
# immutable static index. Do not misclassify their static shells as orphans.
missing=sorted(route for route in pages if not body_sources[route] and route not in dynamic_blog_routes)
assert not missing, ("Pages without contextual internal links", missing[:20])

count = 0
for lang in LOCALES:
    prefix = "" if lang == "en" else lang + "/"
    for source, targets in PATHWAYS.items():
        file = DIST / prefix / source / "index.html"
        markup = file.read_text(encoding="utf-8")
        if 'class="section buyer-pathways"' in markup:
            assert markup.count('class="section buyer-pathways"') == 1, (lang,source)
        main=markup.split("<main",1)[-1].split("</main>",1)[0]
        for target in targets:
            # The three new D1 buyer-guide targets currently exist in English
            # only. They receive inbound links from English sources; never
            # create broken locale-prefixed URLs for untranslated posts.
            if target.startswith("blog/") and lang!="en":
                assert 'href="/'+target+'/"' not in main,(lang,source,target,"unexpected cross-language link")
                continue
            target_prefix = "" if lang=="en" or target.startswith("blog/") else prefix
            destination = "/" + target_prefix + target + "/"
            assert main.count('href="' + destination + '"') == 1,(lang,source,target,"duplicate or missing link")
            assert "/" + prefix + source + "/" in body_sources[destination], (lang, target)
            count += 1
assert count >= 75, ("Approved contextual link baseline shrank",count)

product_count = 0
for route, file in pages.items():
    if not re.fullmatch(r"/(?:(?:es|pt|ru|tr)/)?products/[^/]+/", route):
        continue
    html = file.read_text(encoding="utf-8")
    head = html.split("</head>", 1)[0]
    product_nodes = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', head, re.S):
        data = json.loads(raw)
        product_nodes.extend(item for item in data.get("@graph", [data]) if item.get("@type") == "Product")
    assert len(product_nodes) == 1, route
    original_images = product_nodes[0].get("image", [])
    if isinstance(original_images, str):original_images=[original_images]
    assert all(x.startswith(ORIGIN+"/") and "/excel/" not in x
               for x in original_images),route
    # The D1 editor may select a different product sharing image. A custom
    # OG/Twitter image is authoritative; validate uniqueness and safe URLs,
    # rather than forcing it to equal the old JSON-LD catalog photo.
    previews=[]
    for pat in (
        r'<meta property="og:image" content="([^"]+)"',
        r'<meta name="twitter:image" content="([^"]+)"',
    ):
        matches=re.findall(pat, head)
        assert len(matches)<=1, (route,"duplicate social image",matches)
        assert all(url.startswith(ORIGIN + "/") for url in matches), (route,"invalid social image",matches)
        previews.extend(matches)
    assert previews, (route,"No social image was provided")
    assert all("/excel/" not in value for value in previews),route
    product_count += 1
assert product_count >= 505, ("Published product baseline shrank",product_count)
print("XUYI_BUYER_CONTEXT_LINKS_75_ZERO_ORPHANS_AND_PRODUCT_OG",product_count,"PASSED")

