"""Guard the LEYA media, revision and release-index contract.

These checks are intentionally source-level: they prevent a future cleanup
from making the public media index optional or allowing R2 changes to bypass
the D1 publish revision used by the release pipeline.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def source(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")

usage = source("functions/_shared/r2-usage.js")
assert "d1Revision!==liveRevision" in usage
assert "D1 publish revision does not match the live Pages media index" in usage
assert "publishRevision:d1Revision" in usage

replace = source("functions/api/admin/media-replace.js")
assert "bumpPublishRevision" in replace
assert replace.count("bumpPublishRevision(c.env.LEYA_DB)") >= 2
assert "LEYA_DB missing; media revision cannot be recorded" in replace

snapshot = source("functions/api/build-snapshot.js")
assert "site_state WHERE key IN ('brand_config','contact_config','language_config','admin_security_config','publish_revision','home_banner_config')" in snapshot
assert "FROM submissions" not in snapshot
assert "MOULD_ROUTES.has" in snapshot and "MOULD_MODELS.has" in snapshot

index_script = source("scripts/r2_usage_index.py")
assert '"site":"leyamould"' in index_script
assert '"publishRevision":meta["publishRevision"]' in index_script

build_script = source("scripts/build_release.py")
assert "def source_revision()" in build_script
assert "CF_PAGES_COMMIT_SHA" in build_script
assert "generate_r2_usage_index(DIST" in build_script

workflow = source(".github/workflows/publish-leyamould.yml")
assert "python scripts/r2_usage_index.py" in workflow
assert "python scripts/test_r2_usage_index.py" in workflow
assert "LEYA_RELEASE_SHA: ${{ github.sha }}" in workflow
assert "python scripts/verify_production_release.py" in workflow
assert "configured locales" in workflow

print("LEYA_MOULD_MEDIA_PUBLISH_CONTRACT_PASSED")

