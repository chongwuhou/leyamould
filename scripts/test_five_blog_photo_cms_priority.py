"""Five reviewed blog photo selections: exact D1 baselines and CMS priority."""
import json,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from blog_media_source import blog_cover_from_cms_source,PHOTO_CORRECTIONS

assert len(PHOTO_CORRECTIONS)==5
assets=set()
for slug,entry in PHOTO_CORRECTIONS.items():
    original,selected=entry['baseline'],entry['photo']
    assert original!=selected and original.startswith('/assets/') and selected.startswith('/assets/')
    assert selected not in assets,(slug,'duplicate approved photo')
    assets.add(selected)
    pic=ROOT/selected.lstrip('/')
    assert pic.is_file(),(slug,'photo missing')
    with Image.open(pic) as img:
        assert img.width>=960 and img.height>=700,(slug,'insufficient photo resolution')
    for loc in ('es','pt','ru','tr'):
        index='<section class="section blog-listing"><div class="shell"><div class="blog-listing__grid"><a class="news-card__image" href="/blog/'+slug+'/"><img src="'+original+'" alt="CMS title"></a></div></div></section>'
        detail='<div class="blog-detail__cover"><img src="'+original+'" alt="CMS title"></div>'
        updated=blog_cover_from_cms_source(index,'/blog/',loc)
        assert selected in updated and original not in updated,(slug,loc,'index')
        assert blog_cover_from_cms_source(updated,'/blog/',loc)==updated
        updated=blog_cover_from_cms_source(detail,'/blog/'+slug+'/',loc)
        assert selected in updated and original not in updated,(slug,loc,'hero')
        owner=index.replace(original,'/assets/blog/editor-replaced.webp')
        assert blog_cover_from_cms_source(owner,'/blog/',loc)==owner,(slug,loc,'owner image priority')
        owner=detail.replace(original,'/assets/blog/editor-replaced.webp')
        assert blog_cover_from_cms_source(owner,'/blog/'+slug+'/',loc)==owner,(slug,loc,'owner hero priority')
        assert blog_cover_from_cms_source(detail,'/blog/a-new-article/',loc)==detail

# Social preview must follow the CMS-selected localized article hero, not
# the inherited English <head> photo. Idempotent and supports new CMS covers.
from blog_media_source import article_social_image_from_cms_source
import json as _json
for locale in ('es','pt','ru','tr'):
    page = ('<meta property="og:image" content="https://xuyibottles.com/assets/old.webp">'
            '<meta name="twitter:image" content="https://xuyibottles.com/assets/old.webp">'
            '<script type="application/ld+json">'
            +_json.dumps({"@context":"https://schema.org","@graph":[{"@type":"BlogPosting",
              "image":["https://xuyibottles.com/assets/old.webp"]}]})
            +'</script><main><div class="blog-detail__cover"><img src="/assets/editor-selected.webp" alt="Owner"></div></main>')
    updated=article_social_image_from_cms_source(page,'/blog/owner-example/')
    assert updated.count('https://xuyibottles.com/assets/editor-selected.webp')==3,(locale,updated)
    assert article_social_image_from_cms_source(updated,'/blog/owner-example/')==updated
    owner_new=page.replace('/assets/editor-selected.webp','/media/editor-new.webp')
    updated_new=article_social_image_from_cms_source(owner_new,'/blog/owner-example/')
    assert updated_new.count('https://xuyibottles.com/media/editor-new.webp')==3
    assert article_social_image_from_cms_source(page,'/blog/')==page
print('XUYI_FIVE_BLOG_PHOTOS_SOURCE_CMS_OWNER_PRIORITY_ALL_FIVE_LOCALES_PASSED')