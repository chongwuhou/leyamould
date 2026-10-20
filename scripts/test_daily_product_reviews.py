"""Protect all 101 exact Excel SKU associations and daily D1 deduplication."""
import sys
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
batch,count=plan(entries,{"recorded":[],"existingModels":[]},today)
assert count==0 and [x["model"] for x in batch]==["LO-001","LO-002","LO-003"]
after=[{"model":x["model"],"published_date":today,"source_row":x["sourceRow"]} for x in batch]
next_batch,count=plan(entries,{"recorded":after,"existingModels":[]},today)
assert next_batch==[] and count==3,"Second run same day cannot publish more"
next_batch,count=plan(entries,{"recorded":after,"existingModels":[x["model"] for x in batch]},"2026-10-21")
assert [x["model"] for x in next_batch]==["LO-004","LO-005","LO-006"],"Next day must skip published SKU"
one=[after[0]]
batch,count=plan(entries,{"recorded":one,"existingModels":[]},today)
assert count==1 and [x["model"] for x in batch]==["LO-002","LO-003"],"Resume partial day safely"
# Even if an editor deletes public review content, the forever ledger wins.
after_only=[after[0]]
batch,count=plan(entries,{"recorded":after_only,"existingModels":[]},"2026-10-22")
assert "LO-001" not in [x["model"] for x in batch]
# An editor's independent review or unpublished draft for an SKU wins.
batch,count=plan(entries,{"recorded":[],"existingModels":["LO-002"]},today)
assert [x["model"] for x in batch]==["LO-001","LO-003","LO-004"]
# Raw personal data MUST NOT appear as a direct static file on the live site.
dist=ROOT/"dist"
assert not (dist/"review_import_private").exists(),"Unpublished reviewer PII leaked into static Pages"
assert not (dist/"101_verified_buyer_reviews.json").exists()
print("XUYI_EXCEL_101_SKU_EXACT_MATCH_5_APPROVED_ALIASES_D1_DATE_IDEMPOTENCE_PASS")
