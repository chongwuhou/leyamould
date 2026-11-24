#!/usr/bin/env python3
"""Prepare a reviewed D1 import payload for the HMould reference catalogue.

This is deliberately an offline preparation step.  It never calls Cloudflare,
HMould or a translation API.  The resulting JSON can be reviewed, uploaded to
the authenticated admin endpoint as ``action=bulk_import``, and kept as draft
records until each compressed image has been moved into LEYA R2.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/mould-models.json"
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,139}$")


def load_rows() -> list[dict]:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = data.get("models") if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows:
        raise SystemExit("mould-models.json has no model rows")
    seen: set[str] = set()
    result: list[dict] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise SystemExit("model row is not an object")
        slug = str(row.get("slug") or "").strip().lower()
        family = str(row.get("family") or "").strip().lower()
        title = str(row.get("title") or "").strip()
        if not SLUG.fullmatch(slug) or slug in seen:
            raise SystemExit(f"invalid or duplicate model slug: {slug}")
        if not family or len(title) < 2:
            raise SystemExit(f"missing family/title: {slug}")
        if "glass cement" in " ".join(str(row.get(key) or "") for key in ("family", "title", "sourceUrl", "description")).lower():
            raise SystemExit(f"glass cement reference must remain excluded: {slug}")
        seen.add(slug)
        result.append({
            "slug": slug,
            "family": family,
            "title": title,
            "alt": str(row.get("alt") or title).strip(),
            "sourceUrl": str(row.get("sourceUrl") or "").strip(),
            "sourceImage": str(row.get("sourceImage") or "").strip(),
            "imagePath": str(row.get("image") or "").strip(),
            "description": str(row.get("description") or "").strip(),
            "publicationStatus": "draft",
            "sortOrder": index,
            "translations": {},
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="write the reviewed JSON payload to a local file")
    args = parser.parse_args()
    rows = load_rows()
    payload = {"action": "bulk_import", "createOnly": True, "items": rows}
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"MODEL_REFERENCE_IMPORT_READY rows={len(rows)} output={args.output}")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
