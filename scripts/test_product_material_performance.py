#!/usr/bin/env python3
"""Guard the lightweight five-language SKU material block, with no CMS changes."""
from pathlib import Path
from html import unescape
from urllib.parse import quote
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from product_material_performance import material_codes,render,inject
from product_material_performance import catalog_purchase_facts
from site_renderer import SERIES

root=Path(__file__).resolve().parent.parent
dist=root/"dist"
languages={
    "en":("Materials and practical use","Material characteristics to discuss"),
    "es":("Materiales y uso práctico","Propiedades de materiales a consultar"),
    "pt":("Materiais e uso prático","Características dos materiais"),
    "ru":("Материалы и применение","Особенности материалов"),
    "tr":("Malzemeler ve kullanım","Malzeme özellikleri"),
}
products={x["slug"]:x for x in SERIES.values()}
assert len(products)>=85
tested=0
for locale,(heading,features) in languages.items():
    prefix="" if locale=="en" else locale+"/"
    for slug,source in products.items():
        path=dist/prefix/"products"/slug/"index.html"
        if not path.exists() and locale!="en":continue
        markup=path.read_text(encoding="utf8")
        assert markup.count('id="material-performance"')==1,(locale,slug)
        assert markup.index('id="material-performance"')<markup.index('class="section product-ordering"'),(locale,slug)
        section=markup.split('<section class="section material-brief"',1)[1].split("</section>",1)[0]
        assert heading in section and features in section,(locale,slug)
        assert 'class="material-brief__grid"' in section
        assert 'class="material-brief__bottom"' in section
        assert 'href="/'+prefix+'contact/?model='+quote(str(source["model"]),safe="")+'#inquiry"' in section,(locale,slug)
        assert "plastic-bottle-material-selection/" in section,(locale,slug)
        if slug=="2501":assert "PC+PP" in section
        assert '90–100' not in section and "FDA approved" not in section
        for v in ("BPA","PETG","Tritan"):
            # PETG/Tritan appear in the optional *comparison guide link*, not
            # automatically as material claimed for an existing PC bottle.
            if v in ("PETG","Tritan") and slug=="2501":
                assert v not in section.split('class="material-brief__links"',1)[0],(locale,slug,v)
        assert markup.count('class="section product-overview"')==1
        tested+=1
assert tested>=425,tested

sources,traits=material_codes({"variants":[{"material":"PC+PP+ABS+硅胶"}]})
assert set(traits)=={"PC","PP","ABS","silicone"}
assert material_codes({"variants":[{"material":"PP+PE"}]})[1]==["PP","PE"]
# Unknown resin: do not invent PC/PP benefits or material assignments.
dummy={"model":"TEST","variants":[{"material":"UNLISTED-POLYMER"}]}
preview=render(dummy,"en","/products/TEST/")
assert "UNLISTED-POLYMER" in preview and "PC: often chosen" not in preview
assert inject('<section class="section product-overview">x</section><section class="section section--soft product-content">y',dummy,"en","/products/TEST/").count('id="material-performance"')==1
assert inject('<section class="section product-overview">x</section><section class="section section--soft product-content">y',dummy,"en","/products/TEST/").count('id="material-performance"')==1
assert "550ml" in catalog_purchase_facts(SERIES["2501"],"en")
assert "80 pcs" in catalog_purchase_facts(SERIES["2501"],"en")
assert "60ml" not in catalog_purchase_facts(SERIES["2506"],"en")
assert "500ml" in catalog_purchase_facts(SERIES["501"],"en")
assert not catalog_purchase_facts(SERIES["G-01"],"en")
print("XUYI_MATERIAL_DETAIL_5_LANGUAGES_PASSED",tested,"product pages; no extra CMS configuration")