#!/usr/bin/env python3
"""Static guard for the fixed, narrow multilingual Blog D1 repair plan."""
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
source=(ROOT/"functions/api/admin/blog-translation-repair-20261105.js").read_text(encoding="utf-8")
assert source.count("route:") == 9
assert "const BATCH_ID = \"2026-11-05-blog-translation-repair\";" in source
assert "json_set(translated_json,'$.mainHtml'" in source
assert "instr(json_extract(translated_json,'$.mainHtml')" in source
assert "bumpPublishRevision(db)" in source
assert "dist" not in source.lower()
assert "INSERT OR IGNORE INTO xuyi_translation_repair_audit" in source
print("XUYI_BLOG_TRANSLATION_REPAIR_SOURCE_GUARD_PASSED 9 D1 records, conditional replacements, audit ledger, publish revision")
