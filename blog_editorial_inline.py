"""Reviewed, paragraph-level editing of the 16 published buyer guides.

Authored paragraphs live in data/blog-inline-edits-reviewed-part{1,2}.json;
D1 remains canonical for CMS-owned localized HTML. These edits only merge into
the exact pre-reviewed D1 source; changed article bodies are never overwritten.
The three editorially chosen related guides are moved *inside* the article at
its end, rather than counted merely because a generic outer template exists.
"""
from pathlib import Path
from html import escape
import hashlib,json,re
ROOT=Path(__file__).resolve().parent
POSTS={}
for part in ("part1","part2"):
    POSTS.update(json.loads((ROOT/f"data/blog-inline-edits-reviewed-{part}.json").read_text(encoding="utf8")))
BASE=json.loads((ROOT/"data/blog-product-proof-source.json").read_text(encoding="utf8"))["cmsLocaleSourceHashes"]
LANGS=("en","es","pt","ru","tr")
LOCALE_MODEL={"en":"model","es":"modelo","pt":"modelo","ru":"модель","tr":"model"}
SECTION=re.compile(r'(<section class="blog-section"[^>]*><h2>.*?</h2><p>)(.*?)(</p></section>)',re.S)
RELATED='<section class="section section--soft blog-related">'
ARTICLE_END='</article></div></div></section>'

def _source_note(slug,section_index,locale):
    decisions=[item for item in POSTS.get(slug,()) if item["section"]==section_index]
    if len(decisions)>1:raise ValueError("More than one product in a reviewed article section: "+slug)
    if not decisions:return ""
    note=decisions[0]
    pattern=note["text"][locale]
    assert pattern.count("{model}")==1,(slug,section_index,locale)
    sku=note["sku"]
    prefix="" if locale=="en" else "/"+locale
    model='<a class="blog-editorial__product-link" href="'+prefix+'/products/'+escape(sku)+'/">'+escape(LOCALE_MODEL[locale]+" "+sku)+'</a>'
    front,back=pattern.split("{model}")
    return ' <span class="blog-editorial__product-note" data-editorial-model="'+escape(sku)+'">'+escape(front)+model+escape(back)+'</span>'

def english_note(slug,section_index):
    """Called by source blog_editorial.render_article before HTML is emitted."""
    return _source_note(slug,section_index,"en")

def reviewed_localized_article(body,route,locale,source_original):
    if locale not in LANGS or locale=="en" or not route.startswith("/blog/"):return body
    slug=route.removeprefix("/blog/").strip("/")
    if slug not in POSTS:return body
    # An administrator's source body has the last word, even if only one
    # phrase changed. Pass the *unaltered* snapshot body separately because
    # reviewed ES/TR terminology corrections may have just run on 'body'.
    if hashlib.sha256(source_original.encode("utf8")).hexdigest()!=BASE[slug][locale]:return body
    if 'data-editorial-model="' in body:return body
    sections=SECTION.findall(body)
    if len(sections)!=6:raise ValueError(f"Expected 6 source article paragraphs: {slug} {locale} got {len(sections)}")
    seen=[0]
    def replace(m):
        i=seen[0];seen[0]+=1
        return m.group(1)+m.group(2)+_source_note(slug,i,locale)+m.group(3)
    body=SECTION.sub(replace,body)
    if seen[0]!=6:raise ValueError("Incomplete editorial article "+slug)
    # The published translation already has three *selected* related guides,
    # but the generic card section was outside the article. Move that SAME
    # source-owned section inside the article, immediately after the CTA.
    # No additional auto-related block and no duplication.
    p=body.rfind(RELATED)
    if p<0 or body.count(RELATED)!=1:raise ValueError("Missing approved related posts "+slug)
    head,tail=body[:p],body[p:]
    if not head.endswith(ARTICLE_END) or not tail.endswith("</section>"):
        raise ValueError("Unsafe related-guide template shape "+slug+" "+locale)
    return head[:-len(ARTICLE_END)]+tail+ARTICLE_END