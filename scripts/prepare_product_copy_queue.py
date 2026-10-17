#!/usr/bin/env python3
"""Rank remaining catalog models by copy duplication and source completeness.

Produces an offline editorial queue; it never edits product pages or D1.
The manual source-reviewed shortlist is ranked ahead of generic candidates.
"""
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES
from sku_unique_openings import COPY as PILOT
from sku_unique_openings_phase2 import COPY as PHASE2
PRIORITY=() # Only evidence-incomplete SKUs remain; request verified factory facts before copy.
HOLD={"5247":"Same nominal dimensions and components as 5248: confirm a genuine model-specific difference first",
      "5248":"Same nominal dimensions and components as 5247: confirm a genuine model-specific difference first",
      "2506":"Source says anomalous 60 ml; factory capacity confirmation required"}
def write_queue(rows,target):
 with target.open("w",newline="",encoding="utf-8-sig") as f:
  columns=("rank","category","sku","nearest_main_jaccard","capacity_source","dimensions_source","material_source","colors_source","image_reference","detail_url","decision")
  w=csv.DictWriter(f,fieldnames=columns)
  w.writeheader();w.writerows(rows)
def main():
 a=json.loads((ROOT/"_local_ops/product-body-similarity-2026-10-14.json").read_text(encoding="utf8"))
 scores={r["sku"]:r["nearest_main"] for r in a["rows"] if r["locale"]=="en"}
 model_map={r["slug"]:r for r in SERIES.values()}
 assert set(PRIORITY).issubset(model_map)
 assert not set(PRIORITY).intersection(set(PILOT)|set(PHASE2))
 rows=[]
 for sku,r in model_map.items():
  if sku in PILOT or sku in PHASE2:continue
  if sku in PRIORITY:rank=PRIORITY.index(sku)+1;decision="NEXT: verify photo/lid then write distinct five-language buyer intro"
  elif sku in HOLD:rank=900;decision="HOLD: "+HOLD[sku]
  elif sku.startswith("g-"):rank=950;decision="HOLD: G-series verified factory model but capacity/components not confirmed"
  elif sku.startswith("lo-"):rank=850;decision="REVIEW: confirm original catalog and individual lid/shape evidence"
  else:rank=100;decision="REVIEW AFTER NEXT BATCH: compare real model dimensions, photos, materials"
  rows.append(dict(rank=rank,category=r["category"],sku=sku,nearest_main_jaccard=scores[sku],
   capacity_source=r.get("capacity") or "",dimensions_source=r.get("dimensions") or "",
   material_source=r.get("material") or "",colors_source=r.get("colors") or "",
   image_reference=(r.get("images") or [""])[0],
   detail_url="https://xuyibottles.com/products/"+sku+"/",decision=decision))
 rows.sort(key=lambda r:(r["rank"],-r["nearest_main_jaccard"],r["category"],r["sku"]))
 assert len(rows)==len(SERIES)-len(PILOT)-len(PHASE2)
 target=ROOT/"_local_ops/phase2-remaining-sku-priority.csv"
 write_queue(rows,target)
 pending=json.loads((ROOT/"data/phase8-factory-fact-verification-pending.json").read_text(encoding="utf8"))["items"]
 print("REMAINING_PRODUCT_EDITORIAL_QUEUE",len(rows),"manual_next",len(PRIORITY),"FACTORY_VERIFICATION_PENDING",sum(x["verificationStatus"]=="pending_factory" for x in pending))
 print("FILE",target)
if __name__=="__main__":main()
