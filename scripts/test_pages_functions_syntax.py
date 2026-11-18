#!/usr/bin/env python3
"""Fail fast on syntax errors in Cloudflare Pages Functions before a full build."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = sorted((ROOT / "functions").rglob("*.js"))

if not FUNCTIONS:
    raise SystemExit("No Pages Functions found")

failures = []
for path in FUNCTIONS:
    result = subprocess.run(
        ["node", "--check", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        failures.append((path.relative_to(ROOT).as_posix(), result.stderr.strip() or result.stdout.strip()))

if failures:
    for path, message in failures:
        print(f"::error file={path}::{message}")
    raise SystemExit(f"{len(failures)} Pages Function syntax error(s)")

print("XUYI_PAGES_FUNCTIONS_SYNTAX_PASSED", len(FUNCTIONS), "files")
