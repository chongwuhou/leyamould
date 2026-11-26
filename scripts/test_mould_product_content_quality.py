"""Quality gate for the bilingual 13-family content draft.

This is a source/draft gate, not a D1 writer.  It catches missing locales,
thin project briefs, incomplete FAQ sets and obvious unsupported marketing
claims before an authenticated administrator publishes the rows.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "data" / "mould-product-content-draft.json"
EXPECTED = {
    "mineral-water-closure-cap-molds", "oil-bottle-cap-mould", "flip-top-caps-mould",
    "engine-oil-cap-mould", "food-packaging-cap-mould", "medical-cap-mould",
    "personal-care-cap-mould", "functional-cap-mould", "plastic-handle-cap-mould",
    "five-gallon-water-cap-mould", "wine-cap-mould", "pet-preform-mould", "blow-bottle-mould",
}
FORBIDDEN = re.compile(r"(?:5\s*m\+?|50,?000|72\s+cavities?|FDA|ISO\s*13485|guarantee(?:d|s)?|certified|leak[- ]proof)", re.I)
EN_MARKERS = re.compile(r"\b(?:the|and|our|with|from|before|send|provide|can|what|how)\b", re.I)


def fail(message: str) -> None:
    raise SystemExit("FAIL: " + message)


def main() -> None:
    try:
        data = json.loads(PACK.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        fail(f"cannot read draft: {exc}")
    if set(data) != EXPECTED:
        fail(f"expected exactly 13 family slugs, got {len(data)}")
    for slug, row in data.items():
        for locale, suffix in (("en", ""), ("es", "Es")):
            for key in ("title", "description", "body"):
                if not str(row.get(key + suffix) or "").strip():
                    fail(f"{slug} missing {locale} {key}")
            sections = row.get("sections" + suffix)
            faqs = row.get("faqs" + suffix)
            brief = row.get("projectBrief" + suffix)
            if not isinstance(sections, list) or len(sections) < 2:
                fail(f"{slug} {locale} needs at least two engineering sections")
            if not isinstance(faqs, list) or len(faqs) != 4:
                fail(f"{slug} {locale} needs exactly four FAQs")
            if not isinstance(brief, dict):
                fail(f"{slug} missing {locale} project brief")
            for key, minimum in (("scenarios", 2), ("parameters", 3), ("quoteChecklist", 4), ("sources", 1)):
                values = brief.get(key)
                if not isinstance(values, list) or len(values) < minimum:
                    fail(f"{slug} {locale} brief {key} is incomplete")
            if not str(brief.get("evidenceNote") or "").strip():
                fail(f"{slug} {locale} missing evidence note")
            all_text = json.dumps(row, ensure_ascii=False)
            if FORBIDDEN.search(all_text):
                fail(f"{slug} contains an unsupported fixed claim")
            if locale == "es" and EN_MARKERS.search(" ".join([
                str(row.get("titleEs") or ""), str(row.get("descriptionEs") or ""),
                *[str(x.get("question") or "") for x in faqs],
                *[str(x.get("answer") or "") for x in faqs],
            ])):
                fail(f"{slug} Spanish copy contains an obvious English fragment")
    print(f"PASS: {len(data)} families × 2 locales; sections, 4 FAQs, brief and source checks complete")


if __name__ == "__main__":
    main()

