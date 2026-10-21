"""Protect all 101 exact Excel SKU associations and daily D1 deduplication."""
import sys
from random import Random
from pathlib import Path
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
assert {x["model"] for x in entries}==set(catalog),"Every reviewed model maps 1:1 to the official catalog"
for r in entries:
 assert catalog[r["model"]]["slug"]==r["sourceModel"].lower().replace("透明款","-transparent"),(
  r["sourceRow"],r["sourceModel"],r["model"],catalog[r["model"]]["slug"])
assert len(ALIASES)==5
assert [r["model"] for r in entries[:3]]==["LO-001","LO-002","LO-003"]
today="2026-10-20"
seed=Random(20261021)
batch,count=plan(entries,{"recorded":[],"existingModels":[]},today,rng=seed)
assert count==0 and len(batch)==3 and len({x["model"] for x in batch})==3
assert set(x["model"] for x in batch).issubset({x["model"] for x in entries})
assert [x["sourceRow"] for x in batch]!=[2,3,4],"Publisher must not take first three Excel rows"
# Fixed seeds only test the random sampler; no seed is passed in production.
different,_=plan(entries,{"recorded":[],"existingModels":[]},today,rng=Random(3))
assert {x["model"] for x in different}!={x["model"] for x in batch}
after=[{"model":x["model"],"published_date":today,"source_row":x["sourceRow"]} for x in batch]
next_batch,count=plan(entries,{"recorded":after,"existingModels":[]},today,rng=Random(1))
assert next_batch==[] and count==3,"Second run same day cannot publish more"
next_batch,count=plan(entries,{"recorded":after,"existingModels":[x["model"] for x in batch]},"2026-10-21",rng=Random(1))
assert len(next_batch)==3 and not ({x["model"] for x in next_batch}&{x["model"] for x in batch})
one=[after[0]]
partial,count=plan(entries,{"recorded":one,"existingModels":[]},today,rng=Random(2))
assert count==1 and len(partial)==2 and all(x["model"]!=one[0]["model"] for x in partial)
# An editor's independent review or unpublished draft always wins.
owner_existing=entries[1]["model"]
owner_batch,count=plan(entries,{"recorded":[],"existingModels":[owner_existing]},today,rng=Random(2))
assert len(owner_batch)==3 and owner_existing not in {x["model"] for x in owner_batch}
# A permanent ledger prevents re-publication even if the visible review is deleted.
after_only=[after[0]]
batch2,count=plan(entries,{"recorded":after_only,"existingModels":[]},"2026-10-22",rng=Random(2))
assert after_only[0]["model"] not in {x["model"] for x in batch2}
# Only as many still-unpublished records as exist may be selected.
nearly_all=[{"model":r["model"],"published_date":"2026-10-19"} for r in entries[:-1]]
last,count=plan(entries,{"recorded":nearly_all,"existingModels":[]},"2026-10-21",rng=Random(2))
assert len(last)==1 and last[0]["model"]==entries[-1]["model"]
empty,count=plan(entries,{"recorded":[{"model":r["model"],"published_date":"2026-10-19"} for r in entries],"existingModels":[]},"2026-10-21",rng=Random(2))
assert empty==[] and count==0
# Raw personal data MUST NOT appear as a direct static file on the live site.
dist=ROOT/"dist"
assert not (dist/"review_import_private").exists(),"Unpublished reviewer PII leaked into static Pages"
assert not (dist/"101_verified_buyer_reviews.json").exists()
print("XUYI_EXCEL_101_SKU_AUTHENTIC_RANDOM_SAMPLING_D1_DATE_DEDUP_OWNER_PRIORITY_PASS")
