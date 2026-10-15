"""Accessible catalogue paging links, rendered into the real shared CMS/template body.

The source HTML already contains every approved model anchor; JS only
progressively enhances visible items. Query-based page links remain crawable
without a server, cookies, client-side buttons or additional Pages functions.
"""
from html import escape
import math
import re

PAGE_SIZE=18
LEGACY_NAV=re.compile(
    r'<div class="pagination"><button id="page-prev" type="button" aria-label="([^"]+)">([^<]+)</button>'
    r'<span id="page-status" aria-live="polite"></span>'
    r'<button id="page-next" type="button" aria-label="([^"]+)">([^<]+)</button></div>'
)
CARDS=re.compile(r'<a\b[^>]*\bdata-product-card\b[^>]*>[\s\S]*?</a>',re.I)

def navigation(count,prev_label="← Prev",next_label="Next →",
               prev_aria="Previous page",next_aria="Next page"):
    pages=max(1,math.ceil(count/PAGE_SIZE))
    numbered="".join(
        '<a data-page-link="'+str(i)+'" href="?page='+str(i)+'"'
        +(' aria-current="page"' if i==1 else "")+'>'+str(i)+'</a>'
        for i in range(1,pages+1)
    )
    return (
        '<nav class="pagination" aria-label="Catalogue pages">'
        '<a id="page-prev" href="?page=1" aria-label="'+escape(prev_aria,quote=True)+'"'
        ' aria-disabled="true" tabindex="-1">'+escape(prev_label)+'</a>'
        '<span id="page-status" aria-live="polite">1 / '+str(pages)+'</span>'
        '<span class="pagination__pages">'+numbered+'</span>'
        '<a id="page-next" href="?page='+str(min(2,pages))+'" aria-label="'+escape(next_aria,quote=True)+'"'
        +(' aria-disabled="true" tabindex="-1"' if pages<=1 else "")+'>'
        +escape(next_label)+'</a></nav>'
    )

def upgrade_localized_cms(body):
    """Replace only the unmodified four-control D1 baseline; never overwrite
    an owner's custom paging HTML. Product cards and other CMS text stay intact.
    """
    cards=CARDS.findall(body)
    if not cards:return body
    def edit(m):
        return navigation(len(cards),m.group(2),m.group(4),m.group(1),m.group(3))
    return LEGACY_NAV.sub(edit,body,count=1)