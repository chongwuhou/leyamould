"""Export reviewed category data into a D1 import payload.

The public renderer keeps its visual/layout code in ``mould_category_pages``.
This offline converter prepares business copy and media references for a
reviewed owner import. It does not call a production endpoint or mutate D1.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mould_category_pages import DETAILS


TARGET = ROOT / "data" / "mould-product-structured.json"


def export() -> None:
    current = json.loads(TARGET.read_text(encoding="utf-8"))
    for slug, details in DETAILS.items():
        technology_title, technology_rows = details["technology"]
        category = {
            "hero": {
                "title": details["hero_title"],
                "accent": details["hero_accent"],
                "subtitle": details["hero_subtitle"],
                "image": details["hero_image"],
                "stats": [{"number": number, "label": label} for number, label in details["stats"]],
            },
            "products": [
                {"title": title, "image": image, "body": body}
                for title, image, body in details["products"]
            ],
            "advantages": [
                {"title": title, "body": body}
                for title, body in details["advantages"]
            ],
            "technology": {
                "title": technology_title,
                "items": [
                    {"title": title, "body": body, "image": image, "bullets": bullets}
                    for title, body, image, bullets in technology_rows
                ],
            },
            "samples": [{"image": image} for image in details["samples"]],
            "quality": [
                {"title": title, "body": body}
                for title, body in details["quality"]
            ],
            "testimonials": [
                {"quote": quote, "author": author, "country": country}
                for quote, author, country in details["testimonials"]
            ],
            "videos": [
                {"videoId": video_id, "title": title}
                for video_id, title in details.get("videos", [])
            ],
        }
        row = current.setdefault(slug, {})
        row["category"] = category
    TARGET.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    export()

