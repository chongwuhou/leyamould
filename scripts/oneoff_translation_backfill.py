#!/usr/bin/env python3
"""Generate the one-time LEYA D1 Spanish translation backfill SQL.

This file is intentionally temporary: it is used by the guarded migration
workflow, then removed before the normal production chain is restored.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mould_localization import spanish_model_description, spanish_model_text

ES_ROOT = ROOT / "es"
MODEL_SOURCE = ROOT / "data" / "mould-models.json"
OUTPUT = ROOT / "_local_ops" / "translation-backfill.sql"


def sql(value: object) -> str:
    return "'" + str(value).replace("\x00", "").replace("'", "''") + "'"


def route_for(path: Path) -> str:
    relative = path.relative_to(ES_ROOT).as_posix()
    if relative == "index.html":
        return "/"
    if relative.endswith("/index.html"):
        return "/" + relative[:-len("index.html")]
    return "/" + relative


def extract_page(path: Path) -> tuple[str, str, str]:
    source = path.read_text(encoding="utf-8")
    title_match = re.search(r"<title[^>]*>(.*?)</title>", source, re.I | re.S)
    description_match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        source,
        re.I | re.S,
    )
    main_match = re.search(r'<main\b[^>]*id=["\']main-content["\'][^>]*>(.*?)</main>', source, re.I | re.S)
    if not main_match:
        main_match = re.search(r"<main\b[^>]*>(.*?)</main>", source, re.I | re.S)
    title = html.unescape(re.sub(r"\s+", " ", title_match.group(1)).strip()) if title_match else ""
    description = html.unescape(re.sub(r"\s+", " ", description_match.group(1)).strip()) if description_match else ""
    main_html = main_match.group(1).strip() if main_match else ""
    if not title or not description or len(main_html) < 120:
        raise RuntimeError(f"Spanish page is incomplete: {path}")
    return route_for(path), title, description, main_html


def main() -> None:
    pages = []
    for path in sorted(ES_ROOT.rglob("*.html")):
        pages.append(extract_page(path))
    models = json.loads(MODEL_SOURCE.read_text(encoding="utf-8")).get("models") or []
    if len(pages) != 57:
        raise RuntimeError(f"Expected 57 Spanish pages, got {len(pages)}")
    if len(models) != 112:
        raise RuntimeError(f"Expected 112 model rows, got {len(models)}")

    statements = [
        "BEGIN;",
        "CREATE TABLE IF NOT EXISTS xuyi_translation_overrides (resource_id TEXT NOT NULL, locale TEXT NOT NULL, translated_json TEXT NOT NULL DEFAULT '{}', reviewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(resource_id, locale));",
    ]
    for route, title, description, main_html in pages:
        payload = json.dumps(
            {"title": title, "description": description, "mainHtml": main_html},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        statements.append(
            "INSERT INTO xuyi_translation_overrides(resource_id,locale,translated_json,reviewed_at) "
            f"VALUES ({sql('page:' + route)},{sql('es')},{sql(payload)},CURRENT_TIMESTAMP) "
            "ON CONFLICT(resource_id,locale) DO UPDATE SET translated_json=excluded.translated_json, reviewed_at=CURRENT_TIMESTAMP;"
        )
    for row in models:
        payload = json.dumps(
            {
                "es": {
                    "title": spanish_model_text(row.get("title", "")),
                    "alt": spanish_model_text(row.get("alt") or row.get("title", "")),
                    "description": spanish_model_description(row.get("description", "")),
                }
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        statements.append(
            "UPDATE leya_model_references SET translations_json="
            f"{sql(payload)}, updated_at=CURRENT_TIMESTAMP WHERE slug={sql(row.get('slug', ''))};"
        )
    statements.append("COMMIT;")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(statements) + "\n", encoding="utf-8")
    print("LEYA_TRANSLATION_BACKFILL_SQL_READY", f"pages={len(pages)}", f"models={len(models)}", f"bytes={OUTPUT.stat().st_size}")


if __name__ == "__main__":
    main()

