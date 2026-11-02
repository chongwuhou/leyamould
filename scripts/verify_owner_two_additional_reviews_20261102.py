#!/usr/bin/env python3
"""Read-only D1 and live-page verification for the 2026-11-02 additional reviews."""
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
import json
import os
import sys

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "review_import_private" / "owner-two-additional-reviews-20261102.json"
RECORD = ROOT / "_local_ops" / "owner-two-additional-reviews-20261102.json"
DATE = "2026-11-02"

sys.path.insert(0, str(ROOT / "scripts"))
from publish_daily_product_reviews import request


class ReviewParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_section = False
        self.current = None
        self.field = None
        self.reviews = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section" and attrs.get("id") == "xuyi-customer-reviews":
            self.in_section = True
        if not self.in_section:
            return
        if tag == "article" and "product-review" in attrs.get("class", "").split():
            self.current = {"author": "", "content": "", "date": ""}
        elif self.current is not None:
            if tag == "p" and "product-review__text" in attrs.get("class", "").split():
                self.field = "content"
            elif tag == "p" and "product-review__meta" in attrs.get("class", "").split():
                self.field = "meta"
            elif tag == "strong" and self.field == "meta":
                self.field = "author"
            elif tag == "time" and self.field == "meta":
                self.current["date"] = attrs.get("datetime", "")

    def handle_data(self, data):
        if self.current is not None and self.field in ("author", "content"):
            self.current[self.field] += data

    def handle_endtag(self, tag):
        if self.current is None:
            if tag == "section" and self.in_section:
                self.in_section = False
            return
        if tag == "strong" and self.field == "author":
            self.field = "meta"
        elif tag == "p" and self.field in ("content", "meta"):
            self.field = None
        elif tag == "article":
            self.reviews.append({k: v.strip() for k, v in self.current.items()})
            self.current = None
            self.field = None
        elif tag == "section":
            self.in_section = False


def verify_live_page(item):
    model = item["sourceModel"]
    slug = model.lower() if model.startswith(("LO-", "G-")) else model
    url = "https://xuyibottles.com/products/" + quote(slug, safe="-_") + "/"
    req = Request(url, headers={
        "User-Agent": "XUYI-Additional-Review-Live-Verify/1.0",
        "Cache-Control": "no-cache",
    })
    with urlopen(req, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError("Product page is not HTTP 200: " + model)
        markup = response.read().decode("utf8", "replace")
    parser = ReviewParser()
    parser.feed(markup)
    match = next((review for review in parser.reviews if (
        review["author"] == item["author"]
        and review["content"] == item["content"]
        and review["date"] == DATE
    )), None)
    if match is None:
        raise RuntimeError("Exact selected review not visible on product page " + model)
    return {"model": model, "url": url, "author": match["author"], "date": match["date"]}


def main():
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if not token:
        raise RuntimeError("Read-only D1 verification credential is unavailable")
    manifest = json.loads(MANIFEST.read_text(encoding="utf8"))
    record = json.loads(RECORD.read_text(encoding="utf8"))
    items = manifest.get("items", [])
    if manifest.get("date") != DATE or record.get("date") != DATE or len(items) != 2:
        raise RuntimeError("Invalid same-run additional-review manifest")
    if set(record.get("models", [])) != {item["model"] for item in items}:
        raise RuntimeError("Published model manifest differs from selected Excel rows")

    state = request(token)
    if state.get("today") != DATE:
        raise RuntimeError("D1 Beijing date changed before verification")
    today = [row for row in state.get("recorded", []) if row.get("published_date") == DATE]
    by_model = {row.get("model"): row for row in today}
    for item in items:
        stored = by_model.get(item["model"])
        if not stored or (
            stored.get("source_row") != item["sourceRow"]
            or stored.get("source_model") != item["sourceModel"]
            or stored.get("source_fingerprint") != item["sourceFingerprint"]
        ):
            raise RuntimeError("D1 ledger does not contain the exact selected source row")

    with ThreadPoolExecutor(max_workers=2) as pool:
        live = list(pool.map(verify_live_page, items))
    print("XUYI_20261102_TWO_ADDITIONAL_REVIEWS_D1_AND_LIVE_VERIFIED",
          json.dumps({
              "models": record["models"],
              "excelRows": record["excelRows"],
              "todayCount": len(today),
              "d1Total": len(state.get("recorded", [])),
              "publishRevision": record.get("publishRevision"),
              "livePages": live,
          }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
