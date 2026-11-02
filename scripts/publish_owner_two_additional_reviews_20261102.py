#!/usr/bin/env python3
"""One-time publication of two new reviews from the additional 2026-11-02 workbook.

The selected rows were checked against the old workbook and live product pages.
sourceRow is a globally unique ledger key: 1000 + the original Excel row.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from urllib.error import URLError
from zoneinfo import ZoneInfo
import json
import os
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "review_import_private" / "owner-two-additional-reviews-20261102.json"
RECORD = ROOT / "_local_ops" / "owner-two-additional-reviews-20261102.json"
DATE = "2026-11-02"
REPOSITORY = "chongwuhou/xuyi-drinkware-site"

sys.path.insert(0, str(ROOT / "scripts"))
from publish_daily_product_reviews import request


def load_manifest():
    data = json.loads(MANIFEST.read_text(encoding="utf8"))
    if data.get("schemaVersion") != 1 or data.get("date") != DATE:
        raise RuntimeError("Invalid additional-review manifest version/date")
    if data.get("sourceFile") != "101-additional-reviews-only.xlsx":
        raise RuntimeError("Unexpected additional-review source file")
    items = data.get("items")
    if not isinstance(items, list) or len(items) != 2:
        raise RuntimeError("This one-time release must contain exactly two reviews")
    models, rows, fingerprints = set(), set(), set()
    for item in items:
        model = item.get("model", "")
        source_model = item.get("sourceModel", "")
        excel_row = item.get("excelRow")
        source_row = item.get("sourceRow")
        rating = item.get("rating")
        author = item.get("author", "")
        content = item.get("content", "")
        if not model or model != source_model:
            raise RuntimeError("This release only accepts exact, non-alias model matches")
        if not isinstance(excel_row, int) or not 2 <= excel_row <= 102:
            raise RuntimeError("Original Excel row is invalid")
        if source_row != 1000 + excel_row or not 2 <= source_row <= 2000:
            raise RuntimeError("Global D1 source-row mapping is invalid")
        if source_row in rows or model in models:
            raise RuntimeError("Duplicate source row or product model in selected batch")
        if type(rating) is not int or not 1 <= rating <= 5:
            raise RuntimeError("Customer rating is invalid")
        if not isinstance(author, str) or not 2 <= len(author) <= 99:
            raise RuntimeError("Customer author is invalid")
        if not isinstance(content, str) or not 12 <= len(content) <= 3000:
            raise RuntimeError("Customer review content is invalid")
        raw = model + "\n" + str(rating) + "\n" + author + "\n" + content
        fingerprint = sha256(raw.encode("utf8")).hexdigest()
        if fingerprint != item.get("sourceFingerprint"):
            raise RuntimeError("Review content fingerprint does not match the selected Excel row")
        if fingerprint in fingerprints:
            raise RuntimeError("Duplicate review fingerprint in selected batch")
        rows.add(source_row)
        models.add(model)
        fingerprints.add(fingerprint)
    return data, items


def state_read(token):
    for attempt in range(4):
        try:
            return request(token)
        except (URLError, TimeoutError, RuntimeError) as error:
            message = str(error)
            transient = ("HTTP 429", "HTTP 502", "HTTP 503", "HTTP 504", "timed out")
            if attempt == 3 or not any(value in message for value in transient):
                raise
            time.sleep((4, 8, 12)[attempt])
    raise RuntimeError("Unable to read the XUYI D1 review ledger")


def main():
    manifest, items = load_manifest()
    if "--dry-run" in sys.argv:
        print("XUYI_ADDITIONAL_TWO_REVIEW_MANIFEST_VALIDATED_NO_WRITE",
              [(x["excelRow"], x["model"]) for x in items], flush=True)
        return

    if not (
        os.environ.get("GITHUB_ACTIONS") == "true"
        and os.environ.get("GITHUB_EVENT_NAME") == "push"
        and os.environ.get("GITHUB_REF") == "refs/heads/main"
        and os.environ.get("GITHUB_REPOSITORY") == REPOSITORY
        and os.environ.get("OWNER_TWO_ADDITIONAL_RELEASE") == "1"
    ):
        raise RuntimeError("Only the exact owner-approved main-branch release may publish")
    if datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat() != DATE:
        raise RuntimeError("The one-time additional-review authorization has expired")
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if not token:
        raise RuntimeError("XUYI Cloudflare credential is unavailable")

    state = state_read(token)
    if state.get("today") != DATE:
        raise RuntimeError("D1 and GitHub Beijing dates do not match")

    ledger = state.get("recorded", [])
    today_rows = [row for row in ledger if row.get("published_date") == DATE]
    if len(today_rows) + len(items) > 3:
        raise RuntimeError("Adding two reviews would exceed the D1 three-per-day limit")

    occupied_models = set(state.get("existingModels", [])) | {
        row.get("model") for row in ledger
    }
    used_source_rows = {int(row["source_row"]) for row in ledger}
    used_fingerprints = {row.get("source_fingerprint") for row in ledger}

    for item in items:
        if item["model"] in occupied_models:
            raise RuntimeError("Selected SKU already has a review or ledger entry: " + item["model"])
        if item["sourceRow"] in used_source_rows:
            raise RuntimeError("Global source-row key already exists; no write attempted")
        if item["sourceFingerprint"] in used_fingerprints:
            raise RuntimeError("Review fingerprint already exists in the permanent D1 ledger")

    batch = [{
        "sourceRow": item["sourceRow"],
        "sourceModel": item["sourceModel"],
        "model": item["model"],
        "rating": item["rating"],
        "author": item["author"],
        "content": item["content"],
        "sourceFingerprint": item["sourceFingerprint"],
    } for item in items]

    result = request(token, "POST", {
        "date": DATE,
        "confirmedAuthentic": True,
        "items": batch,
    })
    expected_today = len(today_rows) + 2
    if (
        result.get("success") is not True
        or result.get("inserted") != 2
        or result.get("todayCount") != expected_today
    ):
        raise RuntimeError("D1 write result is ambiguous; inspect the ledger before any retry")

    latest = state_read(token)
    if latest.get("today") != DATE or len(latest.get("recorded", [])) != len(ledger) + 2:
        raise RuntimeError("D1 ledger total did not increase by exactly two")
    published_today = [
        row for row in latest.get("recorded", [])
        if row.get("published_date") == DATE
    ]
    by_model = {row.get("model"): row for row in published_today}
    if len(published_today) != expected_today:
        raise RuntimeError("Unexpected Beijing-day ledger count after publication")
    for item in items:
        stored = by_model.get(item["model"])
        if not stored or (
            stored.get("source_row") != item["sourceRow"]
            or stored.get("source_model") != item["sourceModel"]
            or stored.get("source_fingerprint") != item["sourceFingerprint"]
        ):
            raise RuntimeError("D1 ledger does not match the exact selected Excel row")

    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps({
        "date": DATE,
        "models": [item["model"] for item in items],
        "excelRows": [item["excelRow"] for item in items],
        "sourceRows": [item["sourceRow"] for item in items],
        "sourceFingerprints": [item["sourceFingerprint"] for item in items],
        "publishRevision": result.get("revision"),
        "previousD1Total": len(ledger),
        "d1Total": len(latest["recorded"]),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("XUYI_20261102_TWO_ADDITIONAL_EXCEL_REVIEWS_PUBLISHED_TO_D1",
          json.dumps({
              "models": [item["model"] for item in items],
              "excelRows": [item["excelRow"] for item in items],
              "todayCount": expected_today,
              "d1Total": len(latest["recorded"]),
              "publishRevision": result.get("revision"),
          }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
