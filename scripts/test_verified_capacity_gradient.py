#!/usr/bin/env python3
"""XUYI verified ml/fl oz keywords, gradient identity and owner-edit safety."""
from pathlib import Path
from tempfile import TemporaryDirectory
from html import unescape
import re
import shutil
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from verified_capacity_gradient_en import (
    SOURCE_CAPACITY,GRADIENT_HINTS,actual_model,
    source_baseline,seo_copy,update_one,apply
)
from home_bpa_source import add_home_bpa_note,_SOURCE as HOME_VERIFICATION_SOURCE
from source_catalog_capacity_oz import catalog_volume_numbers,new_seo

DIST=ROOT/"dist"
assert len(SOURCE_CAPACITY)==23
assert sum(grad for _,grad in SOURCE_CAPACITY.values())==13
checked=0
for slug,(ml,gradient) in SOURCE_CAPACITY.items():
    row=actual_model(slug)
    assert row and str(row.get("capacity","")).lower()==f"{ml}ml",slug
    html=(DIST/"products"/slug/"index.html").read_text(encoding="utf8")
    title=unescape(re.search(r"<title>([^<]+)</title>",html).group(1))
    desc=unescape(re.search(r'<meta name="description" content="([^"]+)"',html).group(1))
    exp_title,exp_desc=new_seo('en',row,catalog_volume_numbers(row))
    assert (title,desc)==(exp_title,exp_desc),(slug,title,desc)
    expected_oz="28 oz class" if ml==800 else "32 oz class"
    assert f"{ml}ml" in title and len(title)<=60,slug
    assert expected_oz in desc,slug
    assert expected_oz in re.search(r"<h1>(.*?)</h1>",html).group(1),slug
    assert title.count(str(row["model"]))==1,slug
    assert "Tritan" in desc and "BPA-free" in desc,slug
    assert not re.search(r"\bcertified BPA.free\b|\bmade from Tritan\b",title+" "+desc,re.I),slug
    if gradient:
        assert html.count('class="product-gradient-finish"')==1,slug
        assert GRADIENT_HINTS[slug] in html,slug
    else:
        assert 'class="product-gradient-finish"' not in html,slug
    checked+=1
assert checked==23,checked
css=(DIST/"assets/site.css").read_text(encoding="utf8")
assert "body:has(#xuyi-home-banners)" in css
for loc,(hero_note,headline,detail) in HOME_VERIFICATION_SOURCE.items():
    f=DIST/("index.html" if loc=="en" else loc+"/index.html")
    body=f.read_text(encoding="utf8")
    assert body.count('class="home-bpa-verification"')==1,(loc,"duplicate home prompt")
    assert headline in body and detail in body,(loc,"missing conditional material verification")
    assert not re.search(r'(?i)\bcertified BPA.free\b',body),loc
    assert 'id="xuyi-home-banners"' in body,loc
    assert 'class="home-bpa-verification"' not in (DIST/("products/2514/index.html" if loc=="en" else loc+"/products/2514/index.html")).read_text(encoding="utf8")

with TemporaryDirectory(prefix="xuyi-capacity-owner-") as td:
    root=Path(td)
    for slug in ("2514","lo-005"):
        src=DIST/"products"/slug/"index.html"
        dst=root/"products"/slug/"index.html"
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst)
        model=actual_model(slug)
        assert update_one(dst,slug,SOURCE_CAPACITY[slug][0],True,model)==(0,0)
        # Explicit later CMS edit of title: preserve all other fields and
        # never insert another gradient paragraph.
        body=dst.read_text(encoding="utf8").replace("<title>","<title>CMS APPROVED ",1)
        dst.write_text(body,encoding="utf8")
        assert update_one(dst,slug,SOURCE_CAPACITY[slug][0],True,model)==(0,0)
        assert dst.read_text(encoding="utf8")==body
        # Historical gradient processor no longer touches SEO/oz headings;
        # owner edits survive unchanged on repeated execution.
        regenerated=dst.read_text(encoding="utf8")
        assert update_one(dst,slug,SOURCE_CAPACITY[slug][0],True,model)==(0,0)
        assert dst.read_text(encoding="utf8")==regenerated
    home=(DIST/"index.html").read_text(encoding="utf8")
    assert add_home_bpa_note(home,"en")==home
    owner=home.replace("Taizhou, China · Plastic drinkware · OEM/ODM inquiries","Owner-selected hero text")
    assert add_home_bpa_note(owner,"en")==owner
print("XUYI_CAPACITY_GRADIENT_BPA_CONDITIONAL_23_MODELS_13_GRADIENTS_5_LOCALES_OWNER_POLICY_PASSED")