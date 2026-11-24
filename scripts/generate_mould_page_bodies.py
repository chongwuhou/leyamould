#!/usr/bin/env python3
"""Capture the reviewed English static bodies for the first D1 page migration.

The manifest is generated from the checked-in LEYA renderer output, not from a
remote website. It is imported only by the owner-approved content seed; later
edits in D1 remain authoritative and are never overwritten.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUTPUT = ROOT / "data/mould-page-bodies.json"

ROUTES = {
    "/": "index.html",
    "/about/": "about/index.html",
    "/capabilities/": "capabilities/index.html",
    "/capabilities/mould-design/": "capabilities/mould-design/index.html",
    "/capabilities/precision-manufacturing/": "capabilities/precision-manufacturing/index.html",
    "/capabilities/trial-sampling/": "capabilities/trial-sampling/index.html",
    "/manufacturing/": "manufacturing/index.html",
    "/quality-control/": "quality-control/index.html",
    "/request-sample/": "request-sample/index.html",
    "/contact/": "contact/index.html",
    "/samples/": "samples/index.html",
    "/news/": "news/index.html",
    "/news/Bottle-cap-molds.html": "news/Bottle-cap-molds.html",
    "/Bottle-Cap-Machine/Bottle-Cap-Machine.html": "Bottle-Cap-Machine/Bottle-Cap-Machine.html",
    "/video/": "video/index.html",
    "/faq/": "faq/index.html",
    "/privacy-policy/": "privacy-policy/index.html",
}


def main() -> None:
    rows = []
    for route, relative in ROUTES.items():
        source = DIST / relative
        if not source.is_file():
            raise SystemExit(f"missing rendered page: {source}")
        html = source.read_text(encoding="utf-8")
        match = re.search(r"<main\b[^>]*>([\s\S]*?)</main>", html, re.I)
        if not match:
            raise SystemExit(f"missing main element: {source}")
        body = match.group(1).strip()
        if len(body) < 100 or not re.search(r"<(?:section|article|div|h1)\b", body, re.I):
            raise SystemExit(f"page body is unexpectedly short: {route}")
        rows.append({"route": route, "mainHtml": body, "source": f"dist/{relative}"})
    OUTPUT.write_text(json.dumps({"schemaVersion": 1, "sourceLocale": "en", "items": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("LEYA_PAGE_BODY_MANIFEST_CREATED", len(rows), OUTPUT)


if __name__ == "__main__":
    main()

