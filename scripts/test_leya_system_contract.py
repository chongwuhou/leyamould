"""Static contract checks for the LEYA operational layer."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

system = read("functions/_shared/leya-system.js")
assert "leya_schema_migrations" in system
assert "leya_content_audit" in system
assert "recordContentAudit" in system

settings = read("functions/_shared/site-settings.js")
assert "ensureLeyaSystemSchema" in settings
assert "recordContentAudit" in settings
assert "hashValue" in settings

audit = read("functions/api/admin/audit.js")
assert "authorizedBuildRequest" in audit
assert "leya_content_audit" in audit
assert "DELETE" not in audit

media = read("assets/admin-media.js")
blog = read("assets/admin-blog.js")
assert "compressForUpload" in media
assert "image/webp" in media
assert "toBlob(resolve,'image/webp',0.88)" in blog

seed = read("functions/api/admin/mould-content-seed-20261124.js")
assert "mould-page-bodies.json" in seed
assert "pageBodies" in seed

auth = read("functions/_shared/build-auth.js")
assert "/api/admin/content-seed" in auth
assert "LEYA_ALLOW_LEGACY_MIGRATIONS" in auth

renderer = read("mould_build.py")
assert 'source_body = BODY_OVERRIDES.get(route) if locale == "en" else ""' in renderer
assert "LEYA MOULD delivered our high-cavity water cap mould ahead of schedule" not in renderer

print("LEYA_SYSTEM_CONTRACT_PASSED")

