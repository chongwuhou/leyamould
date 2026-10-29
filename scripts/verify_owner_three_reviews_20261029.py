#!/usr/bin/env python3
"""Post-deploy read-only D1 ledger and live product-page proof for owner 3 reviews."""
import json
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parent))
from publish_daily_product_reviews import check_source, request

ROOT = Path(__file__).resolve().parent.parent
RECORD = ROOT / "_local_ops" / "owner-three-reviews-20261029.json"
DATE = "2026-10-29"
BASE = "https://xuyibottles.com"

def verify_one(model):
    from urllib.parse import quote
    slug = model.lower() if model.startswith("LO-") else model
    url = BASE + "/products/" + quote(slug) + "/"
    req = Request(url, headers={"User-Agent": "XUYI-Owner-Reviewed-Live-Verify/1.0", "Cache-Control": "no-cache"})
    with urlopen(req, timeout=25) as res:
        if res.status != 200:
            raise RuntimeError("Product page is not HTTP 200 for model " + model)
        html = res.read().decode("utf8", "replace")
    review = html.split('id="xuyi-customer-reviews"', 1)
    if len(review) != 2 or 'datetime="' + DATE + '"' not in review[1].split("</section>", 1)[0]:
        raise RuntimeError("Expected reviewed date missing on published product page " + model)
    return url

def main():
    import os
    if not os.environ.get("CLOUDFLARE_API_TOKEN"):
        raise RuntimeError("Read-only D1 verification token required")
    if not RECORD.is_file():
        raise RuntimeError("Missing same-run owner publication record")
    record = json.loads(RECORD.read_text("utf8"))
    if record.get("date") != DATE or len(record.get("models", [])) != 3:
        raise RuntimeError("Invalid owner 3-review manifest")
    source = {r["model"]: r for r in check_source()}
    selected = set(record["models"])
    if len(selected) != 3:
        raise RuntimeError("Owner manifest contains duplicate models")
    state = request(os.environ["CLOUDFLARE_API_TOKEN"])
    today = [r for r in state.get("recorded", []) if r.get("published_date") == DATE]
    if {r["model"] for r in today} != selected:
        raise RuntimeError("Published D1 ledger differs from same-run selected models")
    for r in today:
        expected = source[r["model"]]
        if r["source_fingerprint"] != expected["sourceFingerprint"] or r["source_row"] != expected["sourceRow"]:
            raise RuntimeError("Published review does not match exact original Excel record")
    with ThreadPoolExecutor(max_workers=3) as pool:
        links = list(pool.map(verify_one, record["models"]))
    print("XUYI_20261029_THREE_AUTHENTIC_EXCEL_REVIEWS_D1_AND_LIVE_VERIFIED", json.dumps({
        "models": record["models"], "links": links,
    }, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main()