#!/usr/bin/env python3
"""Read-only reconciliation of the D1 route registry in a build snapshot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def route_set(rows: object) -> set[str]:
    if not isinstance(rows, list):
        return set()
    return {str(row.get("route") or "").strip() for row in rows if isinstance(row, dict) and str(row.get("route") or "").strip()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, default=ROOT / "_local_ops" / "build-snapshot.json")
    args = parser.parse_args()
    if not args.snapshot.is_file():
        print("SITE_PAGES_AUDIT_NEEDS_D1_SNAPSHOT", args.snapshot)
        return 2
    state = json.loads(args.snapshot.read_text(encoding="utf-8"))
    pages = route_set(state.get("pages"))
    registry_rows = [row for row in state.get("pageRegistry", []) if isinstance(row, dict)]
    registry = route_set(registry_rows)
    fields = route_set(state.get("pageFields"))
    promoted = sorted({str(row.get("route") or "") for row in registry_rows if row.get("source") not in ("site_pages", "")})
    report = {
        "site": state.get("site"),
        "readOnly": True,
        "persistentSitePages": len(pages),
        "effectiveRegistry": len(registry),
        "pageFields": len(fields),
        "registryMissingFromFields": sorted(registry - fields),
        "fieldsMissingFromRegistry": sorted(fields - registry),
        "effectiveRoutesNotPersistedInSitePages": promoted,
        "status": "complete" if not (registry - fields or fields - registry or promoted) else "needs-site-pages-readback",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())

