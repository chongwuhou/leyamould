"""Conditional BPA enquiry prompt, generated from approved homepage source HTML.

This is *not* a BPA-free certification. Only a known unchanged hero-note
element may receive the badge; editor-selected D1 content overrides it.
"""
from html import escape
from pathlib import Path
import json,re

_SOURCE={
"en":("Taizhou, China · Plastic drinkware · OEM/ODM inquiries","BPA-FREE?","Ask for material and test verification by model"),
"es":("Taizhou, China · Botellas de plástico · Consultas OEM/ODM","¿Sin BPA?","Solicite verificación del material y ensayos según el modelo"),
"pt":("Taizhou, China · Artigos para bebidas de plástico · Consultas de OEM/ODM","SEM BPA?","Peça verificação de material e ensaios por modelo"),
"ru":("Тайчжоу, Китай · Пластиковая посуда для питья · Запросы OEM/ODM","БЕЗ BPA?","Запросите документы на материал и испытания для модели"),
"tr":("Taizhou, Çin · Plastik içecek ürünleri · OEM/ODM talepleri","BPA İÇERMEZ Mİ?","Modele özel malzeme ve test doğrulaması isteyin")
}
def add_home_bpa_note(body,locale):
    if locale not in _SOURCE or 'class="home-bpa-verification"' in body:return body
    note,label,description=_SOURCE[locale]
    anchor='<p class="hero__note">'+escape(note,quote=True)+'</p>'
    if body.count(anchor)!=1:return body  # changed CMS hero or unsupported new locale
    marker=('<div class="home-bpa-verification">'
            '<span class="home-bpa-verification__icon" aria-hidden="true">?</span>'
            '<span><strong>'+escape(label)+'</strong><small>'+escape(description)+'</small></span></div>')
    return body.replace(anchor,anchor+marker,1)