#!/usr/bin/env python3
"""Guard model identity and useful concise snippets; non-catalog pages untouched."""
from pathlib import Path
from html import unescape
import re
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES
from scripts.model_catalog_buyer_comparison import capacity_number
from scripts.curated_catalog_meta_clarity import LOCALES
from scripts.cms_seo_curation_guard import may_curate,current_field

DIST=ROOT/"dist"
catalog=[m for m in SERIES.values() if not m.get("manualNew")]
assert len(catalog)>=85
tested=0
for row in catalog:
    sku=str(row["model"]);cap=capacity_number(row)
    for lang in LOCALES:
        head=(DIST/lang/"products"/str(row["slug"])/"index.html").read_text(encoding="utf8").split("</head>",1)[0]
        title=unescape(re.search(r'<title>(.*?)</title>',head,re.S).group(1))
        desc=unescape(re.search(r'<meta name="description" content="([^"]*)"',head).group(1))
        # The legacy 2400 transparent variant deliberately localizes its
        # Chinese suffix in snippets while retaining the numeric factory ID.
        model_id=re.match(r"\d+",sku).group(0) if re.match(r"\d+",sku) else sku
        assert sku in title and (sku in desc or model_id in desc),(lang,sku,title,desc)
        route="/products/"+str(row["slug"])+"/"
        if may_curate(lang,route,"title"):
            assert len(title)<=70,(lang,sku,len(title))
        else:
            assert title==current_field(lang,route,"title"),(lang,sku,"CMS title not retained")
        if may_curate(lang,route,"description"):
            assert len(desc)<=180,(lang,sku,len(desc))
        else:
            assert desc==current_field(lang,route,"description"),(lang,sku,"CMS description not retained")
        assert "rel=\"canonical\"" in head and "hreflang=" in head
        assert not any(x in desc.lower() for x in ("in stock","certified","guaranteed","test passed"))
        tested+=1
assert tested==len(catalog)*len(LOCALES)
print("XUYI_LOCALIZED_CATALOG_META",tested,"PAGES_PASSED")