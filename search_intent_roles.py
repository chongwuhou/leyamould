"""Source rendering: distinguish factory home, wholesale collection and how-to guide.

Only known original D1 title+description are replaced. Later owner edits of
either field preserve both, and a custom H1 is always protected.
"""
from pathlib import Path
from html import escape,unescape
import json,re

DATA=json.loads((Path(__file__).parent/"data/search-intent-three-landing-roles.json").read_text(encoding="utf8"))
assert DATA["schemaVersion"]==1
ROLES=DATA["routes"]

def source_role(route,locale):
    role=next((key for key,path in ROLES.items() if path==route),None)
    return DATA["languages"].get(locale,{}).get(role) if role else None

def source_intent_fields(route,locale,old_title,old_description):
    entry=source_role(route,locale)
    if not entry:return None
    base=entry["baseline"]
    if (old_title!=base["title"] or old_description!=base["description"]):return None
    return entry["preferred"]

def render_search_intent(markup,route,locale):
    entry=source_role(route,locale)
    if not entry:return markup
    title=re.search(r"<title>([^<]*)</title>",markup,re.S)
    desc=re.search(r'<meta name="description" content="([^"]*)"',markup)
    if not title or not desc:return markup
    replacement=source_intent_fields(route,locale,unescape(title.group(1)),unescape(desc.group(1)))
    if not replacement:return markup
    preferred_title,preferred_description=replacement["title"],replacement["description"]
    assert preferred_title and len(preferred_title)<=85
    assert preferred_description and len(preferred_description)<=190
    markup=markup[:title.start(1)]+escape(preferred_title)+markup[title.end(1):]
    desc=re.search(r'<meta name="description" content="([^"]*)"',markup)
    markup=markup[:desc.start(1)]+escape(preferred_description,quote=True)+markup[desc.end(1):]
    for key,value in (("og:title",preferred_title),("og:description",preferred_description)):
        markup=re.sub(r'(<meta property="'+re.escape(key)+r'" content=")[^"]*(")',lambda m:m.group(1)+escape(value,quote=True)+m.group(2),markup,count=1)
    # The WebPage and BlogPosting structured data reflect actual user-visible
    # fields. Preserve product/schema refs and editorial dates.
    def schema_change(m):
        data=json.loads(m.group(1))
        for obj in data.get("@graph",[data]):
            if not isinstance(obj,dict):continue
            if obj.get("@type")=="WebPage":
                obj["name"]=preferred_title
                obj["description"]=preferred_description
            if obj.get("@type")=="BlogPosting":
                obj["headline"]=preferred_title
                obj["description"]=preferred_description
        return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("<",r"\u003c")+"</script>"
    markup=re.sub(r'<script type="application/ld\+json">([\s\S]*?)</script>',schema_change,markup)
    heading=replacement.get("h1")
    original=entry["baseline"].get("h1")
    if heading and original:
        # This checks actual text including nested tags, so an editor-changed
        # heading is not replaced by a saved, now stale template value.
        def update_h1(m):
            visible=re.sub(r"\s+"," ",unescape(re.sub(r"<[^>]+>"," ",m.group(2)))).strip()
            if visible!=original:return m.group(0)
            return m.group(1)+escape(heading)+m.group(3)
        markup=re.sub(r"(<h1\b[^>]*>)(.*?)(</h1>)",update_h1,markup,count=1,flags=re.S)
    return markup