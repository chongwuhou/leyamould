#!/usr/bin/env python3
"""Download and upload the reviewed legacy image manifest to LEYA R2.

This is a one-time migration helper.  It never changes D1 and only writes the
content-addressed WebP objects named by ``mould-legacy-media-manifest.json``.
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "mould-legacy-media-manifest.json"
BUCKET = "leyamould-r2"


def main() -> None:
    items = json.loads(MANIFEST.read_text(encoding="utf-8")).get("items", [])
    if not items:
        raise SystemExit("legacy media manifest is empty")
    with tempfile.TemporaryDirectory(prefix="leya-legacy-media-") as temp:
        temp_path = Path(temp)
        for index, item in enumerate(items, 1):
            source = str(item["source"])
            target = str(item["target"])
            filename = target.rsplit("/", 1)[-1]
            local = temp_path / filename
            request = urllib.request.Request(source, headers={"User-Agent": "LEYA-MOULD-R2-MIGRATION/1.0"})
            try:
                with urllib.request.urlopen(request, timeout=45) as response:
                    raw = response.read()
                image = Image.open(io.BytesIO(raw))
                image = ImageOps.exif_transpose(image).convert("RGB")
                image.thumbnail((2400, 2400), Image.Resampling.LANCZOS)
                image.save(local, "WEBP", quality=88, method=6)
            except Exception as error:
                raise SystemExit(f"legacy media conversion failed for {source}: {error}") from error
            key = "site-media/page/" + filename
            command = ["npx", "--yes", "wrangler@4.148.0", "r2", "object", "put", f"{BUCKET}/{key}", "--file", str(local), "--content-type", "image/webp", "--remote"]
            result = subprocess.run(command, cwd=ROOT, env=os.environ.copy(), text=True)
            if result.returncode:
                raise SystemExit(f"R2 upload failed for {key} (item {index}/{len(items)})")
            print(f"LEYA_LEGACY_MEDIA_UPLOADED {index}/{len(items)} {key}", flush=True)
    print(f"LEYA_LEGACY_MEDIA_MIGRATION_PASSED objects={len(items)}")


if __name__ == "__main__":
    main()
