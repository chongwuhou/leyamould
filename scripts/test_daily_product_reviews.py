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
assert count==0 and len(batch)==1
assert batch==Random(1729).sample(entries,1),"Plan must randomly sample, not take the first row"
assert len({r["model"] for r in batch})==1
after=[{"model":r["model"],"published_date":today,"source_row":r["sourceRow"]} for r in batch]
second,count=plan(entries,{"recorded":after,"existingModels":[]},today,rng=Random(8))
assert count==1 and len(second)==1 and second[0]["model"]!=batch[0]["model"]
after += [{"model":r["model"],"published_date":today,"source_row":r["sourceRow"]} for r in second]
third,count=plan(entries,{"recorded":after,"existingModels":[]},today,rng=Random(11))
assert count==2 and len(third)==1 and third[0]["model"] not in {r["model"] for r in after}
after += [{"model":r["model"],"published_date":today,"source_row":r["sourceRow"]} for r in third]
next_batch,count=plan(entries,{"recorded":after,"existingModels":[]},today,rng=Random(12))
assert not next_batch and count==3,"Cannot publish a fourth today"
next_batch,count=plan(entries,{"recorded":after,"existingModels":[r["model"] for r in after]},"2026-10-26",rng=Random(19))
assert count==0 and len(next_batch)==1
assert next_batch[0]["model"] not in {r["model"] for r in after},"No duplicate SKU across days"
one=after[:1]
partial,count=plan(entries,{"recorded":one,"existingModels":[]},today,rng=Random(21))
assert count==1 and len(partial)==1 and partial[0]["model"]!=one[0]["model"]
# The permanent ledger also prevents reuse if an owner deletes the visible review.
future,count=plan(entries,{"recorded":one,"existingModels":[]},"2026-10-27",rng=Random(21))
assert len(future)==1 and one[0]["model"]!=future[0]["model"]
existing={entries[1]["model"],entries[4]["model"]}
batch,count=plan(entries,{"recorded":[],"existingModels":list(existing)},today,rng=Random(123))
assert count==0 and len(batch)==1 and not {r["model"] for r in batch}.intersection(existing)
cron=(ROOT/".github/workflows/publish-three-real-reviews-daily.yml").read_text(encoding="utf8")
for slot in ('17 1 * * *','47 5 * * *','13 11 * * *'):
 assert 'cron: "'+slot+'"' in cron,slot
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