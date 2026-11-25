"""Contract checks for the reviewed model-reference catalogue boundary."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


data = json.loads(source("data/mould-models.json"))
rows = data.get("models", [])
assert isinstance(rows, list) and rows, "reference catalogue must not be empty"
slugs = [str(row.get("slug") or "").strip().lower() for row in rows]
assert all(slugs), "every reference model requires a slug"
assert len(set(slugs)) == len(slugs), "reference model slugs must be unique"
assert all(row.get("family") and row.get("title") and row.get("image") for row in rows)
assert all("glass cement" not in " ".join(str(row.get(key) or "") for key in ("family", "title", "sourceUrl", "description")).lower() for row in rows)

api = source("functions/api/admin/model-references.js")
for required in (
    "leya_model_references", "publication_status", "translations_json", "image_path",
    "authorizeAdminRequest", "bumpPublishRevision", "verifyPublishedImage", "bulk_import",
):
    assert required in api, required
assert "LEYA_ASSETS.head" in api
assert "Bulk import aborted; no rows were written" in api
assert 'action==="regrade"' in api
assert "publication_status='draft'" in api

snapshot = source("functions/api/build-snapshot.js")
assert "leya_model_references" in snapshot
assert "modelReferences" in snapshot
assert "publication_status='published'" in snapshot
assert "reviewed_at" in snapshot
assert "modelReferenceAudit" in snapshot
assert "publishedIssues" in snapshot

renderer = source("mould_build.py")
assert "STATE.get(\"modelReferences\"" in renderer
assert "STATIC_HMOULD_MODELS" in renderer
assert "MODEL_REFERENCE_SOURCE" in renderer
renderer_section = source("mould_category_pages.py")
assert "_model_text" in renderer_section and "translations" in renderer_section

admin = source("admin/index.html")
assert "modelreferences" in admin
assert "/assets/admin-model-references.js" in admin
assert "model-reference-editor" in admin and "model-reference-import" in admin
assert "model-reference-reviewed-at" in admin

release = source("scripts/build_release.py")
assert '"modelReferences"' in release and "modelReferenceCount" in release

regrade = source("scripts/regrade_mould_references.py")
assert "never calls a remote API" in regrade
assert "ownerReviewed" in regrade

print("LEYA_MOULD_MODEL_REFERENCE_CONTRACT_PASSED", f"rows={len(rows)}")

