"""Single build-time source of truth for XUYI's *published* locales.

The saved D1 language configuration defines codes and path prefixes. New
languages do NOT become public just because an option exists in the CMS:
published locales must have reviewed UI/runtime/form resources and an exact
English source route + translated route before SEO alternates are generated.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
CONFIG=json.loads((ROOT/"deployment/site.config.json").read_text(encoding="utf-8"))
if CONFIG.get("localizationFrameworkVersion")!=2:
    raise ValueError("XUYI multilingual SEO framework must use the reviewed v2 locale registry")
DEFAULT=CONFIG["site"]["defaultLocale"]
ORIGIN=CONFIG["site"]["origin"]
PUBLISHED_CODES={str(code).strip().lower() for code in CONFIG["site"].get("publishedLocales",[]) if str(code).strip()}
_CODE=re.compile(r"^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$")
_PREFIX=re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?$")
_RESERVED={"admin","api","assets","media","products","collections","blog",
           "capabilities","about","contact","faq","privacy-policy","sitemap"}
_RESOURCES={
 "header/footer": "data/ui-translations.json",
 "dynamic UI": "data/runtime-ui-translations.json",
 "contact form": "data/contact-form-translations.json",
 "Blog date labels": "data/blog-date-labels.json",
 "gallery short titles": "data/gallery-short-titles.json",
}

def approved_locales(state,require_resources=True):
    """Return ordered public locale configurations, fail-closed on bad setup."""
    config=(state.get("languages") or {}) if isinstance(state,dict) else {}
    source=config.get("sourceLocale",DEFAULT)
    default=config.get("defaultLocale",DEFAULT)
    # Current English origin is a design constraint, not a claim to support
    # arbitrary default-locale switching without migrating canonical URLs.
    if default!=DEFAULT or source!=DEFAULT:
        raise ValueError("XUYI default/source locale migration needs dedicated approval and URL redirects")
    all_rows=config.get("languages") or [
       {"code":"en","pathPrefix":"","enabled":True,"publishReady":True,"nativeName":"English","sortOrder":10},
       {"code":"es","pathPrefix":"es","enabled":True,"publishReady":True,"nativeName":"Español","sortOrder":20},
       {"code":"pt","pathPrefix":"pt","enabled":True,"publishReady":True,"nativeName":"Português","sortOrder":30},
       {"code":"ru","pathPrefix":"ru","enabled":True,"publishReady":True,"nativeName":"Русский","sortOrder":40},
       {"code":"tr","pathPrefix":"tr","enabled":True,"publishReady":True,"nativeName":"Türkçe","sortOrder":50},
    ]
    seen_codes=set()
    seen_prefix=set()
    locales=[]
    for row in sorted(all_rows,key=lambda x:(int(x.get("sortOrder",999)),str(x.get("code","")))):
        code=str(row.get("code","")).strip().lower()
        if PUBLISHED_CODES and code not in PUBLISHED_CODES:
            continue
        if not _CODE.fullmatch(code) or code in seen_codes:
            raise ValueError("Invalid or duplicate XUYI locale code: "+code)
        seen_codes.add(code)
        prefix=str(row.get("pathPrefix") or ("" if code==DEFAULT else code)).strip().strip("/").lower()
        if code==DEFAULT:
            if prefix:raise ValueError("Default English locale must use the root URL")
        elif not _PREFIX.fullmatch(prefix) or prefix in seen_prefix or prefix in _RESERVED:
            raise ValueError("Invalid or duplicate XUYI locale path prefix: "+prefix)
        if prefix:seen_prefix.add(prefix)
        if not(row.get("enabled") and row.get("publishReady")):continue
        locales.append({"code":code,"pathPrefix":prefix,
                        "nativeName":str(row.get("nativeName") or row.get("displayName") or code),
                        "sortOrder":int(row.get("sortOrder",999))})
    if not any(lang["code"]==DEFAULT for lang in locales):
        raise ValueError("Default English language must be enabled and publish-ready")
    # D1 sortOrder is an editorial menu ordering preference. Moving the
    # default language row below another locale must not abort the build.
    locales.sort(key=lambda lang:(lang["code"]!=DEFAULT,lang["sortOrder"],lang["code"]))
    if require_resources:
        for name,path in _RESOURCES.items():
            resources=json.loads((ROOT/path).read_text(encoding="utf-8"))
            for lang in locales:
                if lang["code"]==DEFAULT:continue
                entry=resources.get(lang["code"])
                if not isinstance(entry,dict) or not entry:
                    raise ValueError(f"XUYI locale {lang['code']} lacks reviewed {name} resource: {path}")
        baseline=json.loads((ROOT/_RESOURCES["header/footer"]).read_text(encoding="utf-8"))
        baseline_locale=next((lang["code"] for lang in locales
                              if lang["code"]!=DEFAULT and isinstance(baseline.get(lang["code"]),dict)),None)
        if baseline_locale:
            required=set(baseline[baseline_locale])
            for lang in locales:
                if lang["code"]==DEFAULT:continue
                missing=required-set(baseline[lang["code"]])
                if missing:
                    raise ValueError("XUYI locale "+lang["code"]+" is missing UI keys: "+", ".join(sorted(missing)[:7]))
    return locales

def public_routes(state):
    """Stable serialized client/API manifest, generated from actual built pages."""
    return [{"code":lang["code"],"pathPrefix":lang["pathPrefix"],
             "nativeName":lang["nativeName"]} for lang in approved_locales(state)]

def local_url(lang,route):
    if not(route.startswith("/") and route.endswith("/")):raise ValueError("Invalid canonical route")
    prefix=lang["pathPrefix"]
    return ORIGIN+("/"+prefix+route if prefix else route)

