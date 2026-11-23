#!/usr/bin/env python3
"""Release gate for the new LEYA MOULD public source build."""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ORIGIN = "https://leyamould.com"
LOCALES = ["en", "es"]
CATEGORIES = ["pet-preform-moulds", "bottle-cap-moulds", "bottle-moulds", "knife-fork-moulds"]


class Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag in {"img", "script", "link"}:
            value = attrs.get("src") or attrs.get("href")
            if value and value.startswith("/"):
                self.images.append(value)


manifest = json.loads((DIST / "locale-manifest.json").read_text(encoding="utf-8"))
assert [row["code"] for row in manifest["locales"]] == LOCALES, manifest
assert (DIST / "build-meta.json").is_file()
meta = json.loads((DIST / "build-meta.json").read_text(encoding="utf-8"))
assert meta["siteOrigin"] == ORIGIN
assert meta["noindex"] is True
assert meta["templateSet"] == "templates/site"

routes = ["/", "/products/", "/about/", "/manufacturing/", "/quality-control/", "/contact/", "/faq/", "/blog/", "/privacy-policy/"]
routes += ["/collections/" + slug + "/" for slug in CATEGORIES]
for locale in LOCALES:
    prefix = "" if locale == "en" else locale
    for route in routes:
        path = DIST / prefix / route.strip("/") / "index.html" if route != "/" else DIST / prefix / "index.html"
        assert path.is_file(), (locale, route, path)
        html = path.read_text(encoding="utf-8")
        assert "<main id=\"main-content\">" in html and "</html>" in html
        assert "LEYA MOULD" in html and "amyhu@leyamould.com" in html and "8613606727715" in html
        assert "XUYI" not in html and "water bottle" not in html.lower() and "drinkware" not in html.lower()
        assert '<meta name="robots" content="noindex,nofollow">' in html
        parser = Refs()
        parser.feed(html)
        for ref in parser.links + parser.images:
            if ref.startswith(("/api/", "/media/", "mailto:", "https://", "tel:")):
                continue
            target = urlsplit(ref).path.lstrip("/")
            localized = target
            if locale != "en" and localized.startswith(locale + "/"):
                localized = localized[len(locale) + 1 :]
            if not target or target.startswith("#"):
                continue
            if not (DIST / target).is_file() and not (DIST / target / "index.html").is_file():
                # The static site references only generated local routes/assets.
                raise AssertionError((locale, route, "broken local ref", ref))

home = (DIST / "index.html").read_text(encoding="utf-8")
for slug in CATEGORIES:
    assert "/collections/" + slug + "/" in home
assert "PET Preform Moulds" in home and "Bottle Cap Moulds" in home
assert "Knife &amp; Fork Moulds" in home
assert "4-55,Xicheng New Village,Huangyan Taizhou,Zhejiang Province, China" in home
assert "WhatsApp +8613606727715" in home
machine_en = (DIST / "Bottle-Cap-Machine" / "Bottle-Cap-Machine.html").read_text(encoding="utf-8")
machine_es = (DIST / "es" / "Bottle-Cap-Machine" / "Bottle-Cap-Machine.html").read_text(encoding="utf-8")
assert "nopic.gif" not in machine_en and "/assets/mould-news-placeholder.svg" in machine_en
assert "The Role of Cooling Water" in machine_en
assert "El papel de la calidad del agua" in machine_es and "The Role of Cooling Water" not in machine_es
detail_es = (DIST / "es" / "Bottle-Cap-Machine" / "cap-ejection-pin-placement.html").read_text(encoding="utf-8")
assert "Comparta con nuestro equipo de ingeniería" in detail_es
assert (DIST / "admin" / "index.html").is_file()
assert "LEYA MOULD" in (DIST / "admin" / "index.html").read_text(encoding="utf-8")
print("LEYA_MOULD_RELEASE_PASSED", len(routes), "routes x", len(LOCALES), "locales")


