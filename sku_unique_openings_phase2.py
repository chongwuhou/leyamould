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
# Third audited 14-model batch, merged before CMS-aware source rendering.
THIRD=json.loads((ROOT/"data/phase3-next14-openings-en.json").read_text(encoding="utf8"))["groups"]
assert all(group in EN and not set(models).intersection(EN[group]) for group,models in THIRD.items())
for group,models in THIRD.items():
 EN[group].update(models)
THIRD_TRANSLATIONS={lang:json.loads((ROOT/f"data/phase3-next14-openings-{lang}.json").read_text(encoding="utf8"))
                    for lang in ("es","pt","ru","tr")}
for slug in (sku for group in THIRD.values() for sku in group):
 LOCALES[slug]={lang:THIRD_TRANSLATIONS[lang][slug] for lang in THIRD_TRANSLATIONS}
OWNER.update(json.loads((ROOT/"data/phase3-next14-d1-baselines.json").read_text(encoding="utf8"))["hashes"])
ADDENDA.update(json.loads((ROOT/"data/phase3-next14-locale-addenda.json").read_text(encoding="utf8")))
# Fourth source-reviewed 14-model batch, merged before D1-aware rendering.
FOURTH=json.loads((ROOT/"data/phase4-next14-openings-en.json").read_text(encoding="utf8"))["groups"]
assert all(group in EN and not set(models).intersection(EN[group]) for group,models in FOURTH.items())
for group,models in FOURTH.items():
 EN[group].update(models)
FOURTH_TRANSLATIONS={lang:json.loads((ROOT/f"data/phase4-next14-openings-{lang}.json").read_text(encoding="utf8"))
                     for lang in ("es","pt","ru","tr")}
for slug in (sku for group in FOURTH.values() for sku in group):
 LOCALES[slug]={lang:FOURTH_TRANSLATIONS[lang][slug] for lang in FOURTH_TRANSLATIONS}
OWNER.update(json.loads((ROOT/"data/phase4-next14-d1-baselines.json").read_text(encoding="utf8"))["hashes"])
ADDENDA.update(json.loads((ROOT/"data/phase4-next14-locale-addenda.json").read_text(encoding="utf8")))
# Fifth evidence-reviewed 14-model batch: always merge at source before CMS-aware renderer.
FIFTH=json.loads((ROOT/"data/phase5-next14-openings-en.json").read_text(encoding="utf8"))["groups"]
assert all(group in EN and not set(models).intersection(EN[group]) for group,models in FIFTH.items())
for group,models in FIFTH.items():
 EN[group].update(models)
FIFTH_TRANSLATIONS={lang:json.loads((ROOT/f"data/phase5-next14-openings-{lang}.json").read_text(encoding="utf8"))
                    for lang in ("es","pt","ru","tr")}
for slug in (sku for group in FIFTH.values() for sku in group):
 LOCALES[slug]={lang:FIFTH_TRANSLATIONS[lang][slug] for lang in FIFTH_TRANSLATIONS}
OWNER.update(json.loads((ROOT/"data/phase5-next14-d1-baselines.json").read_text(encoding="utf8"))["hashes"])
ADDENDA.update(json.loads((ROOT/"data/phase5-next14-locale-addenda.json").read_text(encoding="utf8")))
# Sixth reviewed batch: LO source-photo products use a pinned native-template
# baseline (not D1); a later CMS-owned body cannot be replaced by this copy.
LO_BATCH=json.loads((ROOT/"data/phase6-lo8-openings-en.json").read_text(encoding="utf8"))["groups"]
assert all(group in EN and not set(items).intersection(EN[group]) for group,items in LO_BATCH.items())
for group,items in LO_BATCH.items():
 EN[group].update(items)
LO_LANGS={lang:json.loads((ROOT/f"data/phase6-lo8-openings-{lang}.json").read_text(encoding="utf8"))
          for lang in ("es","pt","ru","tr")}
for slug in (model for group in LO_BATCH.values() for model in group):
 LOCALES[slug]={lang:LO_LANGS[lang][slug] for lang in LO_LANGS}
OWNER.update(json.loads((ROOT/"data/phase6-lo8-template-baselines.json").read_text(encoding="utf8"))["hashes"])
ADDENDA.update(json.loads((ROOT/"data/phase6-lo8-locale-addenda.json").read_text(encoding="utf8")))
# Seventh source-photo batch: eight verified G-series factory model IDs.
# No unconfirmed capacity, dimensions, material, tests or stock is asserted.
G_BATCH=json.loads((ROOT/"data/phase7-g8-buyer-guides-en.json").read_text(encoding="utf8"))["groups"]
assert all(group in EN and not set(models).intersection(EN[group]) for group,models in G_BATCH.items())
for group,models in G_BATCH.items():
 EN[group].update(models)
G_TRANSLATIONS={lang:json.loads((ROOT/f"data/phase7-g8-buyer-guides-{lang}.json").read_text(encoding="utf8"))
                for lang in ("es","pt","ru","tr")}
for slug in (sku for group in G_BATCH.values() for sku in group):
 LOCALES[slug]={lang:G_TRANSLATIONS[lang][slug] for lang in G_TRANSLATIONS}
OWNER.update(json.loads((ROOT/"data/phase7-g8-gallery-template-baselines.json").read_text(encoding="utf8"))["hashes"])
ADDENDA.update(json.loads((ROOT/"data/phase7-g8-buyer-guides-addenda.json").read_text(encoding="utf8")))
# Eighth closing batch: source-discrepancy-safe buyer guides for the last
# three catalog IDs. Copy is unique, but underlying factory facts stay held.
LAST3=json.loads((ROOT/"data/phase8-last3-buyer-intros-en.json").read_text(encoding="utf8"))["groups"]
assert all(group in ("sports","shakers") and (group not in EN or not set(items).intersection(EN[group])) for group,items in LAST3.items())
for group,items in LAST3.items():
 EN.setdefault(group,{}).update(items)
LAST3_LANGS={loc:json.loads((ROOT/f"data/phase8-last3-buyer-intros-{loc}.json").read_text(encoding="utf8"))
             for loc in ("es","pt","ru","tr")}
for slug in (sku for group in LAST3.values() for sku in group):
 LOCALES[slug]={loc:LAST3_LANGS[loc][slug] for loc in LAST3_LANGS}
OWNER.update(json.loads((ROOT/"data/phase8-last3-d1-baselines.json").read_text(encoding="utf8"))["hashes"])
CATEGORY={"sports":"Plastic Sports Water Bottles","kids":"Kids Plastic Water Bottles",
          "jugs":"Large Capacity Water Jugs","shakers":"Plastic Shaker Bottles"}
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
 if slug.casefold() not in paragraph.casefold():raise ValueError("Reviewed model missing: "+slug+"/"+locale)
 rendered='<p class="copy-muted product-buyer-intro" data-pilot-intro="'+escape(slug)+'">'+escape(paragraph)+'</p>'
 return body[:h1.end()]+rendered+remainder[original.end():]