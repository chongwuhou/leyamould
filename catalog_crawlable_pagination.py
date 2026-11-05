"""Accessible catalogue paging links, rendered into the real shared CMS/template body.

The source HTML already contains every approved model anchor; JS only
progressively enhances visible items. Query-based page links remain crawable
without a server, cookies, client-side buttons or additional Pages functions.
"""
from html import escape,unescape
import math
import re

PAGE_SIZE=18
LEGACY_NAV=re.compile(
    r'<div class="pagination"><button id="page-prev" type="button" aria-label="([^"]+)">([^<]+)</button>'
    r'<span id="page-status" aria-live="polite"></span>'
    r'<button id="page-next" type="button" aria-label="([^"]+)">([^<]+)</button></div>'
)
CARDS=re.compile(r'<a\b[^>]*\bdata-product-card\b[^>]*>[\s\S]*?</a>',re.I)

CATALOG_CATEGORIES=(
    ("sports-water-bottles","Plastic Sports Water Bottles"),
    ("large-capacity-water-jugs","Large Capacity Water Jugs"),
    ("kids-water-bottles","Kids Plastic Water Bottles"),
    ("plastic-shaker-bottles","Plastic Shaker Bottles"),
    ("spray-water-bottles","Spray Water Bottles"),
    ("two-way-drinking-cups","Two-Way Drinking Cups"),
    ("titanium-vacuum-cups","Titanium Vacuum Cups"),
)

ENGLISH_NAV_LABELS=frozenset((
    "Products","All products","Sports Water Bottles","Large Capacity Water Jugs",
    "Kids Water Bottles","Protein Shaker Bottles",
    "Plastic Sports Water Bottles","Kids Plastic Water Bottles",
    "Plastic Shaker Bottles","Spray Water Bottles","Two-Way Drinking Cups",
    "Titanium Vacuum Cups",
))

def plain_nav_text(markup):
    return unescape(re.sub(r"<[^>]+>"," ",markup)).strip()

def contains_english_nav(markup):
    text=plain_nav_text(markup)
    return any(
        re.search(r"(?<![A-Za-z])"+re.escape(label)+r"(?![A-Za-z])",text,re.I)
        for label in ENGLISH_NAV_LABELS
    )

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

def upgrade_localized_catalog_navigation(body,locale,path_prefix,labels=None,current_route="/products/"):
    """Complete the legacy four-category catalog navigation in reviewed locales.

    Only the known baseline is upgraded: an existing sidebar must contain the
    original four category links and still lack at least one current category.
    Owner-edited navigation that is already current is left untouched.
    """
    labels=labels or {}
    prefix="/"+str(path_prefix).strip("/") if str(path_prefix).strip("/") else ""

    def localized(route):
        return prefix+route

    def has_route(markup,route):
        return 'href="'+localized(route)+'"' in markup or 'href="'+route+'"' in markup

    sidebar=re.compile(
        r'(<aside\b[^>]*class="[^"]*\bcatalog-side\b[^"]*"[^>]*>)'
        r'([\s\S]*?)(</aside>)',re.I
    )

    def edit_sidebar(match):
        inner=match.group(2)
        old_count=sum(1 for slug,_ in CATALOG_CATEGORIES[:4]
                      if has_route(inner,"/collections/"+slug+"/"))
        current_count=sum(1 for slug,_ in CATALOG_CATEGORIES
                          if has_route(inner,"/collections/"+slug+"/"))
        english_fallback=str(locale)!="en" and contains_english_nav(inner)
        if old_count<4 or (
            current_count==len(CATALOG_CATEGORIES) and not english_fallback
        ):
            return match.group(0)

        heading=re.search(r'<strong\b[^>]*>[\s\S]*?</strong>',inner,re.I)
        heading_html=heading.group(0) if heading else (
            "<strong>"+escape(labels.get("Products","Products"))+"</strong>"
        )
        if str(locale)!="en" and contains_english_nav(heading_html):
            heading_html="<strong>"+escape(labels.get("Products","Products"))+"</strong>"

        product=re.search(
            r'<a\b[^>]*href=["\'][^"\']*/products/["\'][^>]*>([\s\S]*?)</a>',
            inner,re.I
        )
        product_label=product.group(1).strip() if product else escape(
            labels.get("All products",labels.get("Products","Products"))
        )
        if str(locale)!="en" and contains_english_nav(product_label):
            product_label=escape(labels.get("All products",labels.get("Products","Products")))
        links=[
            '<a href="'+escape(localized("/products/"),quote=True)+'"'
            +(' class="active"' if current_route=="/products/" else "")
            +">"+product_label+"</a>"
        ]
        for slug,source_label in CATALOG_CATEGORIES:
            route="/collections/"+slug+"/"
            links.append(
                '<a href="'+escape(localized(route),quote=True)+'"'
                +(' class="active"' if current_route==route else "")
                +">"+escape(labels.get(source_label,source_label))+"</a>"
            )
        return match.group(1)+heading_html+"\n"+"\n".join(links)+"\n"+match.group(3)

    body=sidebar.sub(edit_sidebar,body,count=1)

    if current_route=="/products/":
        category_select=re.compile(
            r'(<select\b[^>]*\bdata-catalog-category\b[^>]*>)'
            r'([\s\S]*?)(</select>)',re.I
        )
        def edit_select(match):
            inner=match.group(2)
            old_count=sum(
                1 for slug,_ in CATALOG_CATEGORIES[:4]
                if re.search(r'value=["\']'+re.escape(slug)+r'["\']',inner,re.I)
            )
            missing=[
                (slug,source_label) for slug,source_label in CATALOG_CATEGORIES
                if not re.search(r'value=["\']'+re.escape(slug)+r'["\']',inner,re.I)
            ]
            if old_count<4 or not missing:
                return match.group(0)
            additions="".join(
                "\n<option value=\""+escape(slug,quote=True)+"\">"
                +escape(labels.get(source_label,source_label))
                +"</option>"
                for slug,source_label in missing
            )
            return match.group(1)+inner+additions+match.group(3)
        body=category_select.sub(edit_select,body,count=1)
    return body
