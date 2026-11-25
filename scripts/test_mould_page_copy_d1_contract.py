"""Regression gate for structured page copy and shared CTA ownership."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")

snapshot = read("functions/api/build-snapshot.js")
assert "'page_copy'" in snapshot
assert "pageCopy:parseJson(config.page_copy,null)" in snapshot

assert not (ROOT / "functions/api/admin/content-seed.js").exists()
assert not (ROOT / "functions/api/admin/mould-content-seed-20261124.js").exists()

structured_api = read("functions/api/admin/structured-copy.js")
for marker in ("save_page_copy", "quickAnswers", "groups", "bumpPublishRevision"):
    assert marker in structured_api, marker

page_data = read("data/mould-page-structured.json")
assert "quickAnswers" in page_data and "groups" in page_data

renderer = read("mould_build.py")
for marker in ("PAGE_COPY = STATE.get(\"pageCopy\")", "def structured_page_copy", "structured_page_value", "d1_ctas", "structured_eyebrow"):
    assert marker in renderer, marker

sys.path.insert(0, str(ROOT))
import mould_build  # noqa: E402

# Simulate an owner edit from the same public snapshot shape used in CI.
mould_build.PAGE_COPY = {
    "en": {"/about/": {"eyebrow": "OWNER STORY", "title": "Owner About", "subtitle": "Owner subtitle."}},
    "es": {"/about/": {"eyebrow": "HISTORIA EDITADA", "title": "Sobre editado", "subtitle": "Subtítulo editado."}},
}
mould_build.COMMON_COPY = {
    "en": {"shared_cta": {"catalog": {"title": "OWNER CTA", "description": "Owner CTA text.", "note": "Owner note."}}}
}
assert mould_build.structured_page_value("en", "/about/", "title") == "Owner About"
assert mould_build.structured_page_value("es", "/about/", "title") == "Sobre editado"
cta = mould_build.shared_cta("en", "catalog")
assert "OWNER CTA" in cta and "Owner CTA text." in cta and "Owner note." in cta

print("LEYA_MOULD_PAGE_COPY_D1_CONTRACT_PASSED")

