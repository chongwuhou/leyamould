"""Canonical slugs for five legacy Chinese-labelled transparent bottle variants.

The regular and transparent variants are *distinct* factory records.
Preserve D1/CMS-edited copy, only normalize routing and local internal URLs.
"""
from __future__ import annotations
import re

ALIASES = {
    "2306---": "2306-transparent",
    "2307---": "2307-transparent",
    "2308---": "2308-transparent",
    "2400---": "2400-transparent",
    "2401---": "2401-transparent",
}
REVERSE = {new:old for old,new in ALIASES.items()}
PREFIXES = ("", "es", "pt", "ru", "tr")

def route(old_or_new):
    """Route-only normalization; never merge the two factory model variants."""
    parts=old_or_new.split("/")
    if len(parts)>=4 and parts[1]=="products" and parts[2] in ALIASES:
        parts[2]=ALIASES[parts[2]]
    return "/".join(parts)

def source_redirects(locales=PREFIXES):
    result=[]
    for prefix in locales:
        root=("/"+prefix if prefix else "")
        for legacy,clean in ALIASES.items():
            result.append(f"{root}/products/{legacy}/ {root}/products/{clean}/ 301")
    return result

def normalize_local_links(text):
    """Retarget only exact known incorrect href URLs; preserve owner prose."""
    if not isinstance(text,str):return text
    for legacy,clean in ALIASES.items():
        text=re.sub(r'(?<=href=")(/((?:es|pt|ru|tr)/)?products/)'+re.escape(legacy)+r'(/(?:#[^"]*)?)',
                    lambda m:m.group(1)+clean+m.group(3),text)
        # The same legacy slug was also used as an inquiry-form URL parameter.
        # Keep the model reference valid without rewriting article prose.
        text=re.sub(r"([?&]model=)"+re.escape(legacy)+r"(?=[&#\"]|$)",lambda m:m.group(1)+clean,text)
    return text