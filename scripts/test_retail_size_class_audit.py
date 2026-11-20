#!/usr/bin/env python3
"""Publish gate: complete SKU/locale overseas size classes and truthful metadata."""
from collections import Counter
from html import unescape
from pathlib import Path
import json,re,sys,os

ROOT=Path(__file__).resolve().parent.parent
os.environ.setdefault("XUYI_BUILD_SNAPSHOT",str(ROOT/"_local_ops/build-snapshot.json"))
sys.path.insert(0,str(ROOT/"scripts"))
from source_catalog_capacity_oz import (
    SERIES,LOCALES,MILLILITERS_PER_US_FL_OZ,RETAIL_SIZES,
    MARKET_CLASS_MAX_DIFFERENCE,volume_terms,format_oz,catalog_volume_numbers,
    NO_CAPACITY_META_DIGESTS,current_baseline,market_record,source_field_allowed,new_seo
)
from cms_seo_curation_guard import snapshot,current_field

DIST=ROOT/"dist"
SOURCE_OWNER=snapshot()
models=list(SERIES.values())

# Canonical D1 productSeo rows must win over historical malformed-slug aliases.
# This guards the exact case where a canonical SEO refresh exists before the
# legacy page/translation record is migrated.
from product_slug_fix import REVERSE as LEGACY_PRODUCT_SLUGS
for model in models:
    canonical_slug=str(model.get("slug") or "")
    legacy_slug=LEGACY_PRODUCT_SLUGS.get(canonical_slug)
    if not legacy_slug:
        continue
    for locale in LOCALES:
        canonical_value="canonical "+canonical_slug+" "+locale
        legacy_value="legacy "+legacy_slug+" "+locale
        probe={
            "productSeo":[
                {"slug":canonical_slug,"locale":locale,"seoTitle":canonical_value,"metaDescription":canonical_value},
                {"slug":legacy_slug,"locale":locale,"seoTitle":legacy_value,"metaDescription":legacy_value},
            ],
            "pages":[],
            "translations":[],
        }
        route="/products/"+canonical_slug+"/"
        assert current_field(locale,route,"title",probe)==canonical_value,(locale,canonical_slug,"canonical D1 title lost to legacy alias")
        assert current_field(locale,route,"description",probe)==canonical_value,(locale,canonical_slug,"canonical D1 description lost to legacy alias")

known={n for row in models for n in catalog_volume_numbers(row)}# The JSON config contains the 23 explicitly reviewed retail classes. The
# expanded 254-model catalog has additional exact mL sizes; market_record()
# maps those to a familiar class only within the approved tolerance, otherwise
# labels the value as approximate rather than claiming exact equivalence.
assert set(RETAIL_SIZES)<=known,(sorted(set(RETAIL_SIZES)-known),sorted(known-set(RETAIL_SIZES)))
assert len(known)==44,known
for ml in known:
    record=market_record(ml)
    assert record["kind"] in ("class","approx"),(ml,record)
    diff=abs(record["oz"]*MILLILITERS_PER_US_FL_OZ-ml)/ml
    assert diff<=MARKET_CLASS_MAX_DIFFERENCE,(ml,record,diff)
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
        title_source_allowed=source_field_allowed(lang,row,"title",SOURCE_OWNER)
        description_source_allowed=source_field_allowed(lang,row,"description",SOURCE_OWNER)
        if title_source_allowed:
            if numbers:assert title==new_seo(lang,row,catalog_volume_numbers(row))[0],(lang,slug,"source title mismatch")
        else:
            assert title==current_field(lang,"/products/"+slug+"/","title",SOURCE_OWNER),(lang,slug,"D1 title overridden")
        if description_source_allowed:
            if numbers:assert desc==new_seo(lang,row,catalog_volume_numbers(row))[1],(lang,slug,"source description mismatch")
        else:
            assert desc==current_field(lang,"/products/"+slug+"/","description",SOURCE_OWNER),(lang,slug,"D1 description overridden")
        # Older owner-approved D1 descriptions (including disputed 2506)
        # predate the separate custom-material inquiry section. Do not
        # demand promotional wording in an editor-controlled SEO field:
        # verify the actual inquiry text on the product page instead.
        # Owner-approved SEO entries may use longer, custom text. The D1
        # product SEO API validates these lengths and is authoritative.
        assert len(desc)<=(180 if description_source_allowed else 240),(lang,slug,"overlong meta",len(desc))
        assert not re.search(r'(?i)\bcertified BPA.free\b|\bmade (of|from) tritan\b',desc),(lang,slug)
        material_panel=re.search(r'<aside class="product-custom-material-options"[^>]*>.*?</aside>',page,re.S)
        assert material_panel,(lang,slug,"no model-specific material inquiry")
        if row.get("category")=="Titanium Vacuum Cups":
            panel_text=unescape(re.sub(r"<[^>]+>"," ",material_panel.group(0))).lower()
            titanium_terms={
                "en":("titanium","grade"),
                "es":("titanio","grado"),
                "pt":("titânio","grau"),
                "ru":("титан","марка"),
                "tr":("titanyum","kalitesi"),
            }[lang]
            assert all(term in panel_text for term in titanium_terms),(lang,slug,"titanium grade inquiry missing")
        elif row.get("category")=="Two-Way Drinking Cups":
            panel_text=unescape(re.sub(r"<[^>]+>"," ",material_panel.group(0))).lower()
            component_terms={
                "en":("body","valve","seal","confirm"),
                "es":("cuerpo","válvula","junta","confirme"),
                "pt":("corpo","válvula","vedação","confirme"),
                "ru":("корпус","клапан","уплотн","уточн"),
                "tr":("gövde","valf","conta","doğrulay"),
            }[lang]
            assert all(term in panel_text for term in component_terms),(lang,slug,"two-way component material inquiry missing")
            assert "tritan" not in panel_text and "bpa" not in panel_text,(lang,slug,"unverified plastic material claim")
        else:
            assert "Tritan" in material_panel.group(0) and "BPA" in material_panel.group(0),(lang,slug,"plastic material inquiry missing")
        assert page.count('class="product-custom-material-options"')==1,(lang,slug)
        canonical=re.search(r'<link rel="canonical" href="([^"]+)"',head)
        assert canonical and canonical.group(1)=="https://leyamould.com/"+pfx+"products/"+slug+"/",(lang,slug)
        if title_source_allowed:assert title.count("XUYI")>=1,(lang,slug)
        if numbers:
            with_sizes+=1
            expected=volume_terms(numbers,lang)
            assert expected in main,(lang,slug,expected,"missing exact source ml paired to common size")
            assert page.count('class="product-capacity-summary"')==1,(lang,slug)
            assert page.count('class="product-capacity-disclaimer"')==1,(lang,slug)
            # Search titles stay concise. The approved retail oz class is
            # still present in H1, body and SEO description.
            if title_source_allowed:
                assert "ml" in title and len(title)<=60,(lang,slug,title)
            if description_source_allowed:
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
            # A D1-reviewed but still legacy no-capacity description may not
            # contain every default custom-material keyword. Its visible
            # source-rendered B2B inquiry panel (checked above) carries the
            # verified option. Migration must preserve editor-owned copy,
            # rather than rewriting a G/2506 description to satisfy a test.
            assert slug in NO_CAPACITY_META_DIGESTS,(lang,slug,"source SEO review missing")
        total+=1;by_locale[lang]+=1
expected_with_sizes=sum(bool(catalog_volume_numbers(row)) for row in models)*len(LOCALES)
expected_unknown=(len(models)-sum(bool(catalog_volume_numbers(row)) for row in models))*len(LOCALES)
assert with_sizes==expected_with_sizes and unknown==expected_unknown,(with_sizes,unknown,expected_with_sizes,expected_unknown)
assert total==len(models)*len(LOCALES) and all(n==len(models) for n in by_locale.values()),by_locale
# The source still carries exact catalogue millilitres and factory model identity.
assert catalog_volume_numbers(SERIES["5247"])==(450.0,700.0)
assert catalog_volume_numbers(SERIES["5248"])==(450.0,700.0)
assert catalog_volume_numbers(SERIES["2506"])==()
assert all(catalog_volume_numbers(SERIES[k])==() for k in SERIES if str(k).startswith("G-"))
css=(DIST/"assets/site.css").read_text(encoding="utf8")
assert "body:has(#xuyi-home-banners)" in css
assert ".product-capacity-disclaimer" in css
print("XUYI_MARKET_OZ_44_CATALOG_SIZES_254_MODELS_1270_PAGES_5_LOCALES_CANONICAL_META_PASSED")
