#!/usr/bin/env python3
"""Move legacy cap-molds.com pictures to the LEYA R2 media namespace.

The source sites are owner-controlled.  This utility makes one deterministic
inventory, rewrites only image URLs in checked-in text sources, and prepares a
manifest for the one-time R2 upload step.  Every output is an sRGB WebP and the
public path is accepted by the existing ``/media/page/:filename`` proxy.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "mould-legacy-media-manifest.json"
URL_RE = re.compile(r"https://www\.cap-molds\.com[^\"'\s<>)]*?\.(?:jpg|jpeg|png|gif|webp)(?:\?[^\"'\s<>)]*)?", re.I)
TEXT_EXTS = {".py", ".json", ".html", ".js", ".css", ".md"}
SKIP_PARTS = {".git", "dist", "__pycache__", ".tmp-about-audit", ".tmp-about-reference"}
DYNAMIC_URLS = [f"https://www.cap-molds.com/upload/caps/Bottle-cap-sample{i:02d}.jpg" for i in range(1, 22)]


def source_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        if any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts):
            continue
        if path == MANIFEST:
            continue
        if "blog-source-images" in path.parts:
            continue
        files.append(path)
    return files


def target_for(url: str) -> str:
    digest = hashlib.md5(url.encode("utf-8"), usedforsecurity=False).hexdigest()
    return f"/media/page/{digest}.webp"


def inventory() -> dict[str, dict]:
    records: dict[str, dict] = {}
    if MANIFEST.is_file():
        try:
            for row in json.loads(MANIFEST.read_text(encoding="utf-8")).get("items", []):
                if isinstance(row, dict) and str(row.get("source", "")).startswith("https://www.cap-molds.com/"):
                    records[str(row["source"])] = row
        except (OSError, ValueError):
            pass
    for path in source_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for url in URL_RE.findall(text):
            if url not in records:
                parsed = urlparse(url)
                filename = Path(parsed.path).name or "legacy-image"
                records[url] = {
                    "source": url,
                    "target": target_for(url),
                    "filename": filename,
                    "r2Key": "site-media/page/" + target_for(url).rsplit("/", 1)[-1],
                    "contentType": "image/webp",
                    "conversion": "sRGB WebP, max 2400px, quality 88",
                }
    for url in DYNAMIC_URLS:
        if url not in records:
            records[url] = {
                "source": url,
                "target": target_for(url),
                "filename": Path(urlparse(url).path).name,
                "r2Key": "site-media/page/" + target_for(url).rsplit("/", 1)[-1],
                "contentType": "image/webp",
                "conversion": "sRGB WebP, max 2400px, quality 88",
            }
    return dict(sorted(records.items()))


def main() -> None:
    records = inventory()
    MANIFEST.write_text(
        json.dumps({"schemaVersion": 1, "site": "leyamould", "items": list(records.values())}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if "--rewrite" in sys.argv:
        replacements = {url: record["target"] for url, record in records.items()}
        changed = 0
        for path in source_files():
            try:
                before = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            after = before
            for old, new in replacements.items():
                after = after.replace(old, new)
            if after != before:
                path.write_text(after, encoding="utf-8")
                changed += 1
        print(f"LEYA_LEGACY_MEDIA_REWRITTEN urls={len(records)} files={changed}")
    else:
        print(f"LEYA_LEGACY_MEDIA_INVENTORY urls={len(records)} manifest={MANIFEST}")


if __name__ == "__main__":
    main()
