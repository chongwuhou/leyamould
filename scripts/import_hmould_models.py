"""Import non-glass product model references from HMould.

The importer keeps the source catalogue auditable while making the public LEYA
catalogue independent of HMould's image host. Source thumbnails are resized and
encoded as WebP before they are added to the site assets.
"""
from __future__ import annotations

import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://www.hmould.com"
DATA_PATH = ROOT / "data/mould-models.json"
ASSET_DIR = ROOT / "assets/catalog/hmould-models"


class ProductParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_item = False
        self.capture_title = False
        self.buffer: list[str] = []
        self.item: dict[str, str] = {}
        self.items: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "li" and values.get("class") == "plist1":
            self.in_item = True
            self.item = {}
        if not self.in_item:
            return
        if tag == "a" and values.get("href"):
            self.item["sourceUrl"] = urljoin(SOURCE, values["href"] or "")
        elif tag == "img":
            if values.get("src"):
                self.item["sourceImage"] = urljoin(SOURCE, values["src"] or "")
            if values.get("alt"):
                self.item["alt"] = values["alt"] or ""
        elif tag == "span" and values.get("class") == "pro":
            self.capture_title = True
            self.buffer = []

    def handle_data(self, data: str) -> None:
        if self.capture_title:
            self.buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "span" and self.capture_title:
            self.item["title"] = " ".join("".join(self.buffer).split())
            self.capture_title = False
            self.buffer = []
        if tag == "li" and self.in_item:
            if self.item.get("sourceUrl"):
                self.items.append(dict(self.item))
            self.in_item = False


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "LEYA-MOULD-catalog-import/1.0"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def clean_slug(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "model"


def family_for(row: dict[str, str]) -> str:
    path = [part for part in urlparse(row["sourceUrl"]).path.split("/") if part]
    family_path = "/".join(path[1:-1]) if len(path) >= 3 else ""
    title = re.sub(r"[-_]+", " ", row.get("title", "").lower())
    direct = {
        "Preform-Mould": "pet-preform-mould",
        "Blow-Bottle-Mould": "blow-bottle-mould",
        "Cap-Mould/Flip-Top-Cap-Mould": "flip-top-caps-mould",
        "Cap-Mould/Self-locked-Cap-Mould": "functional-cap-mould",
        "Cap-Mould/Oil-Cap-Mould": "oil-bottle-cap-mould",
        "Cap-Mould/Cosmetic-Cap-Mould": "personal-care-cap-mould",
        "Cap-Mould/Water-Cap-Mould": "mineral-water-closure-cap-molds",
        "Cap-Mould/5-Gallon-Cap-Mould": "five-gallon-water-cap-mould",
        "Cap-Mould/Wine-Cap-Mould": "wine-cap-mould",
    }
    if family_path in direct:
        return direct[family_path]
    if "engine oil" in title:
        return "engine-oil-cap-mould"
    if "5 gallon" in title or "5-gallon" in title:
        return "five-gallon-water-cap-mould"
    if "oil" in title:
        return "oil-bottle-cap-mould"
    if any(word in title for word in ("sports", "aerosol", "easy open", "dust proof", "pesticide", "pull top", "cover")):
        return "functional-cap-mould"
    return "general-cap-mould"


def import_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for page in range(1, 11):
        url = f"{SOURCE}/products/" if page == 1 else f"{SOURCE}/products/{page}/"
        parser = ProductParser()
        parser.feed(fetch(url).decode("utf-8", "ignore"))
        rows.extend(parser.items)

    seen: set[str] = set()
    output: list[dict[str, str]] = []
    for row in rows:
        source_url = row.get("sourceUrl", "")
        if not source_url or source_url in seen or "glass-cement" in source_url.lower():
            continue
        seen.add(source_url)
        family = family_for(row)
        path_parts = [part for part in urlparse(source_url).path.split("/") if part]
        source_stem = Path(path_parts[-1]).stem if path_parts else row.get("title", "model")
        # Keep same-named models from the generic Cap Mould page and a
        # dedicated sub-category distinct; both can carry different images.
        family_path = "-".join(path_parts[1:-1]) if len(path_parts) >= 3 else family
        model_slug = clean_slug(f"{family}-{family_path}-{source_stem}")
        output.append({
            "slug": model_slug,
            "family": family,
            "title": row.get("title") or row.get("alt") or source_stem,
            "alt": row.get("alt") or row.get("title") or source_stem,
            "sourceUrl": source_url,
            "sourceImage": row.get("sourceImage", ""),
            "image": f"/assets/catalog/hmould-models/{model_slug}.webp",
            "description": "HMould catalogue model reference. Final cavity plan, steel, machine interface and production evidence are confirmed during LEYA MOULD project review.",
        })
    return output


def compress_images(rows: list[dict[str, str]]) -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    for index, row in enumerate(rows, start=1):
        source = row.get("sourceImage", "")
        target = ROOT / row["image"].lstrip("/")
        if target.is_file() and target.stat().st_size > 0:
            continue
        try:
            raw = fetch(source)
            temp = target.with_suffix(".source")
            temp.write_bytes(raw)
            with Image.open(temp) as image:
                image = image.convert("RGB")
                image.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
                image.save(target, "WEBP", quality=78, method=6)
            temp.unlink(missing_ok=True)
        except Exception as error:  # keep catalogue import auditable if one old image is unavailable
            row["image"] = "/assets/mould-placeholder.svg"
            row["imageError"] = str(error)
        if index % 10 == 0:
            print(f"compressed {index}/{len(rows)}")
        time.sleep(0.02)


def main() -> None:
    rows = import_rows()
    compress_images(rows)
    DATA_PATH.write_text(json.dumps({"schemaVersion": 1, "source": SOURCE, "excluded": ["Glass Cement Mould"], "models": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"HMOULD_MODELS_IMPORTED {len(rows)}")


if __name__ == "__main__":
    main()
