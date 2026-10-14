"""XUYI About: reviewed five-language source template, with D1 owner-edit guard."""
from pathlib import Path
from html import escape as esc
from functools import lru_cache
import json,hashlib,re

ROOT=Path(__file__).resolve().parent
ASSETS=(
 "/media/group/factory-bottle-packing.webp",
 "/media/group/factory-final-pack.webp",
 "/media/group/qa-color-box.webp",
 "/media/group/factory-shipment.webp",
)
LINKS=("/products/","/request-sample/","/contact/#inquiry")
PROCESS_LINKS=("/manufacturing/","/quality-control/")
BASELINES=json.loads((ROOT/"data/about-company-d1-baselines.json").read_text(encoding="utf8"))["locales"]

@lru_cache(maxsize=5)
def source(locale):
    if locale not in BASELINES:raise ValueError("Unsupported About locale: "+locale)
    return json.loads((ROOT/("data/about-company-"+locale+".json")).read_text(encoding="utf8"))

def digest(value):return hashlib.sha256(value.encode("utf8")).hexdigest()

def baseline_body(current,locale):
    """Respect any subsequent D1 CMS About edit, not only original source."""
    if locale not in BASELINES:return False  # Future locales stay D1-owned until reviewed translations exist.
    if 'id="xuyi-about-company"' in current:return False
    if digest(current)==BASELINES[locale]["body"]:return True
    # No D1 snapshot in a fresh local source build: the original shared
    # resource-page component is the editable template owner.
    return locale=="en" and '<h1>About XUYI: Plastic Drinkware Supply in Taizhou</h1>' in current

def safe_text(value):return esc(str(value),quote=True)
def paras(items):
    return "".join("<p>"+safe_text(p)+"</p>" for p in items)

def render(locale):
    data=source(locale)
    h='<div id="xuyi-about-company" class="xuyi-about-company" lang="'+locale+'">'
    h+='<section class="rs-hero xac-hero"><div class="shell"><nav class="rs-crumb" aria-label="Breadcrumb"><a href="'+("/" if locale=="en" else "/"+locale+"/")+'">Home</a><span>/</span><span>About XUYI</span></nav>'
    h+='<span class="eyebrow">'+safe_text(data["eyebrow"])+'</span>'
    h+='<h1>'+safe_text(data["h1"])+'</h1>'
    h+='<div class="xac-intro">'+paras(data["lead"])+'</div>'
    h+='<div class="xac-hero-actions">'
    for label,href in zip(data["links"],LINKS):
        loc_href=href if locale=="en" else "/"+locale+href
        h+='<a class="button" href="'+safe_text(loc_href)+'">'+safe_text(label)+' →</a>'
    h+='</div></div></section>'
    h+='<section class="rs-section"><div class="shell xac-glance"><div><span class="eyebrow">XUYI BOTTLES</span><h2>'+safe_text(data["glanceTitle"])+'</h2></div><dl>'
    for name,value in data["glance"]:
        h+='<div><dt>'+safe_text(name)+'</dt><dd>'+safe_text(value)+'</dd></div>'
    h+='</dl></div></section>'
    h+='<section class="rs-section rs-section--soft"><div class="shell xac-prose"><h2>'+safe_text(data["taizhouTitle"])+'</h2><p>'+safe_text(data["taizhou"])+'</p></div></section>'
    h+='<section class="rs-section"><div class="shell"><div class="xac-section-lead"><h2>'+safe_text(data["workflowTitle"])+'</h2><p>'+safe_text(data["workflowIntro"])+'</p></div><ol class="xac-workflow">'
    for index,(heading,detail) in enumerate(data["workflow"],1):
        h+='<li><span>'+str(index).zfill(2)+'</span><div><h3>'+safe_text(heading)+'</h3><p>'+safe_text(detail)+'</p></div></li>'
    h+='</ol><div class="xac-support-links">'
    for label,href in zip(data["workflowLinks"],PROCESS_LINKS):
        h+='<a href="'+(href if locale=="en" else "/"+locale+href)+'">'+safe_text(label)+' →</a>'
    h+='</div></div></section>'
    h+='<section class="rs-section rs-section--soft"><div class="shell xac-prose"><h2>'+safe_text(data["manufacturingTitle"])+'</h2>'+paras(data["manufacturing"])+'</div></section>'
    h+='<section class="rs-section"><div class="shell"><div class="xac-section-lead"><h2>'+safe_text(data["qualityTitle"])+'</h2><p>'+safe_text(data["qualityLead"])+'</p></div><div class="xac-quality">'
    for heading,detail in data["quality"]:
        h+='<article><h3>'+safe_text(heading)+'</h3><p>'+safe_text(detail)+'</p></article>'
    h+='</div><p class="xac-quality-note">'+safe_text(data["qualityAfter"])+'</p></div></section>'
    h+='<section class="rs-section rs-section--dark"><div class="shell"><h2>'+safe_text(data["photoTitle"])+'</h2><div class="rs-about__gallery xac-gallery">'
    for index,url in enumerate(ASSETS):
        alt=data.get("photoAlts",[])[index] if locale!="en" else data["photos"][index]["alt"]
        caption=data.get("photoCaptions",[])[index] if locale!="en" else data["photos"][index]["caption"]
        h+='<figure><img src="'+url+'" loading="lazy" decoding="async" alt="'+safe_text(alt)+'"><figcaption>'+safe_text(caption)+'</figcaption></figure>'
    h+='</div></div></section>'
    h+='<section class="rs-section rs-section--soft xac-no-claims-section" id="what-you-wont-find-here"><div class="shell"><h2>'+safe_text(data["noClaimsTitle"])+'</h2><div class="xac-no-claims">'
    for heading,detail in data["noClaims"]:
        h+='<article><h3>'+safe_text(heading)+'</h3><p>'+safe_text(detail)+'</p></article>'
    h+='</div></div></section>'
    h+='<section class="rs-footer-cta xac-final"><div class="shell"><h2>'+safe_text(data["endTitle"])+'</h2><p>'+safe_text(data["endCopy"])+'</p><div class="xac-final-links">'
    for label,href in zip(data["links"],LINKS):
        h+='<a class="button" href="'+(href if locale=="en" else "/"+locale+href)+'">'+safe_text(label)+' →</a>'
    return h+'</div></div></section></div>'

def apply_body(current,locale):
    return render(locale) if baseline_body(current,locale) else current

def metadata_unchanged(old_title,old_description,locale):
    return locale in BASELINES and digest(str(old_title)+"\n"+str(old_description))==BASELINES[locale]["meta"]

def replace_head_if_original(content,locale,old_title,old_description):
    if not metadata_unchanged(old_title,old_description,locale):return content
    d=source(locale)
    content=re.sub(r"<title>[^<]*</title>",lambda m:"<title>"+safe_text(d["title"])+"</title>",content,count=1)
    content=re.sub(r'<meta name="description" content="[^"]*">',lambda m:'<meta name="description" content="'+safe_text(d["description"])+'">',content,count=1)
    content=re.sub(r'<meta property="og:title" content="[^"]*">',lambda m:'<meta property="og:title" content="'+safe_text(d["title"])+'">',content,count=1)
    content=re.sub(r'<meta property="og:description" content="[^"]*">',lambda m:'<meta property="og:description" content="'+safe_text(d["description"])+'">',content,count=1)
    return content