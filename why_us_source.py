"""Why Us buyer-decision content from versioned, five-language canonical copy.

Never replace a D1 editor's independently written Why Us body.
"""
from pathlib import Path
from html import escape as e
import json,hashlib
ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/"data/why-us-buyer-comparison-five-locales.json").read_text(encoding="utf8"))
LOCALE_BASELINES={
"en":"57ff080e3ed3889d0f3d82f9c84856f054fa09f6699694a6ddce81d32444a763",
"es":"c98c47583417b4d3cdefc0629ee39f068b47c1586e39a97d2624b34f1bdcf524",
"pt":"7b365bc8cdc23f8b2735f9b81931058bd128bf21a46bef8ba31adf0b6b8c0932",
"ru":"ab4ff47485e30f8048f299218a0e0413530174bd431f300319b685e657854b8d",
"tr":"a6164556de5ff1fd88f4b361b460165622da201559fe85468be20165ad00317b"
}
def section(locale):
 d=DATA[locale]
 t='<section class="rs-section xuyi-why-buyer-proof" id="supplier-comparison-evidence"><div class="shell">'
 t+='<h2>'+e(d["heading"])+'</h2>'
 for name,paragraphs in (("focus","focusTitle"),("workflow","workflowTitle"),("honesty","honestyTitle")):
  if name=="honesty":
   t+='<div class="xuyi-why-quality-check"><h3>'+e(d["matrixTitle"])+'</h3><p>'+e(d["matrixIntro"])+'</p><dl>'
   for heading,detail in d["matrix"]:
    t+='<div><dt>'+e(heading)+'</dt><dd>'+e(detail)+'</dd></div>'
   t+='</dl></div>'
  t+='<div class="xuyi-why-explainer"><h3>'+e(d[paragraphs])+'</h3>'
  for text in d[name]:t+='<p>'+e(text)+'</p>'
  t+='</div>'
 t+='<p class="xuyi-why-call-to-action">'+e(d["cta"])+'</p>'
 href=("/" if locale=="en" else "/"+locale+"/")
 t+='<p><a class="button" href="'+href+'request-sample/">'
 t+=e({"en":"Request the exact model sample","es":"Solicitar una muestra del modelo","pt":"Solicitar amostra do modelo","ru":"Запросить образец модели","tr":"Model numunesi isteyin"}[locale])+' →</a></p>'
 return t+'</div></section>'
def augment(body,locale,owner_override=False):
 if locale not in DATA:return body
 if 'id="supplier-comparison-evidence"' in body:return body
 actual=hashlib.sha256(body.encode("utf8")).hexdigest()
 # English is also D1-owned: add reviewed content only to the exact
 # known factory baseline. Any later CMS edit takes precedence.
 if owner_override and (locale!="en" or actual!=LOCALE_BASELINES["en"]):return body
 if locale!="en" and actual!=LOCALE_BASELINES[locale]:return body
 # A source section inserted immediately before the existing buyer contact
 # CTA, not a detached block or a replacement of D1 source body.
 marker='<section class="rs-footer-cta">'
 if marker not in body:return body
 return body.replace(marker,section(locale)+marker,1)
