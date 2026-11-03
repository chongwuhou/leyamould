#!/usr/bin/env python3
"""Read-only D1 schema/JSON audit for the XUYI build snapshot source."""
import json
import os
import urllib.error
import urllib.request

BASE = "https://api.cloudflare.com/client/v4"


def api(method, path, payload=None):
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("CLOUDFLARE_API_TOKEN is unavailable")
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        BASE + path,
        data=data,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/json",
            **({"Content-Type": "application/json"} if data is not None else {}),
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read(1000).decode("utf-8", "replace")
        raise RuntimeError(f"Cloudflare D1 API HTTP {error.code}: {detail}") from error
    if not result.get("success"):
        raise RuntimeError("Cloudflare D1 API returned success=false: " +
                           json.dumps(result.get("errors", [])[:3]))
    return result


def main():
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    if not account:
        raise RuntimeError("CLOUDFLARE_ACCOUNT_ID is unavailable")
    databases = api("GET", f"/accounts/{account}/d1/database?per_page=100").get("result", [])
    matches = [row for row in databases if row.get("name") == "xuyi-drinkware-d1"]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one XUYI D1 database; found {len(matches)}")
    database_id = matches[0]["uuid"]

    def query(sql):
        result = api("POST", f"/accounts/{account}/d1/database/{database_id}/query",
                     {"sql": sql, "params": []}).get("result")
        item = result[0] if isinstance(result, list) and result else result
        if not isinstance(item, dict) or item.get("success") is False:
            raise RuntimeError("D1 SQL query returned an unsuccessful result")
        return item.get("results") or []

    expected = {
        "site_state": {"key", "value", "updated_at"},
        "site_pages": {"route", "label", "seo_title", "meta_description", "robots", "sitemap_enabled"},
        "site_navigation": {"id", "parent_id", "label", "url", "sort_order", "enabled", "new_window"},
        "site_redirects": {"source_path", "target_path", "status_code", "enabled"},
        "xuyi_product_content": {"model", "content_json", "publication_status"},
        "xuyi_translation_overrides": {"resource_id", "locale", "translated_json"},
        "xuyi_page_content": {"route", "main_html", "publication_status"},
        "xuyi_media_alt": {"path", "alt_json"},
        "xuyi_product_reviews": {"id", "model", "rating", "author", "review_date", "content", "status"},
        "xuyi_product_seo": {"slug", "locale", "seo_title", "meta_description"},
    }
    tables = {}
    for table, required in expected.items():
        columns = {row["name"] for row in query(f"PRAGMA table_info('{table}')")}
        tables[table] = {
            "tableMissing": not bool(columns),
            "columns": sorted(columns),
            "missingColumns": sorted(required - columns) if columns else [],
        }
        if columns:
            try:
                count = query(f"SELECT COUNT(*) AS n FROM {table}")
                tables[table]["rows"] = int(count[0]["n"]) if count else 0
            except Exception as error:
                tables[table]["countError"] = str(error)[:180]

    invalid = {}
    checks = {
        "site_state_json": "SELECT key FROM site_state WHERE key IN "
            "('brand_config','contact_config','language_config','admin_security_config','home_banner_config') "
            "AND value<>'' AND json_valid(value)=0 LIMIT 50",
        "product_content_json": "SELECT model FROM xuyi_product_content "
            "WHERE publication_status='published' AND json_valid(content_json)=0 LIMIT 50",
        "translation_json": "SELECT resource_id,locale FROM xuyi_translation_overrides "
            "WHERE json_valid(translated_json)=0 LIMIT 50",
        "media_alt_json": "SELECT path FROM xuyi_media_alt WHERE json_valid(alt_json)=0 LIMIT 50",
    }
    for name, sql in checks.items():
        try:
            invalid[name] = query(sql)
        except Exception as error:
            message = str(error)
            invalid[name] = [] if "no such table" in message.lower() else {"queryError": message[:180]}

    report = {
        "audit": "XUYI_D1_BUILD_SNAPSHOT_READ_ONLY",
        "database": "xuyi-drinkware-d1",
        "tables": tables,
        "invalidJsonSamples": invalid,
        "writePerformed": False,
    }
    print("XUYI_D1_SNAPSHOT_DIAGNOSTIC " +
          json.dumps(report, ensure_ascii=False, sort_keys=True), flush=True)
    has_schema_issue = any(item["missingColumns"] for item in tables.values())
    has_invalid_json = any(isinstance(rows, list) and rows for rows in invalid.values())
    has_query_error = any(isinstance(rows, dict) and rows.get("queryError") for rows in invalid.values())
    if has_schema_issue or has_invalid_json or has_query_error:
        raise SystemExit("XUYI D1 snapshot source requires repair; no writes performed")


if __name__ == "__main__":
    main()
