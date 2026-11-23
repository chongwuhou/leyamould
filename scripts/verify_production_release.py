#!/usr/bin/env python3
"""Read-only production release verification for LEYA MOULD.

The deployment is not considered complete until the public build metadata and
the R2 reference index are both reachable and describe the same revision.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

ORIGIN = os.environ.get("LEYA_SITE_ORIGIN", "https://leyamould.com").rstrip("/")
EXPECTED_SHA = os.environ.get("LEYA_RELEASE_SHA") or os.environ.get("GITHUB_SHA", "")
RETRY_DELAYS = (0, 2, 4, 8, 12)


def read_json(path: str) -> dict:
    last_error: Exception | None = None
    for attempt, delay in enumerate(RETRY_DELAYS, start=1):
        if delay:
            time.sleep(delay)
        request = urllib.request.Request(
            ORIGIN + path + ("&" if "?" in path else "?") + "release_audit=" + str(time.time_ns()),
            headers={"Cache-Control": "no-store", "User-Agent": "LEYA-Release-Audit/1.0"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status != 200:
                    raise RuntimeError(f"{path} returned HTTP {response.status}")
                value = json.load(response)
            if not isinstance(value, dict):
                raise RuntimeError(f"{path} did not return a JSON object")
            return value
        except urllib.error.HTTPError as error:
            last_error = error
            # Pages custom domains can briefly serve the previous deployment (or
            # a 404) while the new deployment propagates. Retry only transient
            # responses; a 4xx/5xx that persists will still fail the job.
            if error.code not in {404, 408, 429} and not 500 <= error.code < 600:
                break
        except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError) as error:
            last_error = error
    raise RuntimeError(f"{path} is not readable after {len(RETRY_DELAYS)} attempts: {last_error}") from last_error


meta = read_json("/build-meta.json")
index = read_json("/r2-usage-index.json")
if meta.get("siteOrigin") != ORIGIN:
    raise RuntimeError("build-meta site origin mismatch")
if meta.get("pagesProject") != "leyamould":
    raise RuntimeError("build-meta Pages project mismatch")
if meta.get("noindex") is not True:
    raise RuntimeError("production build must remain noindex until indexing is approved")
if index.get("site") != "leyamould" or index.get("schemaVersion") != 1:
    raise RuntimeError("R2 reference index identity/schema mismatch")
if index.get("publishRevision") != meta.get("publishRevision"):
    raise RuntimeError("R2 reference index and build-meta revisions differ")
if EXPECTED_SHA and meta.get("sourceRevision") != EXPECTED_SHA:
    raise RuntimeError(
        "production source revision mismatch: expected " + EXPECTED_SHA +
        ", got " + str(meta.get("sourceRevision"))
    )
references = index.get("references")
if not isinstance(references, dict):
    raise RuntimeError("R2 reference index is missing references")
print(
    "LEYA_PRODUCTION_RELEASE_VERIFIED",
    "sourceRevision=" + str(meta.get("sourceRevision")),
    "publishRevision=" + str(meta.get("publishRevision")),
    "mediaReferences=" + str(len(references)),
)

