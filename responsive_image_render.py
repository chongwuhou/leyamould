"""Source-render responsive image hints; never change an editor's selected src/alt."""
from functools import lru_cache
from pathlib import Path
import html
import json
import os
import re

IMAGE = re.compile(r"<img\b[^>]*>", re.I)
SRC = re.compile(r'\bsrc="([^"]+)"', re.I)
STANDARD = "(max-width: 760px) 92vw, (max-width: 1200px) 48vw, 360px"
MAIN = "(max-width: 760px) 92vw, 48vw"
# Legacy editorial substitutions still rewrite some specific PPT placeholders
# after page rendering. Adding srcset for them would pair the replacement
# picture with previews derived from the displaced original. Preserve current
# owner/approved image mapping; migrate those legacy replacements separately.
LEGACY_REPLACED_SOURCES = frozenset({
    "/media/ppt/slide-030.webp",
    "/media/ppt/slide-037.webp",
    "/media/ppt/slide-049.webp",
    "/media/ppt/slide-059.webp",
    "/media/ppt/slide-061.webp",
})


@lru_cache(maxsize=2)
def _data(filename):
    path = Path(filename)
    return json.loads(path.read_text(encoding="utf8")) if path.is_file() else {}


def enhance_source_markup(markup):
    filename = os.environ.get("XUYI_RESPONSIVE_MANIFEST")
    if not filename:
        return markup
    data = _data(filename)
    if not data:
        return markup

    def image(match):
        tag = match.group()
        m = SRC.search(tag)
        if not m:
            return tag
        src = html.unescape(m.group(1)).split("?", 1)[0].split("#", 1)[0]
        if src in LEGACY_REPLACED_SOURCES:
            return tag
        entry = data.get(src)
        if not entry:
            return tag
        add = []
        for k in ("width", "height"):
            if not re.search(r"\b" + k + r"\s*=", tag, re.I):
                add.append(f'{k}="{entry[k]}"')
        if not re.search(r"\bsrcset\s*=", tag, re.I):
            vs = entry.get("variants") or []
            if vs:
                add.append('srcset="' + ", ".join(f'{v["url"]} {v["w"]}w' for v in vs) + '"')
                if not re.search(r"\bsizes\s*=", tag, re.I):
                    add.append('sizes="' + (MAIN if 'id="main-photo"' in tag or 'id="hero-image"' in tag else STANDARD) + '"')
        if ('id="main-photo"' in tag or 'id="hero-image"' in tag) and not re.search(r"\bfetchpriority\s*=", tag, re.I):
            add.append('fetchpriority="high"')
        return tag[:-1] + (" " + " ".join(add) if add else "") + ">"

    return IMAGE.sub(image, markup)
