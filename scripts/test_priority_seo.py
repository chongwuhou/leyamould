#!/usr/bin/env python3
"""Regression for manually curated four-route, five-language metadata."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from polish_priority_seo import PRIORITY
from cms_seo_curation_guard import may_curate,current_field
from html import unescape
import re
ROOT=Path(__file__).resolve().parent.parent
count=0
for route,langs in PRIORITY.items():
    assert set(langs)=={"en","es","pt","ru","tr"},route
    for locale,(title,description) in langs.items():
        prefix="" if locale=="en" else locale+"/"
        file=ROOT/"dist"/prefix/route.lstrip("/")/"index.html"
        source=file.read_text(encoding="utf8")
        head=source.split("</head>",1)[0]
        def get(regex):
            m=re.search(regex,head)
            assert m,(locale,route,regex)
            return unescape(m.group(1))
        if not (may_curate(locale,route,"title") and may_curate(locale,route,"description")):
            title=current_field(locale,route,"title")
            description=current_field(locale,route,"description")
        assert get(r"<title>([^<]+)</title>")==title,(locale,route)
        assert get(r'<meta name="description" content="([^"]*)"')==description,(locale,route)
        assert get(r'<meta property="og:title" content="([^"]*)"')==title,(locale,route)
        assert get(r'<meta property="og:description" content="([^"]*)"')==description,(locale,route)
        count+=1
assert count==20,count
print("XUYI_PRIORITY_SEO_CURATED_20_ROUTES_PASSED")