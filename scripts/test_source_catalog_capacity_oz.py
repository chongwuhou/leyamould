#!/usr/bin/env python3
"""Five-language source-rendered product SEO, capacity and card regression gate."""
from __future__ import annotations

from copy import deepcopy
from html import unescape
from pathlib import Path
import os
import re
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"scripts"))
os.environ.setdefault("LEYA_BUILD_SNAPSHOT",str(ROOT/"_local_ops/build-snapshot.json"))

from cms_seo_curation_guard import snapshot
from factory_catalog_locales import LABELS, _source_products, _card_title, catalog_cards as factory_catalog_cards
from factory_product_locales import SOURCE_DOCUMENTS, translation_for, localized_name
from seo_structured_components import visible_faq
from product_source_identity import matches_owner_field
from product_seo_d1_source import apply_d1_product_seo
from site_renderer import SERIES, CAT
from scripts.source_catalog_capacity_oz import (
    MILLILITERS_PER_US_FL_OZ, LOCALES, catalog_volume_numbers, volume_terms,
    format_oz, current_baseline, new_seo, new_seo_without_capacity,
    product_h1_text, source_body_enrichment, enrich_catalog_body, source_field_allowed,
    verified_source_color_term,
)

DIST=ROOT/"dist"
original=snapshot()
data=original
assert original and original["site"]=="leyamould"
assert abs(MILLILITERS_PER_US_FL_OZ-29.5735295625)<1e-10
assert format_oz(500)=="16.9 oz class"
assert format_oz(750)=="24 oz class"
assert format_oz(800)=="28 oz class"
assert format_oz(1000)=="32 oz class"
assert format_oz(1200)=="40 oz class"
assert format_oz(2000)=="64 oz class"
assert format_oz(3800)=="128 oz class"
assert catalog_volume_numbers(SERIES["2506"])==()
assert catalog_volume_numbers({**SERIES["2506"],"capacity":"600ml"})==(600.0,)
assert catalog_volume_numbers(SERIES["5247"])==(450.0,700.0)
assert catalog_volume_numbers(SERIES["5248"])==(450.0,700.0)
assert catalog_volume_numbers(SERIES["G-02"])==()

new_rows=_source_products(SERIES)
assert len(new_rows)>=153,(len(new_rows),SOURCE_DOCUMENTS)
assert {row.get("sourceDocument") for row in new_rows}==SOURCE_DOCUMENTS
vol_models=sum(bool(catalog_volume_numbers(row)) for row in SERIES.values())
assert len(SERIES)>=254
assert vol_models>=245,vol_models

volume_pages=custom_pages=0
for row in SERIES.values():
    numbers=catalog_volume_numbers(row)
    for lang in LOCALES:
        prefix="" if lang=="en" else lang+"/"
        page=DIST/prefix/"products"/row["slug"]/"index.html"
        assert page.is_file(),(lang,row["model"],page)
        markup=page.read_text(encoding="utf8")
        head,main=markup.split("</head>",1)
        assert main.count('class="product-custom-material-options"')==1,(lang,row["model"],"material options panel")
        assert not re.search(r'(?i)\bcertified BPA.free\b|\bmade of Tritan\b',head+main),(lang,row["model"],"unsupported certification")
        if row.get("category") in {"Plastic Sports Water Bottles","Kids Plastic Water Bottles","Large Capacity Water Jugs","Plastic Shaker Bottles","Spray Water Bottles"}:
            assert "Tritan" in main and "BPA" in main,(lang,row["model"],"custom plastic choices")
        elif row.get("category")=="Titanium Vacuum Cups":
            assert any(term in main.lower() for term in ("titanium","titán","titânio","титан","titanyum")),(lang,row["model"],"titanium sourcing")
        if numbers:
            volume_pages+=1
            exact=volume_terms(numbers,lang)
            assert main.count('class="product-capacity-summary"')==1,(lang,row["model"],"capacity summary")
            assert exact in main,(lang,row["model"],exact)
            assert 'class="product-capacity-disclaimer"' in main,(lang,row["model"],"size-class caveat")
            title=unescape(re.search(r"<title>([^<]+)</title>",head).group(1))
            desc=unescape(re.search(r'<meta name="description" content="([^"]+)"',head).group(1))
            h1=unescape(re.search(r"<h1[^>]*>(.*?)</h1>",main,re.S).group(1))
            allow_title=source_field_allowed(lang,row,"title",data)
            allow_desc=source_field_allowed(lang,row,"description",data)
            if allow_title:
                assert "ml" in title.lower() and "oz" in title.lower(),(lang,row["model"],title)
                assert len(title)<=60,(lang,row["model"],len(title))
            if allow_desc:
                assert "ml" in desc.lower() and "oz" in desc.lower(),(lang,row["model"],desc)
                assert len(desc)<=180,(lang,row["model"],len(desc))
            if h1==product_h1_text(lang,row):
                assert "B2B" in h1 and str(row["model"]).replace("透明款","") in h1,(lang,row["model"],h1)
                assert exact in h1,(lang,row["model"],"H1 must show all verified mL and approximate oz sizes",h1)
            if row.get("sourceDocument") in SOURCE_DOCUMENTS:
                expected_title,expected_desc=new_seo(lang,row,numbers)
                if allow_title:assert title==expected_title,(lang,row["model"],title,expected_title)
                if allow_desc:assert desc==expected_desc,(lang,row["model"],desc,expected_desc)
            for val in numbers:
                assert format_oz(val,lang) in main,(lang,row["model"],val)
        else:
            assert 'class="product-capacity-summary"' not in main,(lang,row["model"])
            if str(row["model"])=="2506":
                assert main.count('class="product-capacity-warning"')==1,(lang,"2506 warning")
        custom_pages+=1

assert volume_pages==vol_models*len(LOCALES),(volume_pages,vol_models,len(LOCALES))
assert custom_pages==len(SERIES)*len(LOCALES),(custom_pages,len(SERIES)*len(LOCALES))

# Every source product gets a distinct native detail page, not a repeated English
# placeholder. The localized H1, metadata, FAQ and procurement guidance vary by model.
for lang in LOCALES:
    titles=set()
    descriptions=set()
    for row in new_rows:
        prefix="" if lang=="en" else lang+"/"
        markup=(DIST/prefix/"products"/row["slug"]/"index.html").read_text(encoding="utf8")
        head,main=markup.split("</head>",1)
        title=unescape(re.search(r"<title>([^<]+)</title>",head).group(1))
        desc=unescape(re.search(r'<meta name="description" content="([^"]+)"',head).group(1))
        titles.add(title);descriptions.add(desc)
        h1=unescape(re.search(r"<h1[^>]*>(.*?)</h1>",main,re.S).group(1))
        assert str(row["model"]).replace("透明款","") in h1,(lang,row["model"],h1)
        if h1==product_h1_text(lang,row):assert "B2B" in h1 and volume_terms(catalog_volume_numbers(row),lang) in h1,(lang,row["model"],h1)
        if source_field_allowed(lang,row,"title",data):
            assert "OEM" in title and "XUYI" in title and "ml" in title.lower() and "oz" in title.lower(),(lang,row["model"],title)
        if source_field_allowed(lang,row,"description",data):
            assert "B2B" in desc and "ml" in desc.lower() and "oz" in desc.lower(),(lang,row["model"],desc)
        assert len(visible_faq(markup))>=4,(lang,row["model"],"visible SKU-specific FAQ content missing")
    assert len(titles)==len(new_rows),(lang,"duplicate titles",len(titles))
    assert len(descriptions)==len(new_rows),(lang,"duplicate descriptions",len(descriptions))

# All 254 models appear once in every localized catalog with native detail links,
# verified mL/oz badges and B2B/OEM search terms.
for lang in LOCALES:
    prefix="" if lang=="en" else lang+"/"
    listing=(DIST/prefix/"products/index.html").read_text(encoding="utf8")
    for row in SERIES.values():
        slug=row["slug"]
        localized_prefix="" if lang=="en" else lang+"/"
        href="/"+localized_prefix+"products/"+slug+"/"
        cards=re.findall(r'<a\b(?=[^>]*class="product-card\b)(?=[^>]*href="'+re.escape(href)+r'")[^>]*>.*?</a>',listing,re.S)
        assert len(cards)==1,(lang,slug,"card count",len(cards))
        card=cards[0]
        assert "B2B" in card and "OEM" in card,(lang,slug,"procurement search terms")
        numbers=catalog_volume_numbers(row)
        if numbers:
            if row.get("category")=="Two-Way Drinking Cups":
                assert 'class="product-card__capacity"' not in card,(lang,slug,"two-way capacity should be in title")
                assert volume_terms(numbers,lang) in card,(lang,slug,"two-way title capacity")
            else:
                assert card.count('class="product-card__capacity"')==1,(lang,slug,"capacity badge")
                assert volume_terms(numbers,lang) in card,(lang,slug,"capacity label")
        else:
            assert 'class="product-card__capacity"' not in card,(lang,slug,"unexpected capacity badge")
        if lang=="en" or row.get("sourceDocument") in SOURCE_DOCUMENTS:
            heading_match=re.search(r"<h3\b[^>]*>(.*?)</h3>",card,re.S)
            assert heading_match,(lang,slug,"missing visible product title")
            heading=unescape(re.sub(r"<[^>]+>"," ",heading_match.group(1))).strip()
            expected_title=_card_title(row,lang)
            if lang=="en":
                default_titles={localized_name(row,lang),str(row.get("name") or "").strip(),str(row.get("model") or slug).strip()}
                capacity_text=str(row.get("capacity") or "").strip()
                if capacity_text:
                    default_titles.update(capacity_text+" "+value for value in tuple(default_titles) if value)
                if heading in default_titles:
                    assert heading==expected_title,(lang,slug,"English default card title was not refreshed",heading,expected_title)
                else:
                    assert heading,(lang,slug,"owner-authored English card title must remain nonempty")
            else:
                assert heading!=localized_name(row,lang),(lang,slug,"generic factory card title",heading)
                if heading==expected_title and numbers:
                    assert volume_terms(numbers,lang) in heading,(lang,slug,"localized card title missing mL/oz")
            color=verified_source_color_term(lang,row)
            if color and heading==expected_title:
                assert color.casefold() in heading.casefold(),(lang,slug,"verified color missing from card title",color,heading)
        if lang!="en" and row.get("sourceDocument") in SOURCE_DOCUMENTS:
            assert LABELS[lang]["details"] in card,(lang,slug,"native detail link label")
# Source renderers are idempotent and never append duplicate panels or badges.
sample=next(row for row in new_rows if catalog_volume_numbers(row))
body='<section class="product-overview"><table class="spec"></table></section>'
once=source_body_enrichment(body,"en",sample)
assert once==source_body_enrichment(once,"en",sample)
card='<a class="product-card" data-search="sample" href="/products/'+sample["slug"]+'/"><h3>Sample</h3></a>'
enriched=enrich_catalog_body(card,"en",SERIES)
assert enriched==enrich_catalog_body(enriched,"en",SERIES)
assert 'class="product-card__capacity"' in enriched
assert "wholesale B2B OEM" in enriched
# The English CMS may provide a D1-owned catalog body. Refresh only an untouched
# default SKU card title, while retaining an owner-authored replacement.
card_product=SERIES["2501"]
card_slug=card_product["slug"]
card_category=CAT[card_product["category"]][1]
legacy_card_title=str(card_product.get("capacity") or "")+" "+localized_name(card_product,"en")
owner_card_title="Owner-approved catalog title for model 2501"
def catalog_fixture(title):
    return (
        '<div class="grid grid--4 product-grid">'
        '<a class="product-card" data-product-card data-search="legacy catalog" href="/products/'+card_slug+'/">'
        '<div class="product-card__body"><span class="product-card__small">MODEL 2501</span><h3>'+title+'</h3></div>'
        '</a></div>'
    )
catalog_route="/collections/"+card_category+"/"
source_card=factory_catalog_cards(catalog_fixture(legacy_card_title),"en",catalog_route,series={"2501":card_product})
assert _card_title(card_product,"en") in source_card,("English D1 default catalog card title not refreshed",source_card)
assert source_card==factory_catalog_cards(source_card,"en",catalog_route,series={"2501":card_product})
owner_card=factory_catalog_cards(catalog_fixture(owner_card_title),"en",catalog_route,series={"2501":card_product})
assert owner_card_title in owner_card,("English D1 owner-authored catalog title overwritten",owner_card)
# LO priority cards stay first, but their default title, capacity badge and
# search terms receive the same source refresh; an owner title remains intact.
lo_product=SERIES["LO-001"]
lo_slug=lo_product["slug"]
lo_category=CAT[lo_product["category"]][1]
lo_default_title=str(lo_product.get("name") or localized_name(lo_product,"en"))
lo_owner_title="Owner-approved LO catalog title"
def lo_catalog_fixture(title):
    return (
        '<div class="grid grid--4 product-grid">'
        '<a class="product-card" data-product-card data-search="legacy LO catalog" href="/products/'+lo_slug+'/">'
        '<div class="product-card__body"><span class="product-card__small">MODEL LO-001</span><h3>'+title+'</h3></div>'
        '</a></div>'
    )
lo_route="/collections/"+lo_category+"/"
lo_source_card=factory_catalog_cards(lo_catalog_fixture(lo_default_title),"en",lo_route,series={"LO-001":lo_product})
assert _card_title(lo_product,"en") in lo_source_card,("LO priority default title not refreshed",lo_source_card)
assert 'class="product-card__capacity"' in lo_source_card,("LO priority capacity badge missing",lo_source_card)
assert volume_terms(catalog_volume_numbers(lo_product),"en") in lo_source_card,("LO priority mL/oz missing",lo_source_card)
assert lo_source_card==factory_catalog_cards(lo_source_card,"en",lo_route,series={"LO-001":lo_product})
lo_owner_card=factory_catalog_cards(lo_catalog_fixture(lo_owner_title),"en",lo_route,series={"LO-001":lo_product})
assert lo_owner_title in lo_owner_card,("LO owner-authored catalog title overwritten",lo_owner_card)


from scripts.model_catalog_buyer_comparison import SOURCE_MODELS,render_for_product
comparison_row=SOURCE_MODELS[0]
comparison_body=source_body_enrichment(body,"en",comparison_row)
assert 'id="catalog-comparison"' in comparison_body
assert comparison_body==source_body_enrichment(comparison_body,"en",comparison_row)

# Owner edits remain authoritative. Only fields that still match the reviewed
# factory-default baseline may receive the refreshed source-generated SEO.
edited=deepcopy(original)
row=next(x for x in edited["pages"] if x.get("route")=="/products/2514/")
row["seo_title"]="OWNER TITLE 1000ml green bottle"
assert not current_baseline("en",SERIES["2514"],edited)
unmodified=deepcopy(original)
row=next(x for x in unmodified["translations"] if x.get("locale")=="es" and x.get("resourceId")=="page:/products/2514/")
row["content"]["description"]="OWNER EDITED description"
assert not current_baseline("es",SERIES["2514"],unmodified)
assert current_baseline("en",SERIES["2514"],original) or any(
    x.get("slug")=="2514" and x.get("locale")=="en" for x in original.get("productSeo",[])
)
future={"slug":"future-source-1500","model":"F-1500","capacity":"1500ml",
        "category":"Plastic Sports Water Bottles","name":"1500ml Plastic Sports Bottle"}
assert catalog_volume_numbers(future)==(1500.0,)
assert current_baseline("en",future,original)
assert "1500ml" in new_seo("en",future,(1500.0,))[0]
assert "50 oz class" in new_seo("en",future,(1500.0,))[1]
assert "capacity to be confirmed" in new_seo_without_capacity("en",{**future,"capacity":""})[1].lower()
assert "B2B" in product_h1_text("en",sample) and "Manufacturer" in product_h1_text("en",sample)
two_way_products=[row for row in SERIES.values() if row.get("category")=="Two-Way Drinking Cups"]
from factory_catalog_locales import _card_title
for locale in LOCALES:
    two_way_h1=[product_h1_text(locale,row) for row in two_way_products]
    assert len(two_way_h1)==20 and len(set(two_way_h1))==20,(locale,"two-way H1 uniqueness")
    for row,heading in zip(two_way_products,two_way_h1):
        card_title=_card_title(row,locale)
        variant,buyer=card_title.split(" | ",1)
        volume=volume_terms(catalog_volume_numbers(row),locale)
        if volume and variant.startswith(volume+" "):
            variant=variant[len(volume)+1:]
        assert variant in heading,(locale,row["slug"],"two-way H1 missing source feature modifier",heading,variant)
        assert buyer in heading,(locale,row["slug"],"two-way H1 missing B2B buyer modifier",heading,buyer)
        assert volume in heading,(locale,row["slug"],"two-way H1 missing mL/oz capacity",heading,volume)
assert not matches_owner_field("Owner-authored gallery H1","g-02","en",0,False)
# A single D1 title edit must not block source refresh of the still-baseline description.
owner_test=deepcopy(original)
owner_row=new_rows[0]
assert not any(x.get("slug")==owner_row["slug"] and x.get("locale")=="en" for x in owner_test.get("productSeo",[]))
owner_test.setdefault("productSeo",[]).append({"slug":owner_row["slug"],"locale":"en","seoTitle":"OWNER TITLE","metaDescription":""})
assert not source_field_allowed("en",owner_row,"title",owner_test)
assert source_field_allowed("en",owner_row,"description",owner_test)
probe='<head><title>Source Title</title><meta name="description" content="Source Description"><meta property="og:title" content="Source Title"><meta property="og:description" content="Source Description"></head>'
updated=apply_d1_product_seo(probe,owner_row["slug"],"en",owner_test)
assert "OWNER TITLE" in updated and "Source Description" in updated
# Imported PPT SEO strings are source defaults only while they exactly match the reviewed import templates.
ppt_row=next(row for row in new_rows if row.get("sourceDocument")=="水杯最新产品.pptx")
ppt_owner=deepcopy(original)
ppt_record=next(item for item in ppt_owner["products"] if str(item.get("model"))==ppt_row["slug"])
assert source_field_allowed("en",ppt_row,"title",ppt_owner)
assert source_field_allowed("en",ppt_row,"description",ppt_owner)
ppt_record["content"]["seoDescription"]+=" Owner-approved addition."
assert not source_field_allowed("en",ppt_row,"description",ppt_owner)
assert source_field_allowed("en",ppt_row,"title",ppt_owner)

print(f"PASS: {len(SERIES)} products, {len(new_rows)} new factory models, "
      f"{volume_pages} localized capacity pages, {custom_pages} localized detail pages, "
      f"{len(LOCALES)} languages, source-rendered SEO and owner-priority checks.")
