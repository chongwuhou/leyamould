#!/usr/bin/env python3
"""One-time owner-requested four authentic Excel reviews on Beijing 2026-10-28.

Never alters the standing one-review daily schedule. D1's append-only ledger
and atomic insert protect against replays, removed reviews and duplicate SKUs.
"""
from datetime import datetime
from pathlib import Path
from secrets import SystemRandom
from zoneinfo import ZoneInfo
import json
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from publish_daily_product_reviews import check_source, request

DATE = "2026-10-28"
OWNER_BATCH = "xuyi-owner-random-four-20261028"

def main():
    entries = check_source()
    if "--dry-run" in sys.argv:
        print("OWNER_FOUR_SOURCE_VALIDATED", len(entries), "NO_D1_WRITE")
        return
    if (os.environ.get("GITHUB_ACTIONS") != "true"
            or os.environ.get("GITHUB_EVENT_NAME") != "push"
            or os.environ.get("GITHUB_REF") != "refs/heads/main"
            or os.environ.get("GITHUB_REPOSITORY") != "chongwuhou/xuyi-drinkware-site"):
        raise RuntimeError("Only the XUYI GitHub main push workflow may publish.")
    if datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat() != DATE:
        raise RuntimeError("Owner-approved batch is valid only on 2026-10-28 Beijing date.")
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if not token:
        raise RuntimeError("Cloudflare deployment credential unavailable.")
    state = request(token)
    if state.get("today") != DATE:
        raise RuntimeError("D1 date does not match Beijing date.")
    ledger = state.get("recorded", [])
    prior_rows = [r for r in ledger if r.get("published_date") == DATE]
    if len(prior_rows) >= 4:
        print("ONE_TIME_BATCH_NOT_REPLAYED", DATE, "TODAY_ALREADY", len(prior_rows))
        return
    if len(prior_rows) > 1:
        raise RuntimeError("Other reviews already exist today; cannot safely add four.")
    occupied = set(state.get("existingModels", [])) | {
        r["model"] for r in ledger
    }
    eligible = [x for x in entries if x["model"] not in occupied]
    if len(eligible) < 4:
        raise RuntimeError("Fewer than four unused, exact-SKU source reviews remain.")
    selected = SystemRandom().sample(eligible, 4)
    rows = [{
        "sourceRow": x["sourceRow"], "sourceModel": x["sourceModel"],
        "model": x["model"], "rating": x["rating"], "author": x["author"],
        "content": x["reviewBody"], "sourceFingerprint": x["sourceFingerprint"],
    } for x in selected]
    print("OWNER_RANDOM_FOUR_SELECTED_MODELS", [x["model"] for x in rows])
    response = request(token, "POST", {
        "date": DATE, "items": rows, "confirmedAuthentic": True,
        "ownerBatch": OWNER_BATCH
    })
    if (response.get("success") is not True
            or response.get("inserted") != 4
            or response.get("todayCount") != len(prior_rows) + 4):
        raise RuntimeError("D1 commit outcome needs ledger inspection before retry.")
    confirmed = {(r["model"], r["source_row"], r["published_date"])
                 for r in response.get("recorded", [])}
    if not all((x["model"], x["sourceRow"], DATE) in confirmed for x in rows):
        raise RuntimeError("D1 ledger reconciliation failed.")
    print("FOUR_EXCEL_REVIEWS_PUBLISHED_TO_D1",
          [x["model"] for x in rows], "revision", response.get("revision"))

if __name__ == "__main__":
    main()
