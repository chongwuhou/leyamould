"""Apply explicit D1 product SEO fields during source rendering.

Product SEO rows are the CMS owner's authoritative title and description. Source
recommendations may fill only when no D1 row exists; once a row exists, preserve
it exactly, including reviewed capacity and conditional material wording.
"""
from html import escape
import re


def apply_d1_product_seo(markup, slug, locale, snapshot):
    record = next(
        (
            x
            for x in snapshot.get("productSeo", [])
            if x.get("slug") == slug and x.get("locale") == locale
        ),
        None,
    )
    if not record:
        return markup

    title = record.get("seoTitle")
    desc = record.get("metaDescription")
    head, sep, tail = markup.partition("</head>")
    if not sep:
        return markup

    changed = False
    if isinstance(title, str) and title.strip():
        title_html = escape(title, quote=False)
        head, count = re.subn(
            r"<title>[^<]*</title>",
            "<title>" + title_html + "</title>",
            head,
            count=1,
        )
        if count == 1:
            head = re.sub(
                r'(<meta property="og:title" content=")[^"]*(")',
                lambda match: match.group(1) + escape(title, quote=True) + match.group(2),
                head,
                count=1,
            )
            changed = True

    if isinstance(desc, str) and desc.strip():
        desc_html = escape(desc, quote=True)
        head = re.sub(
            r'(<meta name="description" content=")[^"]*(")',
            lambda match: match.group(1) + desc_html + match.group(2),
            head,
            count=1,
        )
        head = re.sub(
            r'(<meta property="og:description" content=")[^"]*(")',
            lambda match: match.group(1) + desc_html + match.group(2),
            head,
            count=1,
        )
        changed = True

    return head + sep + tail if changed else markup
