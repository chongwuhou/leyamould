#!/usr/bin/env python3
"""Run the fixed, owner-safe 2026-11-04 XUYI D1 product SEO refresh in CI."""
from __future__ import annotations
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import json
import os

SITE = "https://xuyibottles.com/api/admin/product-seo-refresh-20261104"

def call(token, body=None):
    request = Request(
        SITE,
        data=json.dumps(body, separators=(",", ":")).encode("utf-8") if body else None,
        method="POST" if body else "GET",
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "XUYI-Reviewed-Product-SEO-Refresh/1.0",
        },
    )
    try:
        with urlopen(request, timeout=65) as response:
            return json.load(response)
    except HTTPError as error:
        raise RuntimeError(
            "D1 SEO refresh failed with HTTP " + str(error.code) + " " +
            error.read(500).decode("utf-8", "replace")
        ) from None

def main():
    if (os.environ.get("GITHUB_ACTIONS") != "true" or
            os.environ.get("GITHUB_REPOSITORY") != "chongwuhou/xuyi-drinkware-site" or
            os.environ.get("GITHUB_REF") != "refs/heads/main"):
        raise RuntimeError("Only the approved XUYI GitHub main workflow may run this D1 refresh")
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        raise RuntimeError("Missing XUYI deployment credential")

    initial = call(token)
    if initial.get("reviewed") != 505:
        raise RuntimeError("Unexpected reviewed SEO source count")
    if initial.get("missingRows"):
        raise RuntimeError("Missing D1 product SEO rows; no batch was changed")
    print(
        "SEO_REFRESH_PREFLIGHT",
        "TITLE_ELIGIBLE", initial.get("titleEligible"),
        "TITLE_ALREADY_UPDATED", initial.get("titleUpdated"),
        "TITLE_OWNER_PRESERVED", initial.get("titlePreserved"),
        "DESCRIPTION_ELIGIBLE", initial.get("descriptionEligible"),
        "DESCRIPTION_ALREADY_UPDATED", initial.get("descriptionUpdated"),
        "DESCRIPTION_OWNER_PRESERVED", initial.get("descriptionPreserved"),
    )

    if initial.get("titleEligible") or initial.get("descriptionEligible"):
        for index in range(initial["batchCount"]):
            result = call(token, {"action": "batch", "batchIndex": index})
            if result.get("missingRows"):
                raise RuntimeError("A reviewed D1 SEO row disappeared during refresh")
            if index % 8 == 0 or index + 1 == initial["batchCount"]:
                print(
                    "REFRESHED_REVIEWED_BATCH", index + 1, "OF", initial["batchCount"],
                    "TITLE_UPDATED", result.get("titleUpdated"),
                    "DESCRIPTION_UPDATED", result.get("descriptionUpdated"),
                    "OWNER_FIELDS_PRESERVED",
                    result.get("titlePreserved", 0) + result.get("descriptionPreserved", 0),
                )

    final_state = call(token)
    if (final_state.get("reviewed") != 505 or final_state.get("missingRows") or
            final_state.get("titleEligible") or final_state.get("descriptionEligible")):
        raise RuntimeError("D1 SEO refresh did not account for every reviewed field")

    final = call(token, {"action": "finalize"})
    if not final.get("complete"):
        raise RuntimeError("D1 SEO refresh could not queue the publish revision")
    revision = int(final["revision"])
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write("revision=" + str(revision) + "\n")
    print(
        "XUYI_PRODUCT_SEO_REFRESH_20261104_COMPLETE",
        "ROWS", final["reviewed"],
        "TITLE_UPDATED", final.get("titleUpdated"),
        "TITLE_OWNER_PRESERVED", final.get("titlePreserved"),
        "DESCRIPTION_UPDATED", final.get("descriptionUpdated"),
        "DESCRIPTION_OWNER_PRESERVED", final.get("descriptionPreserved"),
        "PUBLISH_REVISION", revision,
    )

if __name__ == "__main__":
    main()
