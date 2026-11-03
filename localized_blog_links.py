"""Disable links to scheduled/unpublished Blog pages in localized Blog indexes only.

The CMS-owned card copy stays intact. A link is restored automatically on the next
build once its canonical English Blog route exists in the generated release.
"""
from __future__ import annotations

import html
import re
from urllib.parse import urlsplit

_BLOG_ARTICLE_ROUTE = re.compile(r"^/blog/[a-z0-9-]+/$")


def disable_unpublished_blog_links(markup: str, published_routes: set[str]) -> str:
    """Remove href from internal Blog-article anchors whose English page is absent."""
    if not isinstance(markup, str) or not markup:
        return markup

    published = set(published_routes)

    def replace(match: re.Match[str]) -> str:
        opening, body = match.group(1), match.group(2)
        href = re.search(r'\bhref\s*=\s*(["\'])(.*?)\1', opening, re.I | re.S)
        if not href:
            return match.group(0)

        raw = html.unescape(href.group(2)).strip()
        if raw.startswith("//"):
            return match.group(0)
        parts = urlsplit(raw)
        if parts.scheme or parts.netloc:
            if parts.scheme not in ("http", "https") or parts.netloc.lower() not in {
                "xuyibottles.com", "www.xuyibottles.com"
            }:
                return match.group(0)
        elif not raw.startswith("/"):
            return match.group(0)

        path = parts.path
        if path == "/blog/" or not _BLOG_ARTICLE_ROUTE.fullmatch(path) or path in published:
            return match.group(0)

        opening = re.sub(r'\s+href\s*=\s*(["\']).*?\1', "", opening, count=1, flags=re.I | re.S)
        opening = re.sub(
            r'\s+(?:aria-disabled|tabindex|data-xuyi-unpublished-route)\s*=\s*(["\']).*?\1',
            "", opening, flags=re.I | re.S
        )
        opening = opening[:-1] + (
            ' aria-disabled="true" tabindex="-1" data-xuyi-unpublished-route="'
            + html.escape(path, quote=True) + '">'
        )
        return opening + body + "</a>"

    return re.sub(r"(<a\b[^>]*>)(.*?)</a\s*>", replace, markup, flags=re.I | re.S)
