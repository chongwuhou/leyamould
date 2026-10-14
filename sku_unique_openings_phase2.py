"""Second-wave reviewed-by-source SKU buyer introductions, before HTML output.

An exact historic D1 mainHtml hash is required for translated pages.
Any later admin edit wins. No invented lids, handling claims or certifications.
"""
from pathlib import Path
from hashlib import sha256
from html import escape
import json,re
ROOT=Path(__file__).resolve().parent
EN=json.loads((ROOT/"data/phase2-6-sku-openings-en.json").read_text(encoding="utf8"))["groups"]
LOCALES=json.loads((ROOT/"data/phase2-6-sku-openings-locales.json").read_text(encoding="utf8"))["locales"]
OWNER=json.loads((ROOT/"data/phase2-6-sku-d1-body-baselines.json").read_text(encoding="utf8"))["hashes"]
ADDENDA=json.loads((ROOT/"data/phase2-6-sku-locale-addenda.json").read_text(encoding="utf8"))
# Second reviewed 14-model batch; merge at source before CMS-aware rendering.
NEXT14=json.loads((ROOT/"data/phase2-next14-openings-en.json").read_text(encoding="utf8"))["groups"]
assert all(group in EN and not set(models).intersection(EN[group]) for group,models in NEXT14.items())
for group,models in NEXT14.items():
 EN[group].update(models)
NEW_TRANSLATIONS={lang:json.loads((ROOT/f"data/phase2-next14-openings-{lang}.json").read_text(encoding="utf8"))
                  for lang in ("es","pt","ru","tr")}
for slug in (sku for group in NEXT14.values() for sku in group):
 LOCALES[slug]={lang:NEW_TRANSLATIONS[lang][slug] for lang in NEW_TRANSLATIONS}
OWNER.update(json.loads((ROOT/"data/phase2-next14-d1-baselines.json").read_text(encoding="utf8"))["hashes"])
ADDENDA.update(json.loads((ROOT/"data/phase2-next14-locale-addenda.json").read_text(encoding="utf8")))
CATEGORY={"sports":"Plastic Sports Water Bottles","kids":"Kids Plastic Water Bottles",
          "jugs":"Large Capacity Water Jugs"}
SELECTED_GROUP={slug:group for group,items in EN.items() for slug in items}
COPY={slug:{"en":paragraph,**LOCALES[slug]} for group,items in EN.items() for slug,paragraph in items.items()}
for sku,extras in ADDENDA.items():
 for locale,extra in extras.items():
  COPY[sku][locale]=COPY[sku][locale].rstrip()+" "+extra.strip()

def editor_intro(body,row,locale,owner_edited=False):
 if owner_edited:return body
 slug=str(row.get("slug",""))
 paragraph=COPY.get(slug,{}).get(locale)
 if paragraph is None:return body
 if row.get("category")!=CATEGORY[SELECTED_GROUP[slug]]:
  raise ValueError("Second-wave SKU/category mismatch: "+slug)
 if 'data-pilot-intro="'+slug+'"' in body:return body
 if locale!="en":
  baseline=OWNER.get(slug,{}).get(locale)
  if not baseline or sha256(body.encode("utf8")).hexdigest()!=baseline:return body
 h1=re.search(r"<h1\b[^>]*>.*?</h1>",body,re.I|re.S)
 if not h1:return body
 remainder=body[h1.end():]
 original=re.match(r'\s*<p class="copy-muted">[\s\S]*?</p>',remainder)
 if not original:return body
 if slug not in paragraph:raise ValueError("Second-wave model missing: "+slug+"/"+locale)
 rendered='<p class="copy-muted product-buyer-intro" data-pilot-intro="'+escape(slug)+'">'+escape(paragraph)+'</p>'
 return body[:h1.end()]+rendered+remainder[original.end():]