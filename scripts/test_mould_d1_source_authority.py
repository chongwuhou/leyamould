"""Source-level guard for the LEYA MOULD D1 content migration boundary."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


snapshot = read("functions/api/build-snapshot.js")
assert "'common_copy'" in snapshot
assert "commonCopy:parseJson(config.common_copy,null)" in snapshot
assert "'page_copy'" in snapshot
assert "pageCopy:parseJson(config.page_copy,null)" in snapshot
assert "xuyi_blog_posts WHERE status='published'" in snapshot

renderer = read("mould_build.py")
assert "COMMON_COPY = STATE.get(\"commonCopy\")" in renderer
assert "PAGE_COPY = STATE.get(\"pageCopy\")" in renderer
assert "COMMON_COPY.get(locale)" in renderer
assert "d1_editorial = row.get(\"editorial\")" in renderer
assert 'value["editorial"] = overrides[base["slug"]].get("editorial") or base.get("editorial")' in renderer
assert "FOOTER_LOGO" in renderer and "FOOTER_COPYRIGHT" in renderer

footer = read("templates/site/footer.html")
for marker in ("{{FOOTER_LOGO}}", "{{FOOTER_EMAIL}}", "{{FOOTER_WA_URL}}", "{{FOOTER_COPYRIGHT}}", "{{FOOTER_QUICK_LINKS}}"):
    assert marker in footer, marker

seed = read("functions/api/admin/mould-content-seed-20261124.js")
for marker in ("mould-news-editorial.json", "xuyi_blog_posts", "site_pages", "site_navigation", "common_copy", "ownerEditsPreserved"):
    assert marker in seed, marker

editorial = json.loads((ROOT / "data/mould-news-editorial.json").read_text(encoding="utf-8"))
items = editorial.get("items") or []
assert len(items) == 24
assert len({item["slug"] for item in items}) == 24
assert {item["category"] for item in items} == {"news", "machine"}
assert all(len(item.get("sections", {}).get("en", [])) == 7 for item in items)

workflow = read(".github/workflows/publish-leyamould.yml")
assert "scripts/migrate_mould_content.py" in workflow
assert "scripts/test_mould_release_authority.py" in workflow

print("LEYA_MOULD_D1_SOURCE_AUTHORITY_PASSED")

