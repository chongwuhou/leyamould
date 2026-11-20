#!/usr/bin/env python3
"""Perform and verify the D1 v2 review-ledger migration without publishing reviews.

This is intentionally GET-only. The endpoint's first authorized GET performs
an additive/idempotent legacy-ledger copy and returns the migrated ledger.
No review POST, D1 content edit, or publish-revision bump is performed here.
"""
from datetime import datetime
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import json
import os
import sys

ORIGIN = "https://leyamould.com"
REVIEW_API = ORIGIN + "/api/admin/daily-product-reviews"
PUBLISH_STATE_API = ORIGIN + "/api/publish-state"
EXPECTED_MINIMUM_LEGACY_ROWS = 42


def get_json(url, token):
    req = Request(url, method="GET", headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/json",
        "User-Agent": "XUYI-ReadOnly-Review-Ledger-Migration/1.0",
    })
    try:
        with urlopen(req, timeout=60) as response:
            return json.load(response)
    except HTTPError as error:
        detail = error.read(400).decode("utf8", "replace")
        raise RuntimeError("Read-only migration GET failed: HTTP " +
                           str(error.code) + " " + detail) from None


def main():
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if not token:
        raise RuntimeError("Cloudflare credential missing")
    if os.environ.get("GITHUB_ACTIONS") != "true" or \
       os.environ.get("GITHUB_REPOSITORY") != "chongwuhou/leyamould" or \
       os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise RuntimeError("Migration is allowed only from the canonical XUYI GitHub main")

    today = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    revision_before = get_json(PUBLISH_STATE_API, token)
    state = get_json(REVIEW_API, token)
    revision_after = get_json(PUBLISH_STATE_API, token)

    if state.get("today") != today:
        raise RuntimeError("GitHub Actions and D1 Beijing dates disagree")
    if state.get("publicationSchema") != 2:
        raise RuntimeError("Production daily-review API did not report schema v2")

    records = state.get("recorded")
    published = set(state.get("publishedFingerprints", []))
    if not isinstance(records, list):
        raise RuntimeError("D1 v2 ledger response is not a list")

    legacy = [row for row in records if row.get("source_file") == "legacy-unmapped"]
    if len(legacy) < EXPECTED_MINIMUM_LEGACY_ROWS:
        raise RuntimeError("Fewer than 42 legacy records were migrated; stop and inspect D1")

    ids = [row.get("review_id") for row in records]
    fingerprints = [row.get("source_fingerprint") for row in records]
    source_rows = [(row.get("source_file"), row.get("source_row")) for row in records]
    if None in ids or len(ids) != len(set(ids)):
        raise RuntimeError("Review IDs are missing or duplicated in migrated ledger")
    if None in fingerprints or len(fingerprints) != len(set(fingerprints)):
        raise RuntimeError("Review fingerprints are missing or duplicated in migrated ledger")
    if None in [row for row in source_rows] or len(source_rows) != len(set(source_rows)):
        raise RuntimeError("Source-file/row identities are missing or duplicated")
    if any(row["source_fingerprint"] not in published for row in legacy):
        raise RuntimeError("A migrated legacy ledger fingerprint has no published review")
    if len(published) < len(legacy):
        raise RuntimeError("Published-review count is smaller than the migrated legacy ledger")

    before = revision_before.get("publishRevision")
    after = revision_after.get("publishRevision")
    if before != after:
        raise RuntimeError("Read-only ledger migration unexpectedly changed publishRevision")

    print("XUYI_D1_V2_READ_ONLY_MIGRATION_VERIFIED")
    print("BEIJING_DATE", today)
    print("LEGACY_ROWS_PRESERVED", len(legacy))
    print("TOTAL_LEDGER_ROWS", len(records))
    print("PUBLISHED_REVIEW_FINGERPRINTS", len(published))
    print("PUBLISH_REVISION_UNCHANGED", after)
    print("NO_REVIEW_WAS_PUBLISHED_BY_MIGRATION")


if __name__ == "__main__":
    main()

