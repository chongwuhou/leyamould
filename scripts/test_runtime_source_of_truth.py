#!/usr/bin/env python3
"""Fail the release when runtime source-of-truth rules regress.

This is intentionally a small source audit, not a blanket ban on constants.
Business labels, security limits and reviewed editorial maps may be constants;
locale registries, site origins, catalog counts and Blog ordering may not be
silently frozen in runtime code.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHECKS = {
    "functions/_shared/publish-scheduler.js": [
        ("const locales=[\"es\",\"pt\",\"ru\",\"tr\"]", "scheduler locale array"),
        ("locale IN ('es','pt','ru','tr')", "scheduler locale CHECK"),
    ],
    "functions/_shared/blog-cms.js": [
        ("(?:en|es|pt|ru|tr)", "Blog card locale regex"),
        ("https://xuyibottles.com", "Blog canonical origin"),
    ],
    "functions/api/admin/page-translations.js": [
        ("[a-z]{2}", "translation route locale regex"),
        ("entry?.newProduct!==true", "legacy new-product-only translation gate"),
    ],
    "scripts/render_locales.py": [
        ("BLOG_DATE_LABELS={", "Blog date labels in code"),
        ("https://xuyibottles.com", "renderer origin"),
        ('{"es":"Botella deportiva"', "gallery locale titles in code"),
    ],
    "site_renderer.py": [
        ("if i<76", "catalog image row cutoff"),
        ("len(SERIES)>=85", "frozen catalog count"),
        ('SITE_ORIGIN="https://xuyibottles.com"', "renderer origin"),
    ],
    "locale_registry.py": [
        ('baseline.get("es"', "fixed locale baseline"),
    ],
}

errors = []
for relative, patterns in CHECKS.items():
    path = ROOT / relative
    if not path.is_file():
        errors.append(f"missing audited source: {relative}")
        continue
    source = path.read_text(encoding="utf-8")
    for needle, label in patterns:
        if needle in source:
            errors.append(f"{relative}: {label} ({needle})")

if errors:
    raise SystemExit("XUYI_RUNTIME_SOURCE_OF_TRUTH_FAILED\n" + "\n".join(errors))

print("XUYI_RUNTIME_SOURCE_OF_TRUTH_PASSED", len(CHECKS), "runtime sources audited")
