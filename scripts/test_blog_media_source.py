"""Source-driven legacy/late D1 Blog image repair; owner edits always win."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from blog_media_source import blog_cover_from_cms_source,SOURCE_REPAIRS

assert len(SOURCE_REPAIRS)>=13
for slug,(old,new) in SOURCE_REPAIRS.items():
    assert new.startswith('/assets/'),(slug,new)
    for loc in ('es','pt','ru','tr'):
        index='<div class="blog-listing__grid"><a class="news-card__image" href="/blog/'+slug+'/"><img src="'+old+'" alt="CMS title"></a></div>'
        detail='<div class="blog-detail__cover"><img src="'+old+'" alt="CMS title"></div>'
        related='<article class="blog-related__item"><a href="/blog/'+slug+'/"><img src="'+old+'" alt="CMS title"></a></article>'
        for route,markup in [('/blog/',index),('/blog/'+slug+'/',detail),('/blog/another-guide/',related)]:
            fixed=blog_cover_from_cms_source(markup,route,loc)
            assert new in fixed and old not in fixed,(slug,route,loc,'baseline upgrade')
            assert blog_cover_from_cms_source(fixed,route,loc)==fixed,(slug,route,loc,'idempotent')
            manual=markup.replace(old,'/assets/blog/admin-approved-new-photo.webp')
            assert blog_cover_from_cms_source(manual,route,loc)==manual,(slug,route,loc,'CMS owner wins')
    assert blog_cover_from_cms_source('<section>New article</section>','/blog/unrelated/', 'en')=='<section>New article</section>'

assert 'repair_localized_blog_thumbnails(DIST)' not in (ROOT/'scripts/build_release.py').read_text(encoding='utf8')
print('XUYI_BLOG_MEDIA_SOURCE_CMS_OVERRIDE_AND_MISSING_PAGE_SAFE_PASSED')
