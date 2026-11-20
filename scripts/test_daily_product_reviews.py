"""Protect both Excel sources, multi-review-per-SKU behavior and D1 idempotence."""
import sys
import os
from collections import Counter
from pathlib import Path
from random import Random
ROOT=Path(__file__).resolve().parent.parent
SNAPSHOT=ROOT/"_local_ops"/"build-snapshot.json"
if SNAPSHOT.is_file():
 os.environ["LEYA_BUILD_SNAPSHOT"]=str(SNAPSHOT)
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/"scripts"))
from publish_daily_product_reviews import SOURCE_FILES,ALIASES,check_source,plan,EXCLUDED_SOURCE_ROWS

assert all(path.is_file() for path,_,_ in SOURCE_FILES)
entries=check_source()
assert len(entries)==201 and len({x["model"] for x in entries})==101
assert Counter(x["sourceFile"] for x in entries)=={"101-zhenshipingjia.xlsx":101,"101-additional-reviews-only.xlsx":100}
assert len({x["sourceFingerprint"] for x in entries})==201
assert len(ALIASES)==5 and EXCLUDED_SOURCE_ROWS=={("101-additional-reviews-only.xlsx",59)}
assert not any(x["sourceFile"]=="101-additional-reviews-only.xlsx" and x["sourceRow"]==59 for x in entries)
import json
second=json.loads((ROOT/"review_import_private"/"101_additional_verified_buyer_reviews.json").read_text(encoding="utf8"))
second59=next(x for x in second["reviews"] if x["sourceRow"]==59)
first59=next(x for x in entries if x["sourceFile"]=="101-zhenshipingjia.xlsx" and x["sourceRow"]==59)
assert (first59["model"],first59["author"])==("2319","Beatriz Santos")
assert (second59["model"],second59["author"])==("2319","Beatriz Santos")
from site_renderer import SERIES
catalog={v["model"]:v for v in SERIES.values()}
# Authentic review rows cover only SKUs present in the source spreadsheets.
# A larger D1 catalogue must not require fabricated reviews for every product.
assert {x["model"] for x in entries}.issubset(set(catalog))
for r in entries:
 assert catalog[r["model"]]["slug"]==r["sourceModel"].lower().replace("透明款","-transparent"),(r["sourceFile"],r["sourceRow"],r["model"])
same=[x for x in entries if x["model"]=="LO-001"]
assert len(same)==2 and same[0]["author"]!=same[1]["author"]
today="2026-11-02"
batch,count=plan(entries,{"recorded":[],"publishedFingerprints":[]},today,rng=Random(1729),limit=3)
assert count==0 and batch==Random(1729).sample(entries,3)
backend_five,count=plan(entries,{"recorded":[],"publishedFingerprints":[]},today,rng=Random(1729),limit=5)
assert count==0 and len(backend_five)==5,"The review batch size follows the D1-provided backend quota, not a hard-coded three."
after=[{"source_fingerprint":x["sourceFingerprint"],"source_file":x["sourceFile"],"source_row":x["sourceRow"],"published_date":today} for x in batch]
assert plan(entries,{"recorded":after,"publishedFingerprints":[]},today,rng=Random(8),limit=3)==([],3)
next_batch,count=plan(entries,{"recorded":after,"publishedFingerprints":[]},"2026-11-03",rng=Random(19),limit=3)
assert count==0 and len(next_batch)==3
assert not {x["sourceFingerprint"] for x in next_batch}.intersection(x["source_fingerprint"] for x in after)
first,second=same
partial,count=plan([first,second],{"recorded":[{"source_fingerprint":first["sourceFingerprint"],"published_date":today}],"publishedFingerprints":[first["sourceFingerprint"]]},"2026-11-03",rng=Random(21),limit=3)
assert partial==[second],"A second customer review for the same SKU remains eligible"
manual,count=plan([first,second],{"recorded":[],"existingModels":["LO-001"],"publishedFingerprints":[]},"2026-11-03",rng=Random(7),limit=3)
assert count==0 and len(manual)==2,"Existing SKU reviews must not block different source reviews"
dup,count=plan([first,second],{"recorded":[],"publishedFingerprints":[first["sourceFingerprint"]]},"2026-11-03",rng=Random(3),limit=3)
assert first not in dup and second in dup
from hashlib import sha256
s=entries[0].copy();s["reviewBody"]+=" alteration"
raw=s["model"]+"\n"+str(s["rating"])+"\n"+s["author"]+"\n"+s["reviewBody"]
assert sha256(raw.encode("utf8")).hexdigest()!=s["sourceFingerprint"]
dist=ROOT/"dist"
assert not (dist/"review_import_private").exists()
assert not (dist/"101_verified_buyer_reviews.json").exists()
assert not (dist/"101_additional_verified_buyer_reviews.json").exists()
print("XUYI_TWO_EXCEL_201_AUTHENTIC_REVIEWS_MULTI_SKU_D1_IDEMPOTENCE_PASS")