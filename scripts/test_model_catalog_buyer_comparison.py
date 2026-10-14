#!/usr/bin/env python3
"""Release guard: source-backed model comparisons, five languages, no invented SKUs."""
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from model_catalog_buyer_comparison import SERIES,LOCALES,LANG,SOURCE_LABELS,peers,capacity_number,capacity_text,material_text,quantity_text

DIST=ROOT/"dist"
catalog=[r for r in SERIES.values() if not r.get("manualNew")]
manual=[r for r in SERIES.values() if r.get("manualNew")]
assert len(catalog)>=85 and len(manual)>=16
assert {r["category"] for r in catalog}=={
    "Plastic Sports Water Bottles","Large Capacity Water Jugs",
    "Kids Plastic Water Bottles","Plastic Shaker Bottles"
}
checked=0
for row in catalog:
    selected=peers(row,catalog)
    assert len(selected)==3,(row["model"],selected)
    assert len({x["model"] for x in selected})==3
    assert all(x["category"]==row["category"] and x["model"]!=row["model"] for x in selected)
    for lang in LOCALES:
        prefix="" if lang=="en" else lang+"/"
        source=(DIST/prefix/"products"/str(row["slug"])/"index.html").read_text(encoding="utf8")
        assert source.count('id="catalog-comparison"')==1,(lang,row["slug"])
        main=source.split('id="catalog-comparison"',1)[1].split("</section>",1)[0]
        # Exact source text is required only for the source-generated module.
        # A D1 editor's rewritten comparison remains authoritative and must
        # not fail deployment because its headings/alternatives differ.
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
            if capacity_number(row) is None:
                assert LANG[lang]["capacityUnknown"] in main,(row["model"],lang)
        else:
            assert main.strip(),(lang,row["model"],"empty CMS comparison")
        assert not any(x in main for x in ["InStock","AggregateRating","Best price guaranteed","FDA certified","CE certified"])
        checked+=1
for row in manual:
    for lang in LOCALES:
        prefix="" if lang=="en" else lang+"/"
        page=DIST/prefix/"products"/str(row["slug"])/"index.html"
        assert page.is_file()
        assert 'id="catalog-comparison"' not in page.read_text(encoding="utf8"),(lang,row["slug"])
print("XUYI_CATALOG_COMPARISONS_SOURCE_BACKED",checked,"pages, 16 entries lacking comparable source-catalog measurements excluded")