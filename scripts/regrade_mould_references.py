#!/usr/bin/env python3
"""Report the 112 reference models' publication readiness without writing D1.

The report is deliberately source-only: it never calls a remote API and never
invents translations, PDFs, customer claims or production parameters.  The
admin model-reference endpoint has the matching ``regrade`` action for an
authenticated owner session; it demotes only rows that fail these same checks.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", dest="json_path", help="write the read-only report to a local JSON file")
    args = parser.parse_args()
    payload = json.loads((ROOT / "data" / "mould-models.json").read_text(encoding="utf-8"))
    rows = payload.get("models") or []
    report_rows = []
    for row in rows:
        source_ready = str(row.get("sourceUrl") or "").startswith("https://") and str(row.get("sourceImage") or "").startswith("https://")
        image_ready = str(row.get("image") or "").startswith("/assets/") or str(row.get("image") or "").startswith("/media/")
        report_rows.append({
            "slug": row.get("slug", ""),
            "family": row.get("family", ""),
            "sourceReady": source_ready,
            "imageReferenceReady": image_ready,
            "publicationState": "needs_review" if not (source_ready and image_ready) else "draft_until_d1_review",
            "reason": "D1 Spanish title/ALT/description, R2 image and owner review are still required before publication",
        })
    report = {
        "source": payload.get("source"),
        "total": len(report_rows),
        "publicationReady": sum(item["publicationState"] == "ready" for item in report_rows),
        "needsReview": sum(item["publicationState"] != "ready" for item in report_rows),
        "families": dict(Counter(item["family"] for item in report_rows)),
        "models": report_rows,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_path:
        output = Path(args.json_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print("LEYA_MOULD_REFERENCE_REGRADE", json.dumps({k: report[k] for k in ("total", "publicationReady", "needsReview", "families")}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
