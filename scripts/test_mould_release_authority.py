#!/usr/bin/env python3
"""LEYA-specific release authority and owner-edit regression gate."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

workflow = read(".github/workflows/publish-leyamould.yml")
assert "python scripts/fetch_build_snapshot.py" in workflow
assert "python scripts/build_release.py" in workflow
assert "npx --yes wrangler@4.148.0 pages deploy dist --project-name leyamould --branch main" in workflow
assert "scripts/migrate_mould_content.py" not in workflow
assert "Seed reviewed LEYA D1 content and translations" not in workflow
assert "Build bootstrap source release before D1 seed" not in workflow
assert workflow.count("pages deploy dist --project-name leyamould") == 1
assert "scripts/test_mould_release_authority.py" in workflow

renderer = read("mould_build.py")
for marker in ("structured_section(locale, \"/\", \"advantages\"", "structured_section(locale, \"/\", \"products\"", "structured_section(locale, \"/\", \"technology\"", "STATE.get(\"productReviews\", [])"):
    assert marker in renderer, marker
assert "3 million shots with zero defects" not in renderer
assert "FDA validation effortlessly" not in renderer
assert "ISO 9001:2015 Quality System" not in renderer
assert "LEYA MOULD delivered our high-cavity water cap mould ahead of schedule" not in renderer
assert "Technical Manager · Brazil" not in renderer

structured = read("functions/api/admin/structured-copy.js")
assert "loadLanguageConfig" in structured and "publicLanguages" in structured
assert "publicLanguages(languageConfig)" in structured
assert "sections must be an array or keyed object" in structured

product = read("functions/api/admin/product-content.js")
for marker in ('"bodyEs"', '"sectionsEs"', '"faqsEs"'):
    assert marker in product, marker

admin = read("assets/admin-content.js")
assert "state.structuredCopy?.routes" in admin
assert "bodyEs" in admin and "sectionsEs" in admin and "faqsEs" in admin
assert "if(tab===\"structured-copy\")" in admin

print("LEYA_MOULD_RELEASE_AUTHORITY_GATE_PASSED")

