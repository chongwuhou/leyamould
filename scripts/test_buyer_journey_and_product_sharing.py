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

missing = sorted(route for route in pages if not body_sources[route])
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
            destination = "/" + prefix + target + "/"
            assert main.count('href="' + destination + '"') == 1,(lang,source,target,"duplicate or missing link")
            assert "/" + prefix + source + "/" in body_sources[destination], (lang, target)
            count += 1
assert count == 75, count

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
    original_images = product_nodes[0]["image"]
    expected = original_images[0] if isinstance(original_images, list) else original_images
    assert expected.startswith(ORIGIN + "/"), route
    for pat in (
        r'<meta property="og:image" content="([^"]+)"',
        r'<meta name="twitter:image" content="([^"]+)"',
    ):
        match = re.findall(pat, head)
        assert match == [expected], (route, pat, match, expected)
    assert '<meta name="twitter:card" content="summary_large_image">' in head
    product_count += 1
assert product_count >= 505, ("Published product baseline shrank",product_count)
print("XUYI_BUYER_CONTEXT_LINKS_75_ZERO_ORPHANS_AND_PRODUCT_OG",product_count,"PASSED")