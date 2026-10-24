"""Shared XUYI Blog list source layout; keep CMS article cards/editor edits."""
import html
import re

LEGACY_SECONDARY_TITLES = {
    "es": "Centro de conocimientos sobre abastecimiento",
    "pt": "Centro de conhecimento sobre compras e fornecimento",
    "ru": "Центр знаний по источникам",
    "tr": "Kaynak Bilgisi Merkez",
}

# The legacy D1-owned blog listing included a decorative title just below its
# real H1. Normalize source markup prior to rendering, never generated dist.
# Require its exact reviewed title: a subsequently owner-edited header wins.
_SECONDARY = re.compile(
    r'(<section class="section blog-listing"><div class="shell">)'
    r'<div class="section__head"><div><span class="eyebrow">[^<]*</span>'
    r'<h2 class="section__title">(?P<title>[^<]*)</h2>'
    r'<p class="copy-muted">[^<]*</p></div></div>'
    r'(?=<div class="blog-listing__grid">)',
    re.S,
)


def single_blog_index_heading(main_html: str, locale: str) -> str:
    baseline = LEGACY_SECONDARY_TITLES.get(locale)
    if not baseline:
        return main_html
    match = _SECONDARY.search(main_html)
    if not match or html.unescape(match.group("title")).strip() != baseline:
        return main_html
    return main_html[:match.start()] + match.group(1) + main_html[match.end():]
