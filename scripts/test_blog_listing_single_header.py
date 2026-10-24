"""Regression: one Blog index header; all reviewed locales and editor priority."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from blog_listing_layout import LEGACY_SECONDARY_TITLES,single_blog_index_heading


def fixture(title):
    return ('<section class="page-intro"><div class="shell"><h1>Buyer guides</h1></div></section>'
            '<section class="section blog-listing"><div class="shell">'
            '<div class="section__head"><div><span class="eyebrow">BUYER</span>'
            '<h2 class="section__title">'+title+'</h2>'
            '<p class="copy-muted">CMS summary</p></div></div>'
            '<div class="blog-listing__grid"><article class="news-card">Post one</article>'
            '<article class="news-card">Post two</article></div></div></section>')

for loc,title in LEGACY_SECONDARY_TITLES.items():
    original=fixture(title)
    cleaned=single_blog_index_heading(original,loc)
    assert cleaned.count('class="page-intro"')==1
    assert cleaned.count('class="section__head"')==0
    assert cleaned.count('class="news-card"')==2
    assert cleaned.count('class="blog-listing__grid"')==1
    assert single_blog_index_heading(cleaned,loc)==cleaned
    owner=fixture('Owner edited heading')
    assert single_blog_index_heading(owner,loc)==owner,(loc,'owner copy is authoritative')
    expanded=original.replace('Post two','Post two plus three NEW CMS articles')
    assert 'NEW CMS articles' in single_blog_index_heading(expanded,loc)

# Optional real CMS source check: no assumptions about future text, publication
# status, number of articles or number of active locales.
snapshot=ROOT/'_local_ops/build-snapshot.json'
if snapshot.is_file():
    for row in json.loads(snapshot.read_text(encoding='utf8')).get('translations',[]):
        if row.get('resourceId')!='page:/blog/' or row.get('locale') not in LEGACY_SECONDARY_TITLES:
            continue
        loc=row['locale']; original=(row.get('content') or {}).get('mainHtml','')
        cleaned=single_blog_index_heading(original,loc)
        assert cleaned.count('class="news-card"')==original.count('class="news-card"')
        assert single_blog_index_heading(cleaned,loc)==cleaned

source=(ROOT/'build.py').read_text(encoding='utf8')
portion=source[source.index('def blog_index():'):source.index('\ndef blog_article(')]
assert 'Sourcing Knowledge Center' not in portion
runtime=(ROOT/'functions/blog/[[path]].js').read_text(encoding='utf8')
assert '<h2 class="section__title">Sourcing Knowledge Center' not in runtime
print('XUYI_BLOG_SINGLE_HEADER_FIVE_LOCALES_CMS_PRIORITY_PASSED')
