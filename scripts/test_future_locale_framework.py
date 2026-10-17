#!/usr/bin/env python3
"""Prove that a *sixth* D1 locale needs no hardcoded SEO/JSON-LD code edits.

Fully isolated: synthetic reviewed content and UI mappings live in a temporary
directory and never enter production D1, the XUYI catalog or GitHub.
"""
from pathlib import Path
from copy import deepcopy
import importlib.util,json,re,shutil,tempfile,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import locale_registry as registry
import home_banner_config as banner
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location("future_locale_renderer",ROOT/"scripts/render_locales.py")
renderer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
SOURCE="fr"   # synthetic test case; *not* a public French translation
source_ui=renderer.UI_TRANSLATIONS["es"]
source_runtime=renderer.RUNTIME_UI_TRANSLATIONS["es"]
source_contact=renderer.CONTACT_FORM_TRANSLATIONS["es"]

with tempfile.TemporaryDirectory(prefix="xuyi-future-locale-test-") as folder:
    temp=Path(folder)
    (temp/"deployment").mkdir()
    shutil.copy2(ROOT/"deployment/site.config.json",temp/"deployment/site.config.json")
    for directory in ("data",):
        (temp/directory).mkdir()
    languages={"sourceLocale":"en","defaultLocale":"en","languages":[
        {"code":"en","pathPrefix":"","enabled":True,"publishReady":True,"nativeName":"English","sortOrder":10},
        {"code":SOURCE,"pathPrefix":SOURCE,"enabled":True,"publishReady":True,"nativeName":"Français","sortOrder":20}]}
    state={"site":"xuyi-drinkware-site","languages":languages}
    original_root=registry.ROOT
    registry.ROOT=temp
    try:
        try:registry.approved_locales(state)
        except (ValueError,FileNotFoundError) as error:
            assert "lacks reviewed" in str(error) or "ui-translations.json" in str(error),str(error)
        else:raise AssertionError("New publish-ready locale incorrectly accepted without UI resources")
        for name,path in registry._RESOURCES.items():
            data=json.loads((ROOT/path).read_text(encoding="utf-8"))
            data[SOURCE]=deepcopy(data["es"])
            file=temp/path
            file.parent.mkdir(parents=True,exist_ok=True)
            file.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
        assert [l["code"] for l in registry.approved_locales(state)]==["en",SOURCE]
        # CMS display order may change without migrating the English root URL.
        order=deepcopy(state)
        order["languages"]["languages"][0]["sortOrder"]=300
        assert [l["code"] for l in registry.approved_locales(order)]==["en",SOURCE]
        try:banner.config_for(state)
        except ValueError as error:assert "Missing reviewed fr banner text" in str(error),str(error)
        else:raise AssertionError("Missing reviewed Banner was not blocked")
        state["banners"]=deepcopy(banner.DEFAULT)
        for slide in state["banners"]["slides"]:
            slide["translations"][SOURCE]=deepcopy(slide["translations"]["es"])
        banner.config_for(state)
        body='<section class="section"><div class="shell"><h1>QA sixth-language catalog page</h1><p>'+(
            "Synthetic test text for URL, metadata, and structured data generation. "
            "It must never be published to the live site.")+'</p></div></section>'
        state["translations"]=[
            {"locale":SOURCE,"resourceId":"page:"+route,
             "content":{"title":"QA Locale "+route+" | XUYI","description":"Isolated synthetic title and description for "+route,
                        "mainHtml":body}}
            for route in ("/","/about/")]
        renderer.UI_TRANSLATIONS[SOURCE]=deepcopy(source_ui)
        renderer.RUNTIME_UI_TRANSLATIONS[SOURCE]=deepcopy(source_runtime)
        renderer.CONTACT_FORM_TRANSLATIONS[SOURCE]=deepcopy(source_contact)
        dist=temp/"dist"
        for route in ("index.html","about/index.html","contact/index.html"):
            target=dist/route
            target.parent.mkdir(parents=True,exist_ok=True)
            source=(ROOT/"dist"/route).read_text(encoding="utf-8")
            source=re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+">',"",source)
            target.write_text(source,encoding="utf-8")
        (dist/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'+
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+
            '<url><loc>https://xuyibottles.com/</loc></url>'+
            '<url><loc>https://xuyibottles.com/about/</loc></url>'+
            '<url><loc>https://xuyibottles.com/contact/</loc></url></urlset>',encoding="utf-8")
        fixture=temp/"reviewed-snapshot.json"
        fixture.write_text(json.dumps(state,ensure_ascii=False),encoding="utf-8")
        renderer.DIST=dist
        renderer.SNAPSHOT=fixture
        # No approved localized homepage? Publishing MUST fail.
        without_home=deepcopy(state)
        without_home["translations"]=[x for x in state["translations"] if x["resourceId"]!="page:/"]
        fixture.write_text(json.dumps(without_home,ensure_ascii=False),encoding="utf-8")
        try:renderer.main()
        except RuntimeError as error:assert "reviewed localized homepage" in str(error),str(error)
        else:raise AssertionError("Locale published without a reviewed homepage")
        fixture.write_text(json.dumps(state,ensure_ascii=False),encoding="utf-8")
        renderer.main()
        manifest=json.loads((dist/"locale-manifest.json").read_text(encoding="utf-8"))
        assert [x["code"] for x in manifest["locales"]]==["en",SOURCE]
        assert manifest["routes"][SOURCE]==["/","/about/"]
        english=(dist/"about/index.html").read_text(encoding="utf-8")
        localized=(dist/SOURCE/"about/index.html").read_text(encoding="utf-8")
        assert 'hreflang="fr" href="https://xuyibottles.com/fr/about/"' in english
        assert 'hreflang="x-default" href="https://xuyibottles.com/about/"' in localized
        assert '<link rel="canonical" href="https://xuyibottles.com/fr/about/">' in localized
        assert '"inLanguage":"fr"' in localized
        assert 'property="og:title" content="QA Locale /about/ | XUYI"' in localized
        assert '<loc>https://xuyibottles.com/fr/about/</loc>' in (dist/"sitemap.xml").read_text(encoding="utf-8")
        assert not (dist/SOURCE/"contact/index.html").exists()
        english_only=(dist/"contact/index.html").read_text(encoding="utf-8")
        assert 'hreflang="en" href="https://xuyibottles.com/contact/"' in english_only
        assert 'hreflang="x-default" href="https://xuyibottles.com/contact/"' in english_only
        assert 'hreflang="fr" href="https://xuyibottles.com/fr/contact/"' not in english_only
        renderer.main()
        assert (dist/"contact/index.html").read_text(encoding="utf-8").count(
            'hreflang="en" href="https://xuyibottles.com/contact/"')==1
        assert "fr" not in [x["code"] for x in registry.approved_locales({
            **state,"languages":{**languages,"languages":[languages["languages"][0],
                {**languages["languages"][1],"publishReady":False}]}})]
        print("XUYI_FUTURE_LOCALE_FRAMEWORK_TEST_PASSED sixth locale, approved URLs only, fail-closed prereqs")
    finally:
        registry.ROOT=original_root
        renderer.UI_TRANSLATIONS.pop(SOURCE,None)
        renderer.RUNTIME_UI_TRANSLATIONS.pop(SOURCE,None)
        renderer.CONTACT_FORM_TRANSLATIONS.pop(SOURCE,None)
