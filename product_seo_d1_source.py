"""The D1 product SEO source is applied in shared renderers, before page write."""
from html import escape
import re

def apply_d1_product_seo(markup,slug,locale,snapshot):
    record=next((x for x in snapshot.get("productSeo",[])
        if x.get("slug")==slug and x.get("locale")==locale),None)
    if not record:return markup
    title=record.get("seoTitle")
    desc=record.get("metaDescription")
    if not isinstance(title,str) or not isinstance(desc,str) or not title.strip() or not desc.strip():
        return markup
    head,sep,tail=markup.partition("</head>")
    if not sep:return markup
    title_html=escape(title,quote=False)
    desc_html=escape(desc,quote=True)
    head,count=re.subn(r"<title>[^<]*</title>","<title>"+title_html+"</title>",head,count=1)
    if count!=1:return markup
    head=re.sub(r'(<meta name="description" content=")[^"]*(")',
        lambda m:m.group(1)+desc_html+m.group(2),head,count=1)
    head=re.sub(r'(<meta property="og:title" content=")[^"]*(")',
        lambda m:m.group(1)+escape(title,quote=True)+m.group(2),head,count=1)
    head=re.sub(r'(<meta property="og:description" content=")[^"]*(")',
        lambda m:m.group(1)+desc_html+m.group(2),head,count=1)
    return head+sep+tail
