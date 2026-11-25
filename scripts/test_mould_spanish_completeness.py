#!/usr/bin/env python3
"""Rendered Spanish completeness gate for the LEYA mould release.

This is a local, deterministic check.  It does not call a translation API or
Cloudflare.  It checks the files produced by the source renderer, the reviewed
model-reference fallback, and the legacy-route redirect contract.
"""
from __future__ import annotations

import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
sys.path.insert(0, str(ROOT))
from mould_build import HMOULD_MODELS  # noqa: E402


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        if tag.lower() in {"script", "style", "svg", "noscript", "template"}:
            self.hidden += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "svg", "noscript", "template"} and self.hidden:
            self.hidden -= 1

    def handle_data(self, data: str) -> None:
        if not self.hidden and data.strip():
            self.parts.append(data)


def visible(path: Path) -> str:
    parser = VisibleText()
    parser.feed(path.read_text(encoding="utf-8"))
    return " ".join(html.unescape(" ".join(parser.parts)).split())


# These are reviewed source-language labels/sentences, not technical
# identifiers.  Product names, PET/PP/PCO/DFM/CMM and LEYA MOULD remain valid
# in an international Spanish technical page and are intentionally not listed.
ENGLISH_LEAKS = (
    "About Us", "Our Story", "Our Products", "Mould Product Families", "View Category",
    "Factory Address", "Send Us Your Inquiry", "Model Reference", "Additional Cap Model References",
    "Years of Experience", "Countries Served", "Moulds Delivered", "Learn More",
    "Quick Answers", "Still Have Questions?", "Start Your Cap Mould Project",
    "Want to See More Samples or Request a Quote?", "Need Auxiliary Equipment for Your Cap Line?",
    "Let's Work Together", "Engineering Excellence", "Technical Strength", "Quality Control & Inspection",
    "Cooperation Process", "Client Feedback", "EXPLORE OUR WORK", "PRECISION TOOLING",
    "BOTTLE CAP MACHINE", "BOTTLE CAP MOULDS", "Technical Content", "Buyer checklist",
    "Decision matrix", "Related reading", "Sources and disclosure", "Trial samples",
    "Quality Assurance", "What Buyers Say", "Common Questions", "Mould Trials", "Our Journey",
    "Why Choose LEYA MOULD", "Our Facility & Equipment", "Certifications & Quality",
    "Our Production Facilities", "Trial runs, dimensional checks", "Quality evidence is kept",
    "LEYA MOULD production references show", "What is the typical cycle time?",
    "Can one mould run", "Do you provide installation support?",
)


def main() -> None:
    files = sorted((DIST / "es").rglob("*.html"))
    if len(files) < 50:
        raise SystemExit(f"Spanish route tree unexpectedly small: {len(files)}")
    leaks: list[str] = []
    for path in files:
        source = path.read_text(encoding="utf-8")
        if '<html lang="es">' not in source:
            leaks.append(f"{path}:lang")
        if not re.search(r"<title>[^<]{20,}</title>", source):
            leaks.append(f"{path}:title")
        if not re.search(r'<meta name="description" content="[^\"]{35,}">', source):
            leaks.append(f"{path}:description")
        text = visible(path)
        for marker in ENGLISH_LEAKS:
            if marker.casefold() in text.casefold():
                leaks.append(f"{path}:{marker}")
    if not HMOULD_MODELS:
        leaks.append("models:no-published-reference-models")
    seen_models = set()
    for row in HMOULD_MODELS:
        slug = str(row.get("slug") or "").strip().lower()
        if not slug or slug in seen_models:
            leaks.append(f"model:{slug or 'unknown'}:duplicate-slug")
        seen_models.add(slug)
        es = row.get("translations", {}).get("es", {}) if isinstance(row.get("translations"), dict) else {}
        if not all(str(es.get(key) or "").strip() for key in ("title", "alt", "description")):
            leaks.append(f"model:{row.get('slug','unknown')}:es")
    redirects = (DIST / "_redirects").read_text(encoding="utf-8") if (DIST / "_redirects").is_file() else ""
    aliases = (
        "/about/about_us.html", "/about/ABOUT_US.html", "/about/FAQs.html", "/contact/contact_us.html", "/cap-samples/Sample.html",
        "/machine/Cap-Auxiliary-Machines.html", "/videolist/Cap-Mold-Video.html",
        "/news/news.html",
    )
    for alias in aliases:
        if alias + " " not in redirects and alias + "\t" not in redirects:
            leaks.append(f"redirect:{alias}")
        if (DIST / alias.lstrip("/")).is_file():
            leaks.append(f"legacy-file:{alias}")
        if (DIST / ("es" + alias)).is_file():
            leaks.append(f"legacy-file:/es{alias}")
    if leaks:
        raise SystemExit("LEYA_MOULD_SPANISH_COMPLETENESS_FAILED " + "; ".join(leaks[:40]))
    print(f"LEYA_MOULD_SPANISH_COMPLETENESS_PASSED pages={len(files)} models={len(HMOULD_MODELS)} aliases={len(aliases)}")


if __name__ == "__main__":
    main()
