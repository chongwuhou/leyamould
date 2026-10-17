"""Stable release assertions for CMS-owned rendered product pages.

Historic intro source copy still has its own exact-content/idempotency checks.
A later D1 owner edit or native template revision may legitimately suppress
the legacy `data-pilot-intro` marker; the final page must still be a real,
substantial, model-specific page and must not duplicate historical inserts.
"""
import html,re
from pathlib import Path

def check_product_page(filename,sku,editorial_text=None,*,requires_old_marker=False):
    document=Path(filename).read_text(encoding="utf8")
    assert document.count('<main id="main-content">')==1,(sku,"main missing")
    main=document.split('<main id="main-content">',1)[1].split('</main>',1)[0]
    assert main.count("<h1")==1,(sku,"title missing/duplicated")
    assert len(re.sub(r"<[^>]+>"," ",main).split())>=160,(sku,"thin/empty content")
    assert sku.casefold() in html.unescape(re.sub(r'<[^>]+>',' ',main)).casefold(),(sku,"model identity absent")
    pattern=r'<p\b(?=[^>]*data-pilot-intro="'+re.escape(sku)+r'")[^>]*>(.*?)</p>'
    matches=re.findall(pattern,main,re.S)
    assert len(matches)<=1,(sku,"duplicate legacy introduction")
    if requires_old_marker:assert len(matches)==1,(sku,"legacy baseline intro disappeared")
    if matches and editorial_text:
        actual=html.unescape(re.sub(r"<[^>]+>","",matches[0]))
        assert actual==editorial_text,(sku,"unapproved legacy intro differs")
    return len(matches)