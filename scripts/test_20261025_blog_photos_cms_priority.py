"""October 25 source photo curation: all five locales, owner priority and unique covers."""
import json,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from blog_media_source import blog_cover_from_cms_source,PHOTO_20261025,PHOTO_CORRECTIONS
from blog_editorial import GUIDES
assert len(PHOTO_20261025)==3
assert set(PHOTO_20261025).issubset(GUIDES)
selected={entry['photo'] for entry in PHOTO_20261025.values()}
assert len(selected)==3
assert not selected.intersection(x['photo'] for x in PHOTO_CORRECTIONS.values())
for slug,entry in PHOTO_20261025.items():
    old,new=entry['baseline'],entry['photo']
    assert old!=new
    assert GUIDES[slug]['cover']==new,slug
    photo=ROOT/new.lstrip('/')
    assert photo.is_file(),photo
    with Image.open(photo) as img:assert img.width>=960 and img.height>=700,(photo,img.size)
    for lang in ('es','pt','ru','tr'):
        index='<section class="section blog-listing"><div class="shell"><div class="blog-listing__grid"><a class="news-card__image" href="/blog/'+slug+'/"><img src="'+old+'" alt="Owner choice"></a></div></div></section>'
        detail='<div class="blog-detail__cover"><img src="'+old+'" alt="Owner article"></div>'
        for html,route in ((index,'/blog/'),(detail,'/blog/'+slug+'/')):
            updated=blog_cover_from_cms_source(html,route,lang)
            assert new in updated and old not in updated,(slug,lang,route)
            assert updated==blog_cover_from_cms_source(updated,route,lang),'idempotence'
            edited=html.replace(old,'/assets/blog/owner-new-choice.webp')
            assert blog_cover_from_cms_source(edited,route,lang)==edited,(slug,lang,'CMS image priority')
            assert blog_cover_from_cms_source(html,'/blog/completely-different-post/',lang)==html
runtime=(ROOT/'functions/blog/[[path]].js').read_text('utf8')
assert 'PHOTO_20261025' in runtime
assert 'post.cover===newApproved.baseline' in runtime
print('XUYI_20261025_IMAGES_CMS_OWNER_PRIORITY_5_LOCALES_PASSED')