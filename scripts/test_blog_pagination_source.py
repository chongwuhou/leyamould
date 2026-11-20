"""XUYI Blog pager must originate in the Blog template and preserve all CMS links."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent.parent
site=(ROOT/"site_renderer.py").read_text(encoding="utf8")
build=(ROOT/"build.py").read_text(encoding="utf8")
route=(ROOT/"functions/blog/[[path]].js").read_text(encoding="utf8")
cms=(ROOT/"functions/_shared/blog-cms.js").read_text(encoding="utf8")
source=(ROOT/"assets/blog-pagination.js").read_text(encoding="utf8")
assert 'blog_pager=False' in site
assert 'blog_pager=(slug=="blog")' in build
assert site.count('/assets/blog-pagination.js')==1
# D1-powered listing must inherit the pager from the canonical static shell.
# composePage replaces only <main>, preserving the shared <head> on CMS updates.
assert 'const template=await assetHtml(context,"/blog/index.html");' in route
assert 'composePage(template,body,null,"/blog/")' in route
assert 'let html=template.replace(/<main id="main-content">' in cms
assert 'PAGE_SIZE = 12' in source
assert 'document.documentElement.lang' in source
assert 'window.history.pushState' in source and '"popstate"' in source
assert 'card.hidden =' in source and 'img.loading = "lazy"' in source
assert source.count('const cards =')==1
locale_roots=[("", "en")]
dist_root=ROOT/"dist"
if dist_root.exists():
    for directory in sorted(dist_root.iterdir(), key=lambda p:p.name):
        if directory.is_dir() and directory.name not in {"admin","api"} and (directory/"blog/index.html").exists():
            locale_roots.append((directory.name, directory.name))
for prefix, label in locale_roots:
    path=ROOT/"dist"/((prefix+"/" if prefix else "")+"blog/index.html")
    if path.exists():
        page=path.read_text(encoding="utf8")
        assert page.count('/assets/blog-pagination.js')==1,(label,'shared template script')
        assert page.count('class="blog-listing__grid"')==1
        assert page.count('class="news-card"')>=12
        canonical_prefix=re.escape(prefix+"/" if prefix else "")
        assert re.search(r'<link rel="canonical" href="https://leyamould.com/'+canonical_prefix+r'blog/">',page)
print('XUYI_BLOG_LOCALE_SOURCE_PAGER_AND_CMS_GROWTH_PASSED')