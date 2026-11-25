"""Static contract checks for the lightweight LEYA D1 state layer."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

system = read("functions/_shared/leya-system.js")
assert "site_state" in system
assert "leya_schema_migrations" in system
assert "leya_content_audit" not in system

settings = read("functions/_shared/site-settings.js")
assert "ensureLeyaSystemSchema" in settings
assert "bumpPublishRevision" in settings
assert "recordContentAudit" not in settings

media = read("assets/admin-media.js")
blog = read("assets/admin-blog.js")
assert "compressForUpload" in media
assert "image/webp" in media
assert "toBlob(resolve,'image/webp',0.88)" in blog

assert not (ROOT / "functions/api/admin/content-seed.js").exists()
assert not (ROOT / "functions/api/admin/mould-content-seed-20261124.js").exists()

admin = read("admin/index.html")
assert "data-admin-target=\"audit\"" not in admin
assert "admin-audit.js" not in admin

print("LEYA_LIGHTWEIGHT_STATE_CONTRACT_PASSED")

