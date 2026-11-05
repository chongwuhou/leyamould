#!/usr/bin/env python3
"""Verify the nine multilingual Blog translation records rendered from D1."""
import urllib.error, urllib.request

BASE="https://xuyibottles.com"
CASES=[
 ("/es/blog/bottle-factory-rfq-template/",[
  "wholesale buying guide →","how MOQ affects pricing →","request a sample →","OEM/ODM services →"],
  ["guía de compra mayorista →","cómo afecta el MOQ al precio →","solicitar una muestra →","servicios OEM/ODM →"]),



]
for slug in ("can-you-put-hot-water-in-plastic-water-bottle","why-does-reusable-water-bottle-smell-bad"):
    old=(
      ["Plastic Water Bottle Compliance: Food-Contact Documents Buyers Should Request","PC, Tritan, PP and PETG: Selecting Plastic Bottle Materials","BPA-Free Plastic Water Bottles: What Wholesale Buyers Must Verify"]
      if slug.startswith("can-you") else
      ["Leakproof Water Bottle Lids: A Buyer Testing Checklist","Replacement Water Bottle Lids: Bulk Spare-Parts Guide","Plastic Water Bottle Quality Control Checklist for Bulk Orders"]
    )
    for locale, translated in {
      "es": {
       "can-you": ["Cumplimiento de las botellas de agua de plástico: documentos de contacto alimentario que deben solicitar los compradores","PC, Tritan, PP y PETG: cómo seleccionar los materiales para botellas de plástico","Botellas de agua de plástico sin BPA: qué deben verificar los compradores mayoristas"],
       "why-": ["Tapas herméticas para botellas de agua: lista de pruebas para compradores","Tapas de repuesto para botellas de agua: guía de piezas de recambio al por mayor","Lista de control de calidad de botellas de agua de plástico para pedidos al por mayor"]},
      "pt": {
       "can-you": ["Conformidade de garrafas de água de plástico: documentos de contato com alimentos que os compradores devem solicitar","PC, Tritan, PP e PETG: como selecionar materiais para garrafas de plástico","Garrafas de água de plástico sem BPA: o que os compradores por atacado devem verificar"],
       "why-": ["Tampas à prova de vazamentos para garrafas de água: checklist de testes para compradores","Tampas de reposição para garrafas de água: guia de peças de reposição no atacado","Checklist de controle de qualidade de garrafas de água de plástico para pedidos em atacado"]},
      "ru": {
       "can-you": ["Соответствие пластиковых бутылок для воды требованиям: документы для контакта с пищевыми продуктами, которые следует запросить покупателям","PC, Tritan, PP и PETG: выбор материалов для пластиковых бутылок","Пластиковые бутылки для воды без BPA: что должны проверить оптовые покупатели"],
       "why-": ["Герметичные крышки для бутылок воды: список проверок для покупателей","Сменные крышки для бутылок воды: руководство по оптовым запасным деталям","Чек-лист контроля качества пластиковых бутылок для оптовых заказов"]},
      "tr": {
       "can-you": ["Plastik su şişelerinde uygunluk: alıcıların talep etmesi gereken gıda temas belgeleri","PC, Tritan, PP ve PETG: plastik şişe malzemelerini seçme rehberi","BPA içermeyen plastik su şişeleri: toptan alıcıların doğrulaması gerekenler"],
       "why-": ["Sızdırmaz su şişesi kapakları: alıcılar için test kontrol listesi","Yedek su şişesi kapakları: toplu yedek parça rehberi","Toplu siparişler için plastik su şişesi kalite kontrol listesi"]}
      }
    }.items():
        prefix="can-you" if slug.startswith("can-you") else "why-"
        CASES.append((f"/{locale}/blog/{slug}/",old,translated[locale][prefix]))

failed=[]
for path, old, translated in CASES:
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE+path,headers={"Cache-Control":"no-cache","User-Agent":"XUYI-blog-translation-repair-verify/1.0"}),timeout=30) as response:
            body=response.read().decode("utf-8","replace")
        if response.status != 200: failed.append((path,"status",response.status)); continue
    except Exception as error:
        failed.append((path,"request",type(error).__name__)); continue
    for phrase in old:
        if phrase in body: failed.append((path,"english",phrase))
    for phrase in translated:
        if phrase not in body: failed.append((path,"missing translation",phrase))
    if f'<html lang="{path.split("/",2)[1]}">' not in body: failed.append((path,"lang"))
if failed: raise SystemExit("XUYI BLOG TRANSLATION REPAIR LIVE AUDIT FAILED: "+repr(failed))
print("XUYI BLOG TRANSLATION REPAIR LIVE AUDIT PASSED",len(CASES),"localized routes")
