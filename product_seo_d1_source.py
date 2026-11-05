"""Apply only D1-owned product SEO fields during source rendering."""
from html import escape
import re

def apply_d1_product_seo(markup,slug,locale,snapshot):
    record=next((x for x in snapshot.get("productSeo",[])
        if x.get("slug")==slug and x.get("locale")==locale),None)
    if not record:return markup
    from site_renderer import SERIES
    from scripts.source_catalog_capacity_oz import source_field_allowed
    product=next((item for item in SERIES.values() if item.get("slug")==slug),None)
    allow_title=source_field_allowed(locale,product,"title",snapshot) if product else False
    allow_desc=source_field_allowed(locale,product,"description",snapshot) if product else False
    title=record.get("seoTitle")
    desc=record.get("metaDescription")
    head,sep,tail=markup.partition("</head>")
    if not sep:return markup
    changed=False
    if not allow_title and isinstance(title,str) and title.strip():
        title_html=escape(title,quote=False)
        head,count=re.subn(r"<title>[^<]*</title>","<title>"+title_html+"</title>",head,count=1)
        if count==1:
            head=re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                lambda m:m.group(1)+escape(title,quote=True)+m.group(2),head,count=1)
            changed=True
    if not allow_desc and isinstance(desc,str) and desc.strip():
        desc_html=escape(desc,quote=True)
        head=re.sub(r'(<meta name="description" content=")[^"]*(")',
            lambda m:m.group(1)+desc_html+m.group(2),head,count=1)
        head=re.sub(r'(<meta property="og:description" content=")[^"]*(")',
            lambda m:m.group(1)+desc_html+m.group(2),head,count=1)
        changed=True
    return head+sep+tail if changed else markup