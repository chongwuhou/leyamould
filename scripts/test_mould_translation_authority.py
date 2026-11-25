#!/usr/bin/env python3
"""Prevent production builds from silently using renderer translation fallback."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

renderer = (ROOT / "mould_build.py").read_text(encoding="utf-8")
gate = (ROOT / "scripts/test_mould_d1_completeness.py").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/publish-leyamould.yml").read_text(encoding="utf-8")

assert "STRICT_D1" in renderer
assert "Strict D1 translation missing" in renderer
assert 'required = ("title", "description", "mainHtml")' in renderer
assert "has_reviewed_source_fallback" not in gate
assert "source_model = next" not in gate
assert "mainHtml" in gate and "title-description" in gate
assert "python scripts/test_mould_translation_authority.py" in workflow

print("LEYA_MOULD_TRANSLATION_AUTHORITY_GATE_PASSED")

