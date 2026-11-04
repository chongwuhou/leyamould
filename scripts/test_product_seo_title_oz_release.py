"""Regression: source-reviewed mL/approximate oz product titles across locales.

Never overwrite genuine owner-edited D1 SEO or claim disputed capacities.
Keep existing canonical URLs, translated H1, descriptions, OG title, hreflang
and Product SKU consistent without rewriting dist output after build.
"""
from html import unescape
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from site_renderer import SERIES
from cms_seo_curation_guard import snapshot
from source_catalog_capacity_oz import (
    LOCALES, catalog_volume_numbers, current_baseline, new_seo,
    format_ml, oz_number,
)
from sitemap_modification import source_lastmod

DATA = json.loads((ROOT / "data/product-seo-title-refresh-20261020.json").read_text("utf8"))
assert DATA["schemaVersion"] == 1
assert DATA["significantChangeDate"] == "2026-10-20"
approved = set(DATA["slugs"])
assert len(approved) == 92
NEW_FACTORY_SOURCES = {"puyunsm(1).pdf", "水杯最新产品.pptx"}
new_factory_capacity_slugs = {
    r["slug"] for r in SERIES.values()
    if r.get("sourceDocument") in NEW_FACTORY_SOURCES and catalog_volume_numbers(r)
}
baseline_capacity_slugs = {
    r["slug"] for r in SERIES.values()
    if r.get("sourceDocument") not in NEW_FACTORY_SOURCES and catalog_volume_numbers(r)
}
assert approved == baseline_capacity_slugs
assert source_lastmod("/products/2292/") == "2026-10-20"
assert source_lastmod("/pt/products/2292/") == "2026-10-20"
assert source_lastmod("/products/2506/") != "2026-10-20"
assert source_lastmod("/products/nonexistent/") is None

owner = snapshot()
total,eligible,with_sizes,no_sizes = 0,0,0,0
for loc in LOCALES:
    unique = set()
    for row in SERIES.values():
        rel = ("" if loc == "en" else loc + "/") + "products/" + row["slug"] + "/index.html"
        path = ROOT / "dist" / rel
        is_new_factory = row.get("sourceDocument") in NEW_FACTORY_SOURCES
        if is_new_factory and loc != "en" and not path.is_file():
            continue
        assert path.is_file(), rel
        markup = path.read_text("utf8")
        matches = re.findall(r"<title>([^<]+)</title>",markup,re.S)
        assert len(matches)==1,(loc,row["model"],"title count")
        title=unescape(matches[0])
        assert 20<=len(title)<=(60 if catalog_volume_numbers(row) else 90),(loc,row["model"],"SEO title length",title)
        assert title not in unique,(loc,row["model"],"duplicate SEO title")
        unique.add(title)
        assert "XUYI" in title,(loc,row["model"],title)
        assert re.search(r"<h1\b",markup,re.I),(loc,row["model"],"missing H1")
        h1=re.search(r"<h1\b[^>]*>(.*?)</h1>",markup,re.I|re.S)
        heading=unescape(re.sub(r"<[^>]+>"," ",h1.group(1))).strip()
        is_current_baseline = current_baseline(loc,row,owner)
        assert str(row["model"]).replace("透明款","") in heading,(loc,row["model"],heading)
        canonical=("https://xuyibottles.com/"+rel).replace("index.html","")
        assert '<link rel="canonical" href="'+canonical+'">' in markup,(loc,row["model"])
        available_locales = [
            candidate for candidate in LOCALES
            if (ROOT/"dist"/("" if candidate=="en" else candidate)/"products"/row["slug"]/"index.html").is_file()
        ]
        expected_hreflang = len(available_locales) + 1  # one x-default plus each real localized detail page
        assert markup.count('rel="alternate" hreflang=')==expected_hreflang,(loc,row["model"],"hreflang",available_locales)
        assert '<meta name="description" content="' in markup
        if not catalog_volume_numbers(row):
            no_sizes+=1
            assert "oz" not in title,(loc,row["model"],"unverified oz")
            continue
        with_sizes+=1
        if row["slug"] not in approved:
            assert is_new_factory,(loc,row["model"],"unapproved source model")
        if is_current_baseline and not is_new_factory:
            for number in catalog_volume_numbers(row):
                assert format_ml(number) in heading,(loc,row["model"],"H1 missing mL",heading)
                assert oz_number(number) in heading and "oz" in heading,(loc,row["model"],"H1 missing oz")
        # Existing manually curated title/description has absolute priority.
        if not is_current_baseline:
            continue
        eligible+=1
        suggested_title,suggested_description=new_seo(loc,row,catalog_volume_numbers(row))
        assert title==suggested_title,(loc,row["model"],"source SEO title differs from H1 facts",title,suggested_title)
        assert '<meta property="og:title" content="'+title.replace("&","&amp;").replace('"',"&quot;")+'">' in markup,(
            loc,row["model"],"OG title drift")
        desc=re.search(r'<meta name="description" content="([^"]*)"',markup)
        assert unescape(desc.group(1))==suggested_description,(loc,row["model"],"description mismatch")
        assert "oz" in desc.group(1) and "oz" in title,(loc,row["model"],"missing oz SEO")
        for number in catalog_volume_numbers(row):
            assert format_ml(number) in title,(loc,row["model"],"title missing verified mL")
            assert oz_number(number) in title,(loc,row["model"],"title missing reviewed oz class")
        assert "certified" not in title.lower() and "FDA-approved" not in title,(loc,row["model"],"unverified marketing")
        total+=1

expected_with_sizes = 460 + len(new_factory_capacity_slugs)
assert with_sizes==expected_with_sizes and no_sizes==45,(with_sizes,no_sizes,expected_with_sizes)
assert 0<=eligible<=expected_with_sizes and total==eligible,(eligible,total)
print("XUYI_SOURCE_SEO_TITLE_H1_OG_LEGACY_5_LOCALES_PLUS_FACTORY_ENGLISH_ONLY",
      "WITH_SIZES",with_sizes,"UNKNOWN",no_sizes,"AUTO_ELIGIBLE",eligible,"PASS")