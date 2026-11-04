import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from blog_meta_description_overrides import OVERRIDES, REFERENCE_ROUTE, apply

def run():
    assert len(OVERRIDES) == 8
    for (route, locale), reviewed in OVERRIDES.items():
        duplicate = "same bicycle guide description"
        translations = {
            (REFERENCE_ROUTE, locale): {"description": duplicate},
            (route, locale): {"description": duplicate},
        }
        fields = {"title": "CMS-owned title", "description": duplicate, "mainHtml": "<h1>CMS body</h1>"}
        fixed = apply(fields, route, locale, translations)
        assert fixed["description"] == reviewed, (route, locale, fixed)
        assert fixed["title"] == fields["title"] and fixed["mainHtml"] == fields["mainHtml"]
        owner_edit = {"title": "Owner title", "description": "A newer owner-edited unique description"}
        assert apply(owner_edit, route, locale, translations) is owner_edit
        no_reference = {(route, locale): {"description": duplicate}}
        assert apply(fields, route, locale, no_reference) is fields
    assert apply({"description": "same"}, REFERENCE_ROUTE, "es", {})["description"] == "same"
    assert len({value for (route, locale), value in OVERRIDES.items() if locale == "es"}) == 2
    assert len({value for (route, locale), value in OVERRIDES.items() if locale == "pt"}) == 2
    assert len({value for (route, locale), value in OVERRIDES.items() if locale == "ru"}) == 2
    assert len({value for (route, locale), value in OVERRIDES.items() if locale == "tr"}) == 2
    print("XUYI_BLOG_META_DESCRIPTION_DEDUP_PASSED 8 locale descriptions; D1 owner edits preserved")

if __name__ == "__main__":
    run()
