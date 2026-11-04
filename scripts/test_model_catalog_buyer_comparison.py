#!/usr/bin/env python3
"""Release guard: source-backed comparisons and five-language native product details."""
from pathlib import Path
import re
import sys
import os
ROOT=Path(__file__).resolve().parent.parent
SNAPSHOT=ROOT/"_local_ops"/"build-snapshot.json"
if SNAPSHOT.is_file():os.environ["XUYI_BUILD_SNAPSHOT"]=str(SNAPSHOT)
sys.path.insert(0,str(ROOT/"scripts"))
from model_catalog_buyer_comparison import (
    SERIES,LOCALES,LANG,SOURCE_LABELS,SOURCE_MODELS,peers,capacity_number,
    capacity_text,material_text,quantity_text,render_for_product
)
from factory_catalog_locales import LABELS
from factory_product_locales import SOURCE_DOCUMENTS

DIST=ROOT/"dist"
catalog=[r for r in SERIES.values() if not r.get("manualNew")]
manual=[r for r in SERIES.values() if r.get("manualNew")]
assert len(SOURCE_MODELS)>=84 and len(manual)>=16
assert {r["category"] for r in catalog}=={
    "Plastic Sports Water Bottles","Large Capacity Water Jugs",
    "Kids Plastic Water Bottles","Plastic Shaker Bottles"
}
checked=0
for row in SOURCE_MODELS:
    selected=peers(row,SOURCE_MODELS)
    assert len(selected)==3,(row["model"],selected)
    assert len({x["model"] for x in selected})==3
    assert all(x["category"]==row["category"] and x["model"]!=row["model"] for x in selected)
    for lang in LOCALES:
        prefix="" if lang=="en" else lang+"/"
        source=(DIST/prefix/"products"/str(row["slug"])/"index.html").read_text(encoding="utf8")
        assert source.count('id="catalog-comparison"')==1,(lang,row["slug"])
        main=source.split('id="catalog-comparison"',1)[1].split("</section>",1)[0]
        if LANG[lang]["title"] in main:
            assert SOURCE_LABELS[lang] in main
            assert LANG[lang]["disclaimer"] in main
            assert LANG[lang]["verifyAssembly"] in main
            for selected_row in selected:
                href="/"+prefix+"products/"+str(selected_row["slug"])+"/"
                assert main.count('href="'+href+'"')==1,(row["model"],lang,href)
                assert (DIST/prefix/"products"/str(selected_row["slug"])/"index.html").is_file()
                assert material_text(selected_row,LANG[lang]) in main,(row["model"],lang,"material")
                assert capacity_text(selected_row,LANG[lang]) in main,(row["model"],lang,"capacity")
                assert quantity_text(selected_row,LANG[lang]) in main,(row["model"],lang,"carton")
        else:
            assert main.strip(),(lang,row["model"],"empty CMS comparison")
        assert not any(x in main for x in ["InStock","AggregateRating","Best price guaranteed","FDA certified","CE certified"])
        checked+=1
assert all(render_for_product(row,"en") for row in SOURCE_MODELS)
assert all(not render_for_product(row,"en") for row in manual)

# Both new source batches now receive native localized detail pages, not English-only links.
assert SOURCE_DOCUMENTS=={"puyunsm(1).pdf","水杯最新产品.pptx"}
for row in manual:
    slug=str(row["slug"])
    source_document=row.get("sourceDocument") or ""
    for lang in LOCALES:
        prefix="" if lang=="en" else lang+"/"
        page=DIST/prefix/"products"/slug/"index.html"
        assert page.is_file(),(lang,slug,"Missing native localized detail")
        markup=page.read_text(encoding="utf8")
        assert 'id="catalog-comparison"' not in markup,(lang,slug,"manual products lack validated peer data")
        if source_document in SOURCE_DOCUMENTS:
            assert row["model"] in markup
            assert 'class="product-custom-material-options"' in markup
            assert 'class="product-capacity-summary"' in markup
            if lang!="en":
                assert LABELS[lang]["details"] in (DIST/prefix/"products/index.html").read_text(encoding="utf8")
print("XUYI_SOURCE_RENDERED_COMPARISONS",checked,"validated comparison pages;",
      len(manual),"manual products; all new factory models have 5 native-language details.")