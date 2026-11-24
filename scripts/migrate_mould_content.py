#!/usr/bin/env python3
"""Run the fixed LEYA MOULD D1 content seed after the new Pages Function is live."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

ORIGIN = os.environ.get("XUYI_SITE_ORIGIN", "https://leyamould.com").rstrip("/")
PATH = "/api/admin/mould-content-seed-20261124"


def call(token: str) -> dict:
    request = urllib.request.Request(
        ORIGIN + PATH,
        data=b"{}",
        method="POST",
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "LEYA-MOULD-D1-CONTENT-SEED/20261124",
            "x-xuyi-publish-intent": "explicit-owner-approval",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def main() -> None:
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if not token:
        raise SystemExit("CLOUDFLARE_API_TOKEN unavailable")
    last_error = None
    for attempt in range(8):
        try:
            result = call(token)
            if result.get("success") is not True:
                raise SystemExit("LEYA MOULD D1 content seed was not confirmed")
            print("LEYA_MOULD_D1_CONTENT_SEEDED", json.dumps(result, ensure_ascii=False, sort_keys=True))
            return
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code not in (404, 429, 500, 502, 503, 504) or attempt == 7:
                detail = error.read().decode("utf-8", "replace")[:600]
                raise SystemExit(f"D1 content seed HTTP {error.code}: {detail}") from error
            time.sleep(5 + attempt * 5)
        except (TimeoutError, urllib.error.URLError) as error:
            last_error = error
            if attempt == 7:
                raise SystemExit(f"D1 content seed network failure: {error}") from error
            time.sleep(5 + attempt * 5)
    raise SystemExit(f"D1 content seed failed: {last_error}")


if __name__ == "__main__":
    main()


