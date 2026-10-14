#!/usr/bin/env python3
"""Publish gate: complete SKU/locale overseas size classes and truthful metadata."""
from collections import Counter
from html import unescape
from pathlib import Path
import json,re,sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from source_catalog_capacity_oz import (
    SERIES,LOCALES,MILLILITERS_PER_US_FL_OZ,RETAIL_SIZES,
    MARKET_CLASS_MAX_DIFFERENCE,volume_terms,format_oz,catalog_volume_numbers,
    NO_CAPACITY_META_DIGESTS
)

DIST=ROOT/"dist"
models=list(SERIES.values())
known={n for row in models for n in catalog_volume_numbers(row)}
assert set(RETAIL_SIZES)==known,(sorted(set(RETAIL_SIZES)-known),sorted(known-set(RETAIL_SIZES)))
assert len(known)==23,known
for ml,row in RETAIL_SIZES.items():
    assert row["kind"] in ("class","approx"),(ml,row)
    diff=abs(row["oz"]*MILLILITERS_PER_US_FL_OZ-ml)/ml
    assert diff<=MARKET_CLASS_MAX_DIFFERENCE,(ml,row,diff)
assert RETAIL_SIZES[1000]["oz"]==32
assert RETAIL_SIZES[800]["oz"]==28
assert RETAIL_SIZES[1200]["oz"]==40
assert RETAIL_SIZES[2000]["oz"]==64
assert RETAIL_SIZES[3800]["oz"]==128
assert RETAIL_SIZES[500]["oz"]==16.9

by_locale=Counter()
titles={lang:set() for lang in LOCALES}
total=with_sizes=unknown=0
for row in models:
    slug=row["slug"]
    numbers=catalog_volume_numbers(row)
    for lang in LOCALES:
        pfx="" if lang=="en" else lang+"/"
        path=DIST/pfx/"products"/slug/"index.html"
        assert path.is_file(),path
        page=path.read_text(encoding="utf8")
        head,main=page.split("</head>",1)
        title=unescape(re.search(r"<title>([^<]+)</title>",head).group(1))
        desc=unescape(re.search(r'<meta name="description" content="([^"]+)"',head).group(1))
        assert title not in titles[lang],(lang,slug,"duplicate SEO title")
        titles[lang].add(title)
        assert "Tritan" in desc and "BPA" in desc,(lang,slug,"missing requested conditional SEO")
        assert len(desc)<=180,(lang,slug,"overlong meta",len(desc))
        assert not re.search(r'(?i)\bcertified BPA.free\b|\bmade (of|from) tritan\b',desc),(lang,slug)
        assert "Tritan" in main and "BPA" in main,(lang,slug,"no buyer material inquiry")
        assert page.count('class="product-custom-material-options"')==1,(lang,slug)
        canonical=re.search(r'<link rel="canonical" href="([^"]+)"',head)
        assert canonical and canonical.group(1)=="https://xuyibottles.com/"+pfx+"products/"+slug+"/",(lang,slug)
        assert title.count("XUYI")>=1,(lang,slug)
        if numbers:
            with_sizes+=1
            expected=volume_terms(numbers,lang)
            assert expected in main,(lang,slug,expected,"missing exact source ml paired to common size")
            assert page.count('class="product-capacity-summary"')==1,(lang,slug)
            assert page.count('class="product-capacity-disclaimer"')==1,(lang,slug)
            assert "oz" in title,(lang,slug,title)
            assert "oz" in desc,(lang,slug,desc)
            for num in numbers:
                assert format_oz(num,lang) in main,(lang,slug,num)
            # No legacy 1000ml=34oz marketing or old arithmetic fallback
            assert not re.search(r'(?i)1000\s*ml.{0,20}34\s*(?:fl\s*)?oz',page),(lang,slug)
            assert not re.search(r'(?i)800\s*ml.{0,20}27\s*(?:fl\s*)?oz',page),(lang,slug)
            assert not re.search(r'(?i)2000\s*ml.{0,20}68\s*(?:fl\s*)?oz',page),(lang,slug)
        else:
            unknown+=1
            assert page.count('class="product-capacity-summary"')==0,(lang,slug)
            assert "oz" not in title+" "+desc,(lang,slug,"invented volume")
            assert "Tritan" in desc,(lang,slug,"unknown model missing inquiry")
            assert slug in NO_CAPACITY_META_DIGESTS,(lang,slug,"source SEO review missing")
        total+=1;by_locale[lang]+=1
assert with_sizes==460 and unknown==45,(with_sizes,unknown)
assert total==505 and all(n==101 for n in by_locale.values()),by_locale
# The source still carries exact catalogue millilitres and factory model identity.
assert catalog_volume_numbers(SERIES["5247"])==(450.0,700.0)
assert catalog_volume_numbers(SERIES["5248"])==(450.0,700.0)
assert catalog_volume_numbers(SERIES["2506"])==()
assert all(catalog_volume_numbers(SERIES[k])==() for k in SERIES if str(k).startswith("G-"))
css=(DIST/"assets/site.css").read_text(encoding="utf8")
assert "body:has(#xuyi-home-banners)" in css
assert ".product-capacity-disclaimer" in css
print("XUYI_MARKET_OZ_ALL_23_SIZE_CLASSES_92_MODELS_505_PAGES_5_LOCALES_45_UNKNOWNS_CANONICAL_META_PASSED")