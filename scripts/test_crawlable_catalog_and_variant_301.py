#!/usr/bin/env python3
"""No-JS crawlable catalogue pagination and 25 precise 301 slug corrections.

Source-level tests: slug metadata, CMS override priority, 5 locales, sitemap.
No static HTML, R2 or D1 mutations in the test.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from html import unescape
from math import ceil

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
DIST=ROOT/"dist"
from site_renderer import SERIES,PAGE_OVERRIDES,BODY_OVERRIDES
from product_slug_fix import ALIASES,route,source_redirects,normalize_local_links
from catalog_crawlable_pagination import PAGE_SIZE,navigation,upgrade_localized_cms
from product_locale_seo import polish_product_head
from locale_registry import approved_locales

state=json.loads((ROOT/"_local_ops/build-snapshot.json").read_text(encoding="utf8"))
factory_manifest=json.loads((ROOT/"data/factory-catalog-manifest-2026-11-03.json").read_text(encoding="utf8"))
assert factory_manifest["recordCount"]==len(factory_manifest["models"])==58
locales=approved_locales(state)
assert len(locales)>=5 and any(x["code"]=="en" for x in locales)
assert len(SERIES)>=85 and len(ALIASES)==5
slugs=[x["slug"] for x in SERIES.values()]
assert len(slugs)==len(set(slugs))
assert all(re.fullmatch("[a-z0-9][a-z0-9-]*",s) and not s.endswith("-") for s in slugs)
assert not any(s in slugs for s in ALIASES)
assert len({v for v in ALIASES.values()})==5
for legacy,clean in ALIASES.items():
    transparent=next(x for x in SERIES.values() if x["slug"]==clean)
    base=next(x for x in SERIES.values() if x["slug"]==clean.split("-")[0])
    assert transparent["model"]!=base["model"]
    assert str(transparent["model"]).endswith("透明款")
    assert route("/products/"+legacy+"/")=="/products/"+clean+"/"
    assert route("/products/"+clean+"/")=="/products/"+clean+"/"
    # D1 owner metadata belongs to the clean route during build as well.
    old="/products/"+legacy+"/"
    new="/products/"+clean+"/"
    if old in PAGE_OVERRIDES:
        assert new in PAGE_OVERRIDES
    if old in BODY_OVERRIDES:
        assert new in BODY_OVERRIDES
    for lang in locales:
        prefix=lang["pathPrefix"]
        f=DIST/prefix/"products"/clean/"index.html"
        assert f.is_file(),(lang["code"],clean,"no canonical product page")
        assert not (DIST/prefix/"products"/legacy/"index.html").exists()
        markup=f.read_text(encoding="utf8")
        canonical="https://xuyibottles.com"+("/"+prefix if prefix else "")+"/products/"+clean+"/"
        assert '<link rel="canonical" href="'+canonical+'">' in markup
        assert "<h1" in markup
        assert ('?model='+legacy) not in markup
        assert '<meta name="robots" content="index,follow">' in markup

redirects=(DIST/"_redirects").read_text(encoding="utf8").splitlines()
expected=set(source_redirects([l["pathPrefix"] for l in locales]))
assert expected.issubset(set(redirects))
assert len(expected)==len(ALIASES)*len(locales)
assert len(redirects)==len(set(x.split(" ",1)[0] for x in redirects))
sitemap=(DIST/"sitemap.xml").read_text(encoding="utf8")
for legacy,clean in ALIASES.items():
    assert "/products/"+legacy+"/" not in sitemap
    for l in locales:
        prefix=("/"+l["pathPrefix"] if l["pathPrefix"] else "")
        assert '<loc>https://xuyibottles.com'+prefix+'/products/'+clean+'/</loc>' in sitemap

ppt_rows=[row for row in state.get("products",[])
           if isinstance(row,dict) and isinstance(row.get("content"),dict)
           and row["content"].get("newProduct") is True
           and row["content"].get("sourceDocument")=="水杯最新产品.pptx"]
ppt_models={str(row.get("model","")) for row in ppt_rows}
assert all(ppt_models) and len(ppt_models)==len(ppt_rows), "PPT product models must be unique"
series_models={str(row.get("model","")).lower() for row in SERIES.values()}
factory_models={str(row.get("model","")).lower() for row in factory_manifest["models"]}
ppt_models_lower={model.lower() for model in ppt_models}
assert not (ppt_models_lower & (series_models | factory_models)), "PPT models overlap with existing catalogue models"
base_total=len(SERIES)+factory_manifest["recordCount"]
total=base_total+len(ppt_models)
ppt_links={"/products/"+model.lower()+"/" for model in ppt_models}
for l in locales:
    prefix=l["pathPrefix"]
    # All approved catalogue products, including the latest PPT imports, are
    # localized before publication. Keep every locale's crawlable catalog in
    # parity with the canonical release count.
    expected_total=total
    pages=ceil(expected_total/PAGE_SIZE)
    file=DIST/prefix/"products/index.html"
    doc=file.read_text(encoding="utf8")
    main=doc.split('<main id="main-content">',1)[1].split("</main>",1)[0]
    # All full HTML source model <a href> links remain usable with JS disabled.
    cards=re.findall(r'<a\b[^>]*data-product-card[^>]*\bhref="([^"]+)"',main)
    assert len(cards)==expected_total,(prefix,len(cards),expected_total)
    assert len(set(cards))==expected_total
    localized_ppt_links={(("/"+prefix) if prefix else "")+link for link in ppt_links}
    assert localized_ppt_links.issubset(set(cards)), "Published PPT products must enter every localized catalogue"
    for page in range(1,pages+1):
        assert 'data-page-link="'+str(page)+'" href="?page='+str(page)+'"' in main
    assert 'href="?page=2"' in main
    assert '<nav class="pagination"' in main
    for legacy in ALIASES:
        assert '/products/'+legacy+'/' not in main,(prefix,legacy)
        assert '?model='+legacy not in main

# Real CMS entry simulation: owner-customized nav and page content survive.
custom='<section><h2>Owner edited catalogue</h2><div class="pagination"><p>Owner custom page design</p></div></section>'
assert upgrade_localized_cms(custom)==custom
source='<a class="product-card" data-product-card href="/products/2306---/">Catalogue photo</a>'
oldnav='<div class="pagination"><button id="page-prev" type="button" aria-label="Previous page">← Prev</button><span id="page-status" aria-live="polite"></span><button id="page-next" type="button" aria-label="Next page">Next →</button></div>'
modified=upgrade_localized_cms(source+oldnav)
assert modified.count('<nav class="pagination"')==1
assert upgrade_localized_cms(modified)==modified
assert normalize_local_links(modified).count('/products/2306-transparent/')==1
assert normalize_local_links(normalize_local_links(modified))==normalize_local_links(modified)
assert "data-page-link" in navigation(PAGE_SIZE*11+1)
assert navigation(PAGE_SIZE*11+1).count('data-page-link=')==12
# CMS-edited title must never be truncated/reverted from the approved baseline.
owned='<html><head><title>Owner deliberately selected this completely unique transparent variant title</title></head><body></body></html>'
assert 'Owner deliberately selected' in polish_product_head(owned,"en","/products/2306-transparent/")
# Legacy original imported D1 routes must normalize before output.
assert route("/products/2400---/")=="/products/2400-transparent/"
assert not any(re.search(r"/products/[0-9]{4}---/",x.split()[1]) for x in redirects)
# Future D1 edits remain authoritative under the old imported route until
# the owner creates a new canonical route record. The direct new key wins.
import copy
from scripts.cms_seo_curation_guard import current_field,may_curate
assert (may_curate("es","/products/2400-transparent/","title",state) or
    any(x.get("slug")=="2400-transparent" and x.get("locale")=="es"
        for x in state.get("productSeo",[]))),"Historic curation or canonical D1 SEO required"
changed=copy.deepcopy(state)
# Isolate legacy/direct translation-key behavior from the higher-priority
# productSeo table; its precedence is covered by test_cms_seo_rebuild_policy.
changed["productSeo"]=[x for x in changed.get("productSeo",[])
    if not (x.get("locale")=="es" and x.get("slug") in ("2400---","2400-transparent"))]
legacy_record=next(x for x in changed["translations"]
    if x.get("locale")=="es" and x.get("resourceId")=="page:/products/2400---/")
legacy_record["content"]["title"]="Owner chooses a brand-new Spanish title"
assert current_field("es","/products/2400-transparent/","title",changed)=="Owner chooses a brand-new Spanish title"
assert not may_curate("es","/products/2400-transparent/","title",changed)
canonical_record=copy.deepcopy(legacy_record)
canonical_record["resourceId"]="page:/products/2400-transparent/"
canonical_record["content"]["title"]="Owner canonical route selected title"
changed["translations"].append(canonical_record)
assert current_field("es","/products/2400-transparent/","title",changed)=="Owner canonical route selected title"
assert not may_curate("es","/products/2400-transparent/","title",changed)
print("XUYI_CRAWLABLE_QUERY_PAGING_FACTORY_BATCH_25_CANONICAL_301_CMS_PASSED",
      "models",total,"pages",pages,"languages",len(locales),"redirects",len(expected))