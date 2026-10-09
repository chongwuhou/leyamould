#!/usr/bin/env python3
"""XUYI adapter for Demalong's D1 translation queue; output SQL, never touch a live DB.

Usage: python scripts/seed-xuyi-translation-sources.py
Then, after reviewing the generated SQL, import into the isolated XUYI D1 database.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "_local_ops" / "sql" / "xuyi-translation-sources.sql"

def quote(value):
    return "'" + str(value).replace("'", "''") + "'"

def main():
    products = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
    sql = [
        "-- Import only into XUYI_DB / xuyi-drinkware-d1, NEVER into Demalong D1.",
        "CREATE TABLE IF NOT EXISTS xuyi_translation_sources ("
        "resource_id TEXT PRIMARY KEY,resource_type TEXT NOT NULL DEFAULT 'product',"
        "source_locale TEXT NOT NULL DEFAULT 'en',source_json TEXT NOT NULL DEFAULT '{}',"
        "updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);",
        "BEGIN TRANSACTION;"
    ]
    count = 0
    seen = set()
    for item in products:
        model = str(item.get("model") or "").strip()
        slug = str(item.get("slug") or model).strip()
        if model in seen or not model or not (ROOT / "products" / slug / "index.html").exists():
            continue
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        seen.add(model)
        payload = {
            "localization": {
                "name": name,
                "category": str(item.get("category") or ""),
                "description": "Plastic water bottle model " + model + ". "
                    "Confirm capacity, material, components, BPA-free option and branding for the order."
            },
            "contentMeta": {
                "seoTitle": name + " | XUYI Bottles",
                "metaDescription": "Wholesale " + name + ". "
                    "Material options and customization subject to model confirmation."
            },
            "articleSections": []
        }
        value = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        sql.append("INSERT INTO xuyi_translation_sources"
                   "(resource_id,resource_type,source_locale,source_json,updated_at)"
                   " VALUES(" + ",".join(map(quote,[model,"product","en",value]))
                   + ",CURRENT_TIMESTAMP)"
                   " ON CONFLICT(resource_id) DO UPDATE SET"
                   " source_json=excluded.source_json,updated_at=CURRENT_TIMESTAMP;")
        count += 1
    sql.append("COMMIT;")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(sql) + "\n", encoding="utf-8")
    print(f"XUYI_TRANSLATION_SEED_OK products={count} sql={OUTPUT}")
    if count < 70:
        raise SystemExit("Too few published product pages; check product catalogue and output.")

if __name__ == "__main__":
    main()