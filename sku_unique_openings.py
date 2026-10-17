"""20 verified-model purchasing introductions, before final HTML rendering.

This renderer owns a *narrow* pilot editorial introduction, not the whole D1
product body. A later D1 edit of any translated mainHtml field is authoritative.
English D1 body owner edits are guarded by site_renderer itself.
"""
from pathlib import Path
from html import escape
from hashlib import sha256
import json,re

ROOT=Path(__file__).resolve().parent
EN=json.loads((ROOT/"data/pilot-20-sku-openings-en.json").read_text(encoding="utf8"))["groups"]
LOCALES={
 group:json.loads((ROOT/f"data/pilot-20-sku-openings-{group}-locales.json").read_text(encoding="utf8"))
 for group in ("sports","kids","jugs","shakers")
}
OWNER=json.loads((ROOT/"data/pilot-20-sku-d1-body-baselines.json").read_text(encoding="utf8"))["hashes"]
COPY={slug:{"en":paragraph,**LOCALES[group][slug]} for group,items in EN.items() for slug,paragraph in items.items()}
# Native-language additions complete the intended 100–150-word buyer
# introductions without repeating the same generic category paragraph.
ADDENDA=json.loads((ROOT/"data/pilot-20-sku-openings-locale-addenda.json").read_text(encoding="utf8"))
for sku,language_lines in ADDENDA.items():
    for locale,extra in language_lines.items():
        COPY[sku][locale]=COPY[sku][locale].rstrip()+" "+extra.strip()
CATEGORY={
 "sports":"Plastic Sports Water Bottles",
 "kids":"Kids Plastic Water Bottles",
 "jugs":"Large Capacity Water Jugs",
 "shakers":"Plastic Shaker Bottles",
}
SELECTED_GROUP={slug:group for group,items in EN.items() for slug in items}

def editor_intro(body,row,locale,owner_edited=False):
    if owner_edited:return body
    slug=str(row.get("slug",""))
    item=COPY.get(slug)
    if item is None:
        from sku_unique_openings_phase2 import editor_intro as phase2_editor_intro
        return phase2_editor_intro(body,row,locale,owner_edited=owner_edited)
    if locale not in item:return body
    if row.get("category")!=CATEGORY[SELECTED_GROUP[slug]]:
        raise ValueError("Pilot SKU category mismatch: "+slug)
    if 'data-pilot-intro="'+slug+'"' in body:return body
    if locale!="en":
        original_hash=OWNER.get(slug,{}).get(locale)
        if not original_hash or sha256(body.encode("utf8")).hexdigest()!=original_hash:
            return body
    # This HTML is still a source-stage product template / D1 content field,
    # not the generated dist page. Replace only the generic paragraph after
    # the H1 so the new unique introduction genuinely displaces boilerplate.
    h1=re.search(r"<h1\b[^>]*>.*?</h1>",body,re.I|re.S)
    if not h1:return body
    rest=body[h1.end():]
    original=re.match(r'\s*<p class="copy-muted">[\s\S]*?</p>',rest)
    if not original:return body # Owner customized template: do not inject.
    paragraph=item[locale]
    expected_model=str(row["model"]).split("透明款",1)[0]
    if expected_model not in paragraph and slug not in paragraph:
        raise ValueError("Pilot editorial copy missing source model: "+slug+"/"+locale)
    rendered='<p class="copy-muted product-buyer-intro" data-pilot-intro="'+escape(slug)+'">'+escape(paragraph)+'</p>'
    return body[:h1.end()]+rendered+rest[original.end():]
