#!/usr/bin/env python3
"""One-time owner-approved 3 authentic Excel product reviews, Beijing 2026-11-01.

Only D1 append-only ledger is authoritative. The standing daily one-review
publisher and normal D1 maximum-three rule remain unchanged.
"""
from datetime import datetime
from pathlib import Path
from secrets import SystemRandom
from zoneinfo import ZoneInfo
import json
import os
import sys
import time
from urllib.error import URLError

sys.path.insert(0, str(Path(__file__).resolve().parent))
from publish_daily_product_reviews import check_source, request

DATE = "2026-11-01"
RUN = "XUYI-OWNER-THREE-20261101"
ROOT = Path(__file__).resolve().parent.parent
RECORD = ROOT / "_local_ops" / "owner-three-reviews-20261101.json"

def actual_state(token):
    for attempt in range(4):
        try:
            return request(token)
        except (URLError, TimeoutError, RuntimeError) as error:
            text = str(error)
            # Only transient server conditions are retried. Auth and input
            # failures must not be replayed or masked.
            if not any(x in text for x in ("HTTP 429", "HTTP 502", "HTTP 503", "HTTP 504", "timed out")) or attempt == 3:
                raise
            time.sleep((4, 8, 12)[attempt])

def verify_rows(entries, state):
    expected = {x["model"]: x for x in entries}
    published = [r for r in state.get("recorded", []) if r.get("published_date") == DATE]
    if len(published) != 3 or len({x["model"] for x in published}) != 3:
        raise RuntimeError("Expected exactly 3 unique D1-reviewed records for this Beijing date")
    for row in published:
        source = expected.get(row["model"])
        if (source is None
            or source["sourceFingerprint"] != row["source_fingerprint"]
            or source["sourceRow"] != row["source_row"]
            or source["sourceModel"] != row["source_model"]):
            raise RuntimeError("D1 ledger is inconsistent with the original Excel: " + row["model"])
    return sorted(published, key=lambda x: x["source_row"])

def persist(rows, revision):
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps({
        "date": DATE,
        "models": [r["model"] for r in rows],
        "sourceRows": [r["source_row"] for r in rows],
        "publishRevision": revision,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf8")

def main():
    entries = check_source()
    assert len(entries) == 101 and len({x["model"] for x in entries}) == 101
    if "--dry-run" in sys.argv:
        assert len(entries) == 101
        print("OWNER_THREE_101_EXCEL_SOURCE_VALIDATED_NO_WRITE", flush=True)
        return
    if not (
        os.environ.get("GITHUB_ACTIONS") == "true"
        and os.environ.get("GITHUB_EVENT_NAME") == "push"
        and os.environ.get("GITHUB_REF") == "refs/heads/main"
        and os.environ.get("GITHUB_REPOSITORY") == "chongwuhou/xuyi-drinkware-site"
        and os.environ.get("OWNER_THREE_RELEASE") == "1"
    ):
        raise RuntimeError("Only explicitly authorized XUYI GitHub main push may publish reviews")
    if datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat() != DATE:
        raise RuntimeError("One-time owner authorization expires at end of 2026-11-01 Beijing date")
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        raise RuntimeError("XUYI Cloudflare credential not available")
    state = actual_state(token)
    if state.get("today") != DATE:
        raise RuntimeError("Beijing date mismatch between D1 and GitHub")
    today = [r for r in state.get("recorded", []) if r.get("published_date") == DATE]
    if today:
        if len(today) != 3:
            raise RuntimeError("Other reviews already exist today; cannot safely publish exactly three")
        verified = verify_rows(entries, state)
        persist(verified, None)
        print("OWNER_THREE_ALREADY_IN_D1_NO_REPLAY", [x["model"] for x in verified], flush=True)
        return
    occupied = set(state.get("existingModels", [])) | {r["model"] for r in state["recorded"]}
    candidates = [x for x in entries if x["model"] not in occupied]
    if len(candidates) < 3:
        raise RuntimeError("Fewer than three unused, exact-SKU Excel reviews remain")
    selected = SystemRandom().sample(candidates, 3)
    rows = [{
        "sourceRow": x["sourceRow"],
        "sourceModel": x["sourceModel"],
        "model": x["model"],
        "rating": x["rating"],
        "author": x["author"],
        "content": x["reviewBody"],
        "sourceFingerprint": x["sourceFingerprint"],
    } for x in selected]
    print("OWNER_RANDOM_THREE_EXCEL_MODELS", [x["model"] for x in rows], flush=True)
    result = request(token, "POST", {
        "date": DATE,
        "confirmedAuthentic": True,
        "items": rows,
    })
    if result.get("success") is not True or result.get("inserted") != 3 or result.get("todayCount") != 3:
        raise RuntimeError("Ambiguous D1 commit. Read ledger before retry, do not resend blindly")
    state = actual_state(token)
    verified = verify_rows(entries, state)
    if {r["model"] for r in verified} != {x["model"] for x in rows}:
        raise RuntimeError("D1 published models do not match the three selected Excel models")
    persist(verified, result.get("revision"))
    print("OWNER_THREE_EXACT_EXCEL_REVIEWS_PUBLISHED_TO_D1", [x["model"] for x in verified],
          "REVISION", result.get("revision"), flush=True)

if __name__ == "__main__":
    main()