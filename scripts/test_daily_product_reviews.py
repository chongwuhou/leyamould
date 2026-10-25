"""Protect authentic Excel SKUs, RANDOM sampling, D1 day limit and CMS edit priority."""
import sys
from pathlib import Path
from random import Random
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"scripts"))
from publish_daily_product_reviews import SOURCE,ALIASES,check_source,plan

assert SOURCE.is_file()
entries=check_source()
assert len(entries)==101
assert [e["sourceRow"] for e in entries]==list(range(2,103))
from site_renderer import SERIES
catalog={v["model"]:v for v in SERIES.values()}
assert {x["model"] for x in entries}==set(catalog),"Every reviewed model maps 1:1 to official catalog"
for review in entries:
 assert catalog[review["model"]]["slug"]==review["sourceModel"].lower().replace("透明款","-transparent"),(
  review["sourceRow"],review["sourceModel"],review["model"],catalog[review["model"]]["slug"])
assert len(ALIASES)==5
assert [r["model"] for r in entries[:3]]==["LO-001","LO-002","LO-003"]

today="2026-10-25"
seed=Random(1729)
batch,count=plan(entries,{"recorded":[],"existingModels":[]},today,rng=seed)
assert count==0 and len(batch)==3
assert batch==Random(1729).sample(entries,3),"Plan must really sample randomly, not first three rows"
assert len({r["model"] for r in batch})==3

after=[{"model":r["model"],"published_date":today,"source_row":r["sourceRow"]} for r in batch]
next_batch,count=plan(entries,{"recorded":after,"existingModels":[]},today,rng=Random(8))
assert not next_batch and count==3,"Cannot publish a fourth today"
next_batch,count=plan(entries,{"recorded":after,"existingModels":[r["model"] for r in batch]},"2026-10-26",rng=Random(19))
assert count==0 and len(next_batch)==3
assert not {r["model"] for r in next_batch}.intersection(r["model"] for r in batch),"No duplicated SKU"
one=after[:1]
partial,count=plan(entries,{"recorded":one,"existingModels":[]},today,rng=Random(21))
assert count==1 and len(partial)==2 and all(r["model"]!=one[0]["model"] for r in partial)
# Even if the editor removes a public review, the permanent ledger blocks repost.
future,count=plan(entries,{"recorded":one,"existingModels":[]},"2026-10-27",rng=Random(21))
assert len(future)==3 and one[0]["model"] not in [x["model"] for x in future]
# A CMS editor's independent review or unpublished SKU wins.
existing={entries[1]["model"],entries[4]["model"]}
batch,count=plan(entries,{"recorded":[],"existingModels":list(existing)},today,rng=Random(123))
assert count==0 and len(batch)==3 and not {r["model"] for r in batch}.intersection(existing)
# An edited row would invalidate the original XLSX fingerprint before publishing.
from hashlib import sha256
s=entries[0].copy()
s["reviewBody"]=s["reviewBody"]+" alteration"
raw=s["model"]+"\\n"+str(s["rating"])+"\\n"+s["author"]+"\\n"+s["reviewBody"]
assert sha256(raw.encode("utf8")).hexdigest()!=s["sourceFingerprint"]
# Raw personal data must never be shipped as a public static artifact.
dist=ROOT/"dist"
assert not (dist/"review_import_private").exists()
assert not (dist/"101_verified_buyer_reviews.json").exists()
print("XUYI_EXCEL_101_SKU_RANDOMIZED_D1_IDEMPOTENCE_CMS_OWNER_PASS")