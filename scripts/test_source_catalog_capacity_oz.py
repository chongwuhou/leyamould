#!/usr/bin/env python3
"""Five-language, all-model mL/US-fl-oz and safe custom materials release gate."""
from pathlib import Path
from tempfile import TemporaryDirectory
from html import unescape
from copy import deepcopy
import hashlib
import re
import shutil
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from source_catalog_capacity_oz import (
    MILLILITERS_PER_US_FL_OZ,LOCALES,catalog_volume_numbers,
    volume_terms,format_oz,current_baseline,enrich_detail,enrich_cards,
    new_seo,COPY
)
from cms_seo_curation_guard import snapshot
from site_renderer import SERIES

DIST=ROOT/"dist"
assert abs(MILLILITERS_PER_US_FL_OZ-29.5735295625)<1e-10
assert format_oz(500)=="16.9 oz class"
assert format_oz(750)=="24 oz class"
assert format_oz(800)=="28 oz class"
assert format_oz(1000)=="32 oz class"
assert format_oz(1200)=="40 oz class"
assert format_oz(2000)=="64 oz class"
assert format_oz(3800)=="128 oz class"
assert catalog_volume_numbers(SERIES["2506"])==()
assert catalog_volume_numbers({**SERIES["2506"],"capacity":"600ml"})==(600.0,)  # CMS correction works automatically
assert catalog_volume_numbers(SERIES["5247"])==(450.0,700.0)
assert catalog_volume_numbers(SERIES["5248"])==(450.0,700.0)
assert catalog_volume_numbers(SERIES["G-02"])==()

vol_models=0
volume_pages=0
custom_pages=0
for row in SERIES.values():
    numbers=catalog_volume_numbers(row)
    vol_models+=bool(numbers)
    for lang in LOCALES:
        prefix="" if lang=="en" else lang+"/"
        f=DIST/prefix/"products"/row["slug"]/"index.html"
        assert f.is_file(),f
        markup=f.read_text(encoding="utf8")
        head,main=markup.split("</head>",1)
        assert main.count('class="product-custom-material-options"')==1,(lang,row["model"])
        assert "Tritan" in main and ("BPA-free" in main or "BPA" in main),(lang,row["model"])
        assert "catalog" in main.lower() or "catálogo" in main.lower() or "каталога" in main.lower() or "Katalog" in main,(lang,row["model"])
        assert not re.search(r'(?i)\bcertified BPA.free\b|\bmade of Tritan\b',head),(lang,row["model"])
        if numbers:
            volume_pages+=1
            exact=volume_terms(numbers,lang)
            assert markup.count('class="product-capacity-summary"')==1,(lang,row["model"])
            assert exact in main,(lang,row["model"],exact)
            title=unescape(re.search(r"<title>([^<]+)</title>",head).group(1))
            desc=unescape(re.search(r'<meta name="description" content="([^"]+)"',head).group(1))
            assert "oz" in title and "oz" in desc,(lang,row["model"],title,desc)
            assert 'class="product-capacity-disclaimer"' in main,(lang,row["model"],"missing size-class caveat")
            assert "Tritan" in desc and "BPA" in desc,(lang,row["model"])
            assert len(title)<=75 and len(desc)<=180,(lang,row["model"],len(title),len(desc))
            for val in numbers:
                assert format_oz(val,lang) in markup,(lang,row["model"],val)
        else:
            assert 'class="product-capacity-summary"' not in markup,(lang,row["model"])
            if str(row["model"])=="2506":
                assert markup.count('class="product-capacity-warning"')==1,(lang,"2506 warning")
        custom_pages+=1

assert len(SERIES)>=101
assert vol_models==92,(vol_models,len(SERIES))
assert volume_pages==460,volume_pages
assert custom_pages==505,custom_pages

# 92 known-capacity model cards in each language; search index also learns
# US ounces and conditional custom-material buyer language.
for lang in LOCALES:
    prefix="" if lang=="en" else lang+"/"
    listing=(DIST/prefix/"products/index.html").read_text(encoding="utf8")
    for row in SERIES.values():
        slug=row["slug"]
        cards=re.findall(r'<a\b(?=[^>]*class="product-card\b)[^>]*\bhref="/'+
                         re.escape(prefix)+r'products/'+re.escape(slug)+
                         r'/".*?</a>',listing,re.S)
        assert len(cards)==1,(lang,slug,len(cards))
        volume=catalog_volume_numbers(row)
        if volume:
            assert cards[0].count('class="product-card__capacity"')==1,(lang,slug)
            assert volume_terms(volume,lang) in cards[0],(lang,slug,"capacity")
            assert "Tritan BPA-free material options" in cards[0],(lang,slug,"search terms")
        else:
            assert 'class="product-card__capacity"' not in cards[0],(lang,slug)

# Simulate a real owner overwriting only one of the two D1 fields. Old SEO
# suggestions may not rewrite EITHER of the fields in subsequent releases.
original=snapshot()
assert original and original["site"]=="xuyi-drinkware-site"
edited=deepcopy(original)
row=next(x for x in edited["pages"] if x.get("route")=="/products/2514/")
row["seo_title"]="OWNER TITLE 1000ml green bottle"
assert not current_baseline("en",SERIES["2514"],edited)
unmodified=deepcopy(original)
row=next(x for x in unmodified["translations"] if x.get("locale")=="es" and x.get("resourceId")=="page:/products/2514/")
row["content"]["description"]="OWNER EDITED description"
assert not current_baseline("es",SERIES["2514"],unmodified)
assert current_baseline("en",SERIES["2514"],original)
# Future source catalog entries: automatically suggest ml/oz SEO when no
# editor field exists, but back off when an owner later sets either field.
future={"slug":"future-source-1500","model":"F-1500", "capacity":"1500ml",
        "category":"Plastic Sports Water Bottles","name":"1500ml Plastic Sports Bottle"}
assert catalog_volume_numbers(future)==(1500.0,)
assert current_baseline("en",future,original)
assert "50 oz class" in new_seo("en",future,(1500.0,))[0]
future_with_owner=deepcopy(original)
future_with_owner["pages"].append({"route":"/products/future-source-1500/","seo_title":"Owner preferred title"})
assert not current_baseline("en",future,future_with_owner)

with TemporaryDirectory(prefix="xuyi-full-volumes-regression-") as td:
    temporary=Path(td)
    for lang,slug,override in [
        ("en","2514",edited),("es","2514",unmodified),("en","5247",original),
        ("ru","lo-001",original),("en","g-02",original),
    ]:
        prefix="" if lang=="en" else lang+"/"
        src=DIST/prefix/"products"/slug/"index.html"
        dst=temporary/prefix/"products"/slug/"index.html"
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst)
        markup=dst.read_text(encoding="utf8")
        # A CMS-owned custom SEO headline must stay untouched by the
        # historical curation, while source-backed capacity remains.
        if slug=="2514":
            modified=markup.replace("<title>","<title>OWNER VERIFIED ",1)
            dst.write_text(modified,encoding="utf8")
        original_bytes=dst.read_bytes()
        enrich_detail(dst,lang,next(r for r in SERIES.values() if r["slug"]==slug),override)
        assert dst.read_bytes()==original_bytes,(lang,slug,"not idempotent/owner meta changed")
    # Search card enrichment is similarly non-duplicating on a repeat pass.
    listing_src=DIST/"products/index.html"
    listing=temporary/"products/index.html"
    shutil.copy2(listing_src,listing)
    before=hashlib.sha256(listing.read_bytes()).hexdigest()
    assert enrich_cards(listing,{r["slug"]:r for r in SERIES.values()})==0
    assert hashlib.sha256(listing.read_bytes()).hexdigest()==before

print("XUYI_VOLUME_US_FL_OZ_92_MODELS_460_DETAILS_505_CUSTOM_CARDS_5_LANGUAGES_OWNER_TESTS_PASSED")