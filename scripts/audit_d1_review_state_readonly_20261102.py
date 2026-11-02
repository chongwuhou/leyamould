#!/usr/bin/env python3
"""Read-only reconciliation of XUYI's private 101-row source and D1 review state."""
from collections import Counter
from pathlib import Path
import json
import os
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from publish_daily_product_reviews import check_source, request


def main():
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if not token:
        raise RuntimeError("Read-only D1 audit requires the configured XUYI CI credential")

    source = check_source()
    state = request(token)  # GET only; this script never calls POST.
    source_by_model = {row["model"]: row for row in source}
    ledger = state.get("recorded", [])
    ledger_models = {row.get("model") for row in ledger}
    existing_models = set(state.get("existingModels", []))

    source_models = set(source_by_model)
    ledger_from_source = [
        row for row in ledger
        if row.get("model") in source_by_model
        and row.get("source_fingerprint") == source_by_model[row["model"]]["sourceFingerprint"]
        and row.get("source_row") == source_by_model[row["model"]]["sourceRow"]
    ]
    ledger_other = [row for row in ledger if row not in ledger_from_source]
    existing_not_ledger = existing_models - ledger_models
    blocked = (source_models & existing_models) - ledger_models
    absent = source_models - existing_models - ledger_models
    date_counts = Counter(row.get("published_date", "") for row in ledger)

    report = {
        "audit": "XUYI_D1_REVIEW_STATE_READ_ONLY",
        "todayBeijing": state.get("today"),
        "sourceWorkbook": "101-zhenshipingjia.xlsx",
        "sourceRows": len(source),
        "sourceUniqueModels": len(source_models),
        "d1LedgerTotal": len(ledger),
        "d1LedgerModels": len(ledger_models),
        "ledgerRowsExactMatchFirstWorkbook": len(ledger_from_source),
        "ledgerRowsNotExactMatchFirstWorkbook": len(ledger_other),
        "d1ReviewTableDistinctModels": len(existing_models),
        "reviewTableModelsWithoutLedger": len(existing_not_ledger),
        "firstWorkbookModelsBlockedByExistingReviewRows": len(blocked),
        "firstWorkbookModelsNotYetInReviewTableOrLedger": len(absent),
        "availableForDailyPublisherUnderCurrentRules": len(absent),
        "publishedByBeijingDate": dict(sorted(date_counts.items())),
        "blockedModels": sorted(blocked),
        "modelsWithoutAnyReviewRow": sorted(absent),
        "reviewTableModelsWithoutLedger": sorted(existing_not_ledger),
        "ledgerModels": sorted(ledger_models),
        "ledgerRecords": [
            {
                "model": row.get("model"),
                "source_row": row.get("source_row"),
                "source_model": row.get("source_model"),
                "published_date": row.get("published_date"),
                "source_fingerprint": row.get("source_fingerprint"),
                "matchesFirstWorkbook": row in ledger_from_source,
            }
            for row in ledger
        ],
        "writePerformed": False,
    }
    print("XUYI_D1_REVIEW_STATE_AUDIT " + json.dumps(report, ensure_ascii=True, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
