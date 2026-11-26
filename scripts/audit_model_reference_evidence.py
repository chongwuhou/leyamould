#!/usr/bin/env python3
"""Read-only evidence grading for the published LEYA model-reference rows.

The script never writes D1/R2 and never invents a missing fact.  It consumes
the authenticated build snapshot produced by ``fetch_build_snapshot.py`` and
prints a stable classification that an editor can use to decide whether a row
stays published or returns to draft.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def clean(value: object) -> str:
    return str(value or "").strip()


def grade(row: dict, locales: list[str]) -> tuple[str, list[str]]:
    issues: list[str] = []
    if not clean(row.get("sourceUrl")).startswith("https://"):
        issues.append("source_url")
    if not clean(row.get("sourceImage")).startswith("https://"):
        issues.append("source_image")
    if not clean(row.get("image")).startswith("/media/"):
        issues.append("r2_image")
    translations = row.get("translations") if isinstance(row.get("translations"), dict) else {}
    for locale in locales:
        if locale == "en":
            continue
        translated = translations.get(locale) if isinstance(translations.get(locale), dict) else {}
        if not clean(translated.get("title")) or not clean(translated.get("alt")):
            issues.append(locale + "_title_alt")
        if clean(row.get("description")) and not clean(translated.get("description")):
            issues.append(locale + "_description")
    if clean(row.get("pdfUrl")) and (len(clean(row.get("pdfSha256"))) != 64 or int(row.get("pdfPages") or 0) < 1):
        issues.append("pdf_metadata")
    # A row with no PDF is not automatically defective: PDFs are optional until
    # an owner-approved document exists.  It is reported separately so it is
    # never mistaken for a complete technical dossier.
    if not clean(row.get("pdfUrl")):
        issues.append("pdf_pending")
    hard_issues = [issue for issue in issues if issue != "pdf_pending"]
    if hard_issues:
        return ("needs-review", issues)
    if "pdf_pending" in issues:
        return ("reference-ready-pdf-pending", issues)
    return ("evidence-ready", issues)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, default=ROOT / "_local_ops" / "build-snapshot.json")
    args = parser.parse_args()
    if not args.snapshot.is_file():
        print("MODEL_REFERENCE_AUDIT_NEEDS_D1_SNAPSHOT", args.snapshot)
        return 2
    state = json.loads(args.snapshot.read_text(encoding="utf-8"))
    languages = state.get("languages") if isinstance(state.get("languages"), dict) else {}
    locales = [
        clean(row.get("code")).lower()
        for row in languages.get("languages", [])
        if isinstance(row, dict) and row.get("enabled") and row.get("publishReady")
    ] or ["en", "es"]
    rows = [row for row in state.get("modelReferences", []) if isinstance(row, dict)]
    counts: dict[str, int] = {}
    issues: list[dict] = []
    for row in rows:
        status, row_issues = grade(row, locales)
        counts[status] = counts.get(status, 0) + 1
        if row_issues:
            issues.append({"slug": clean(row.get("slug")), "status": status, "issues": row_issues})
    report = {
        "site": state.get("site"),
        "rows": len(rows),
        "locales": locales,
        "counts": counts,
        "issues": issues,
        "readOnly": True,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

