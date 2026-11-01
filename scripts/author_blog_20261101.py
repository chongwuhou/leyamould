#!/usr/bin/env python3
"""Authoritative editorial dataset for XUYI 2026-11-01 three distinct buyer guides.
Creates versioned source JSON consumed by D1/CMS release, never patches dist/HTML.
Each page's linked products are catalog REFERENCES, not claims about photo SKUs.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
D=ROOT/"data"
DAY="2026-11-01"
ISSUES=[
{
"slug":"homeware-store-reusable-water-bottles-wholesale",
"title":"How Should Homeware Stores Buy Reusable Water Bottles for Retail Shelves?",
"cover":"homeware-retail-drinkware-assortment-20261101.webp",
"group":"Homeware Retail Drinkware Buying",
"keyword":"reusable water bottles wholesale for homeware stores",
"desc":"A homeware retail buyer's B2B guide to reusable drinkware shelf assortments, sample approval, product labels, landed cost, replenishment and stock checks.",
"intro":"Homeware and lifestyle stores need a repeatable retail assortment, not just one photogenic bottle. This procurement guide covers customer segments, usable shelf space, sample approval, clear claims, color quantities, landed margin and replenishment. Its licensed shop photograph is an illustrative retail setting, not a XUYI customer or specific model.",
"related":["wholesale-water-bottle-distributor-assortment-planning","mixed-color-size-water-bottle-wholesale-order","wholesale-water-bottle-carton-label-3pl-retail-checklist"],
"skus":["2402","2501","lo-001"],
"heads":[
"Separate commuter, home and gift customers before choosing SKUs",
"Build a small tested assortment of body and closure formats",
"Test retail shelf spacing, labels and customer handling",
"Approve real samples and document materials and care",
"Control private-label artwork and color-by-color order quantities",
"Model landed gross margin and realistic slow-stock exposure",
"Receive shelf-ready cartons and plan data-led replenishment"],
"paras":[
"Start with actual sales or comparable store demand rather than an attractive mood board. Separate commuter bottles, everyday household use, impulse gifts and outdoor accessories because different buyers need different size cues, carrying options and price expectations. Record realistic shelf facings, target ticket prices and likely peak seasons. A small pilot in representative stores gives a better first buy than splitting a high-volume order evenly across every proposed color.",
"Ask for a short list of assembled bottle-and-lid combinations that match each retail use. Compare handling with the lid installed, mouth opening, height, base, ease of carrying and the actual materials documented for each assembly. A shape on a mood board is not an approved production configuration. Keep unfamiliar lid types and replacement-part options as samples until the retailer has tested cleaning and consumer instructions with actual units.",
"Mock up a real gondola, end cap or lifestyle display with the packed sample. Measure shelf height and depth, stability, label visibility, barcode location and room for customers to lift a bottle without knocking over adjacent units. Photograph each approved planogram with its exact variant code. A picture of shoppers evaluating bottles illustrates the retail decision, but neither verifies XUYI supplied the pictured merchandise nor proves a specific unit fits your store.",
"Review the complete physical sample: bottle body, lid, seal, removable straw if any, instructions, retail label and packaging. Ask the supplier for evidence appropriate to the exact material assembly and the destination market; avoid claiming any product is universally leakproof, dishwasher safe or certified without matching records. Have store staff test opening, reassembly and cleanability. Keep signed sample photographs and a revision number linked to the purchase order.",
"Keep blank retail stock separate from private-label designs. Confirm permission for each store brand, approved print position and color proof on a physical sample, not a monitor mock-up. Split the purchase order by SKU, cap configuration, color and artwork revision; ask which splits trigger separate minimum quantities or setup charges. Label every carton accordingly so merchandising staff can maintain the display without mixing versions.",
"Calculate price and margin from the delivered, saleable retail unit, not an isolated ex-factory quotation. Include decorated units, gift packaging, barcode work, master cartons, sampling, inspection, duties, freight and the cost of moving cartons to individual stores. Scenario-test slower sell-through of an unpopular color and a limited promotion. Set reorder points using observed weekly sales and verified lead times rather than optimistic seasonal demand.",
"At receipt, verify carton counts and cross-check retail labels, colors and closures against signed samples before items go on display. Test a sample from multiple cartons for cap presence, visible damage and barcode scanning; isolate any unexpected substitution. Keep a store-level count of received, displayed, sold, returned and damaged units. Feed return reasons and actual weekly sales into the next purchase order rather than adding untested colors automatically."
]},
{
"slug":"tennis-club-team-water-bottles-bulk-buying",
"title":"How Should Tennis Clubs Buy Reusable Bottles for Teams and Lessons in Bulk?",
"cover":"tennis-club-court-bottle-20261101.webp",
"group":"Tennis Club Team Bottle Procurement",
"keyword":"tennis club team water bottles bulk",
"desc":"A practical B2B tennis-club bottle procurement guide for coaching programs, court-side use, player labels, logo approvals, delivered costs and reorders.",
"intro":"Tennis-club purchasing mixes member welcome kits, junior lessons, league teams and tournaments. A reliable reusable-bottle order needs planned issue quantities, court-side handling checks, personalization controls and a clear replacement process. The licensed photograph shows a generic bottle beside a sports-court net, not an exact XUYI model, customer or performance test.",
"related":["soccer-academy-team-water-bottles-bulk-buying","cycling-race-branded-sports-water-bottles-bulk-procurement","summer-camp-reusable-water-bottles-group-order"],
"skus":["2306-transparent","2401","2505"],
"heads":[
"Forecast quantities by league roster, coach group and event",
"Check real court-side storage and safe player identification",
"Approve complete bottles using club training scenarios",
"Separate junior-team logos from member retail merchandise",
"Schedule distribution, cleaning and lost-bottle replacements",
"Compare landed team-kit costs, artwork and split deliveries",
"Inspect club deliveries and preserve an exact reorder specification"],
"paras":[
"Separate the season's fixed team roster, junior coaching intake, temporary tournament volunteers and optional pro-shop resale. Do not estimate demand from the entire club membership if many players already own bottles. List group issue dates, confirmed numbers, planned spare units and the person responsible for each batch. Identify whether family or adult programs use distinct artwork and whether each coach issues one bottle per player or manages spare stock.",
"Assess where bottles may safely stand during training: designated bench areas, equipment shelves or coach-managed carriers, not paths of play or hazardous court edges. Use a physical example to test stability, naming areas and how sweaty hands hold and open a closure. The illustrative court-side bottle is not a XUYI SKU test and does not establish universal court suitability. Ask staff to approve the storage and naming procedure before an order is placed.",
"Bring a fully assembled sample to a supervised lesson rather than judging only an online size graphic. Compare the cap, opening, body grip, removable pieces, carrying arrangement and cleaning instructions. Request evidence for the actual plastics, closures and intended destination-market compliance. Avoid unverified claims that the bottle is leakproof after being thrown into a kit bag or that it tolerates hot washing. Record the approval and the sample revision.",
"Keep team coaching bottles, one-off tournament gifts and items sold in the pro shop as separately approved variants. Obtain written rights for the tennis club emblem and permission for any sponsor logo. Do not personalize junior bottles with unnecessary personal information; use a simple agreed player-label method where permitted. Verify printed color and placement on a real bottle and keep a sign-off for each artwork revision and team color.",
"Name a kit coordinator for delivery to each coaching group and prevent unlabeled mixed cartons. Define whether bottles remain player-owned, who maintains spare caps and how the club handles lost or damaged units. Include an accessible cleaning and drying instruction based on the verified assembly rather than untested claims. A reusable bottle does not replace the venue's own responsibility to provide safe drinking water during organized activities.",
"Ask bidders for the same bottle configuration, number of caps, printing, individual or bulk packing and destination schedule. Include sample freight, setup, split-carton handling, import charges and contingency stock. Compare the full delivered cost per issued player kit, not only the lowest unit price. Tie production approval to the signed sample and print proof, and leave a realistic buffer before a tournament or seasonal registration deadline.",
"On arrival, count each carton against the club allocation plan and verify logos, colors, lids, seals and visible damage using several sample cartons. Quarantine mismatched items and agree the remedy before distributing kits. Retain the approved drawings, actual physical sample, supplier quote, shade reference and count by coaching group. Repeat orders should preserve this approved configuration unless the supplier submits a changed assembly for renewed review."
]},
{
"slug":"functional-training-gym-member-bottles-wholesale",
"title":"How Should Functional Training Gyms Source Bottles for Member Kits?",
"cover":"functional-training-gym-bottle-20261101.webp",
"group":"Functional Training Studio Member Kits",
"keyword":"functional training gym water bottles wholesale",
"desc":"A gym operator's wholesale guide to member drinkware kits, closure sampling, cleaning and storage policies, logo proofs, landed costs and reorders.",
"intro":"Functional training studios often bundle drinkware with new memberships, instructor programs, retail counters and fitness challenges. Buyers need a precise bottle brief that distinguishes regular water bottles from shaker configurations, separates personal issue from shared stock and protects an approved sample for reorders. The licensed fitness photograph is contextual, not an XUYI product test or member testimonial.",
"related":["fitness-studio-branded-shaker-bottle-member-kit-wholesale","pilates-studio-private-label-water-bottles-wholesale","shaker-bottle-wholesale"],
"skus":["2305","2209","lo-004"],
"heads":[
"Separate trial-member gifts, coach kits and retail demand",
"Decide whether standard water bottles or shakers are appropriate",
"Handle-test grip, cap and removable parts after a workout",
"Set hygiene rules for individually issued and shared stock",
"Approve studio artwork, colorways and clear product claims",
"Calculate complete kit cost and staggered onboarding orders",
"Inspect inbound stock and manage replacement-part reorders"],
"paras":[
"Estimate actual new joins by month, class-program instructors, special member challenges and the smaller portion willing to buy a separate retail bottle. Count any introductory membership kit only once and keep approved reserves for trial-to-member conversions. Avoid a single optimistic attendance multiplier. Segment by use and distribution location so front desk teams, coaches and storage rooms can accept properly marked cartons.",
"Functional training members may need simple water access, while a supplement brand partner may propose a different shaker-type closure. Treat these as different physical product choices, not interchangeable labels. Ask for assembled samples of each proposed format, and decide whether any mixer insert, straw or other part is actually approved and available. Never assign shaking, heat-resistance or leakproof capability from a generic product photo or unsupported material name.",
"Test hand grip and lid operation with a production-representative sample in normal studio situations, including an ordinary post-workout pause and placement on an approved shelf. Verify that a bottle does not obstruct gym-floor circulation; do not leave items where lifting or equipment movement creates hazards. Examine the threads, seal and removable components and request actual care guidance. Pictures of athletes drinking do not establish performance or a specific XUYI model.",
"Distinguish a bottle issued permanently to one person from any proposed shared amenity stock. Shared use needs an independently approved cleaning and handling procedure, and gyms must not assume a bottle itself sanitizes between users. Provide member-friendly care and drying instructions tied to the actual assembly. Keep personal names and gym membership records out of public carton labels. Request replacement lids only where compatibility has been established.",
"Obtain written permission for the studio logo and any sponsor mark. Review a physical printed proof for position, color and scuff appearance rather than treating a screen visualization as final authorization. Separate standard brand kits from limited event colorways and require a price and minimum quantity for each variant. Product copy should state only documented materials, capacities, care instructions and other claims for the particular assembly and target market.",
"Compare quotes for the complete member kit including closure, printing, packaging, samples, inspection, freight, taxes and front-desk distribution. Estimate uptake separately for trial offers, annual memberships, coaching staff and retail purchases; these groups may require different delivery dates. An untested limited color may be better piloted in a single location. Confirm production windows only after sample and artwork approvals and specify order-change consequences.",
"At goods-in, check models, assembled parts, logos, labels and quantities against the signed sample and studio allocation. Inspect units drawn from multiple cartons and hold aside missing seals, cracks and incorrect artwork before the reception team issues kits. Log which branch received each carton, what was handed out and why members requested replacements. Use this record to reorder only proven variants, with a separate approval whenever a lid or resin changes."
]}
]
EXTRA_EVIDENCE=[
"Create a documented demand sheet separating confirmed quantities from forecasts, owner approval and a small justified buffer. Recheck the allocation when the first pilot closes; a named buyer should sign off the quantities before deposits or artwork commitments.",
"Record a physical fit-and-use test including the assembled closure and all removable parts. Keep a dated sample photograph, the exact revision and a clear list of assumptions that were not yet proven by supplier documents.",
"Use real measurements, signed labels and multiple sample units instead of applying one generic fit claim to all variants. The shop or operator must approve how bottles are stored and handled in its actual environment.",
"Review care instructions and relevant documented material information for the whole configured bottle. Claims such as dishwasher safe, BPA free or guaranteed leakproof require evidence appropriate to the precise model and destination.",
"Obtain written art rights, inspect a printed sample and reconcile each carton label to an approved model and variant. Any changed logo, color, cap, packaging or supplier component needs a controlled purchase specification update.",
"Compare equivalent offers on total delivered usable-unit cost and explicitly identify freight responsibility, carton quantities, duty assumptions, sampling and make-good procedures. Document the date at which a revised quote must be approved.",
"At receipt, take a documented sample from several cartons, reconcile missing and damaged units and hold discrepancies separately. Preserve the approved sample, purchase order, receiving record and quality notes for a compliant repeat order."
]
LOCALE={
"es":{"name":["tiendas de hogar y estilo de vida","clubes de tenis y escuelas deportivas","gimnasios de entrenamiento funcional"],
"title":["Cómo comprar botellas reutilizables al por mayor para tiendas de hogar","Cómo comprar botellas reutilizables para equipos y clases de tenis","Cómo comprar botellas para kits de socios de gimnasios funcionales"],
"stage":["Planificar una demanda real por grupos","Elegir las variantes y probar las muestras completas","Verificar el uso y las dimensiones en el entorno","Documentar cuidado, materiales y responsabilidades","Aprobar diseños, colores y autorizaciones","Comparar costes entregados y fechas de reposición","Inspeccionar las cajas y conservar la ficha de pedido"],
"action":["Prepare una previsión por destinatario, ubicación y fecha; distinga pedidos confirmados de una reserva calculada y documente quién aprueba cantidades. No convierta una fotografía de referencia en prueba de una compra de un cliente real.","Pida muestras completas con cuerpo, tapa, junta y piezas desmontables. Compare configuraciones reales y registre límites de uso; el aspecto de una imagen de marketing no demuestra compatibilidad ni rendimiento del producto.","Pruebe el conjunto físico en el lugar de uso, con medidas, espacio disponible y manipulación cotidiana. Guarde resultados, responsables y revisión de muestra antes de decidir la cantidad comercial.","Defina cuidado, limpieza, entrega y sustitución de componentes. Solicite documentos correspondientes al material y al montaje reales; no anuncie resistencia térmica, hermeticidad ni certificados sin evidencia concreta.","Solicite permiso escrito para cada logotipo y compruebe la muestra impresa. Distinga colores, modelos, versiones de arte y cajas para impedir entregas equivocadas y costes no previstos.","Compare el coste total del artículo recibido con tapa, impresión, cajas, transporte, impuestos y distribución. Apruebe un plazo realista únicamente después de confirmar la muestra física y el arte final.","Cuente e inspeccione varias cajas contra la muestra firmada, separe defectos y conserve la ficha de producto, incidencias y cantidades entregadas. Use ventas o consumo reales para decidir la reposición."],
"intro":"Esta guía B2B explica cómo escoger cantidades, muestras y variantes verificables. Incluye revisión de material, tapas, embalajes, costes finales y reposición. La fotografía es un contexto ilustrativo autorizado, nunca un pedido real de XUYI ni una prueba de un modelo.",
"question":["¿La foto representa un modelo exacto de XUYI?","¿Podemos anunciar propiedades sin pruebas del conjunto?","¿Se pueden mezclar logotipos y colores sin costes?","¿Qué conviene conservar para repetir un pedido?"],
"answer":["No. Es una ilustración autorizada del contexto comercial; el comprador debe verificar la muestra física completa.","No. Exija documentación para cuerpo, tapa y material exactos y para el mercado de destino.","No necesariamente. Solicite mínimos por variante, permisos, costes de preparación y etiquetado de cajas.","Conserve muestra firmada, SKU, configuración, arte aprobado, condiciones de compra e incidencias de recepción."],
"head":["Fase","Prueba requerida","Aprobación"],"links":["Ver una guía de compra relacionada","Comparar los pasos de aprobación del proveedor"]},
"pt":{"name":["lojas de artigos para casa e estilo de vida","clubes de tênis e programas de aulas","academias de treinamento funcional"],
"title":["Como comprar garrafas reutilizáveis no atacado para lojas de artigos domésticos","Como comprar garrafas reutilizáveis para equipes e aulas de tênis","Como comprar garrafas para kits de membros de academias funcionais"],
"stage":["Planejar a demanda por grupos reais","Selecionar variantes e aprovar amostras completas","Conferir o uso físico no ambiente previsto","Definir cuidados, materiais e responsabilidades","Aprovar logotipos, cores e versões","Comparar custo entregue e prazos de reposição","Inspecionar as caixas e manter o histórico"],
"action":["Monte uma previsão por destinatário, local e data, separando pedidos confirmados de reserva justificada. Registre o responsável pelas quantidades e não trate uma foto editorial como prova de pedido de cliente real.","Solicite amostra com corpo, tampa, vedação e peças removíveis. Compare configurações reais, registre as limitações e não use a aparência da foto para confirmar compatibilidade ou desempenho.","Teste dimensões, espaço, estabilidade e abertura com a unidade física no cenário previsto. Registre os resultados e a revisão aprovada, em vez de assumir que qualquer formato serve para todos os usuários.","Defina entrega, limpeza, secagem e substituição de componentes. Solicite documentos dos materiais e da montagem reais; não anuncie resistência ao calor ou vedação perfeita sem evidências específicas.","Obtenha autorização escrita de cada marca e aprove uma prova impressa em amostra física. Separe modelo, cor, tampa, arte e caixas para evitar variantes erradas ou taxas adicionais.","Compare o custo total por unidade utilizável, incluindo embalagem, impressão, amostras, frete, impostos e distribuição. Aprove datas somente após os testes e a revisão final do pedido.","Conte e inspecione unidades de várias caixas contra a amostra assinada, separe defeitos e registre o recebimento. Preserve as especificações e o consumo real para futuras recompras."],
"intro":"Este guia B2B orienta a definição de quantidades, amostras e variantes verificáveis. Inclui materiais, tampas, embalagens, custos entregues e reposição. A fotografia licenciada é contextual: não representa um pedido real da XUYI nem testes de um SKU específico.",
"question":["A foto mostra um modelo exato da XUYI?","Podemos divulgar características sem provas do conjunto?","É possível misturar marcas e cores sem custos?","Que registros guardar para recomprar?"],
"answer":["Não. É uma imagem editorial licenciada; o comprador deve conferir a amostra física completa.","Não. Exija documentação para o corpo, a tampa e o material do modelo e mercado de destino.","Não necessariamente. Confirme mínimos por variante, permissões, custos de preparação e caixas identificadas.","Guarde amostra aprovada, SKU, composição, arte, cotação, contagem e problemas de recebimento."],
"head":["Etapa","Evidência exigida","Aprovação"],"links":["Ler o guia de compra relacionado","Comparar a aprovação do fornecedor"]},
"ru":{"name":["магазинов товаров для дома","теннисных клубов и школ","залов функционального тренинга"],
"title":["Как закупать многоразовые бутылки оптом для магазинов товаров для дома","Как теннисному клубу закупать бутылки для команд и тренировок","Как спортзалам функционального тренинга закупать бутылки для новых участников"],
"stage":["Разделите спрос по реальным группам","Выберите варианты и проверьте полные образцы","Проверьте размеры и использование на месте","Уточните уход, материалы и ответственность","Утвердите логотипы, цвета и маркировку","Сравните полную цену доставки и сроки","Проверьте коробки и сохраните параметры заказа"],
"action":["Составьте расчет по получателям, месту и дате, отделив подтвержденный спрос от обоснованного резерва. Назначьте ответственного за количество и не считайте редакционное фото доказательством реального клиентского заказа.","Запросите полный образец с корпусом, крышкой, уплотнением и съемными деталями. Сравните реальные комплектации; по рекламной фотографии нельзя подтвердить совместимость или эксплуатационные свойства.","Испытайте реальные размеры, устойчивость и удобство открытия в предполагаемом месте применения. Запишите результаты и редакцию образца; нельзя считать одну форму подходящей всем без проверки.","Установите порядок выдачи, мойки, сушки и замены комплектующих. Запросите сведения о материале и конкретной сборке; не обещайте термостойкость или абсолютную герметичность без доказательств.","Получите письменное разрешение на каждый логотип и утвердите печать на физическом образце. Разделяйте артикулы, цвета, крышки, версии макетов и коробки для предотвращения ошибок и лишних сборов.","Сравнивайте полную цену пригодной к использованию единицы с упаковкой, печатью, образцами, перевозкой, налогами и распределением. Сроки подтверждайте только после согласования сборки и макета.","Проверяйте несколько коробок по подписанному образцу, изолируйте брак и фиксируйте поставку. Сохраните спецификацию, журнал приемки и фактический расход для повторных закупок."],
"intro":"Это руководство B2B помогает определить объем, образцы и проверяемые варианты товара, согласовать материалы и крышки, упаковку, цену поставки и повторный заказ. Лицензионное фото служит иллюстрацией ситуации, а не доказательством заказа или испытаний продукции XUYI.",
"question":["Показан ли на фото точный артикул XUYI?","Можно ли обещать свойства без документов?","Бесплатно ли смешивать цвета и логотипы?","Что хранить для повторного заказа?"],
"answer":["Нет, это лицензионная иллюстрация ситуации, а не подтверждение модели. Проверьте полный образец.","Нет. Нужны документы по корпусу, крышке, сборке и рынку назначения.","Не всегда. Уточните минимальный объем по варианту, права на логотип и стоимость настройки.","Сохраните образец, артикул, комплектность, утвержденный макет, условия и журнал приемки."],
"head":["Этап","Необходимые данные","Согласование"],"links":["Открыть связанную инструкцию","Сравнить этапы согласования"]},
"tr":{"name":["ev ürünleri ve yaşam tarzı mağazaları","tenis kulüpleri ve antrenman grupları","fonksiyonel antrenman salonları"],
"title":["Ev ürünleri mağazaları yeniden kullanılabilir şişeleri toptan nasıl almalı?","Tenis kulüpleri takım ve ders şişelerini toplu nasıl almalı?","Fonksiyonel antrenman salonları üye şişelerini toptan nasıl seçmeli?"],
"stage":["Gerçek alıcı gruplarına göre talebi planlayın","Modelleri karşılaştırıp eksiksiz numuneyi onaylayın","Gerçek kullanım alanında boyut ve tutuşu sınayın","Malzeme, bakım ve sorumlulukları yazın","Logo, renk ve baskı izinlerini onaylayın","Teslim edilmiş maliyeti ve terminleri karşılaştırın","Kolileri kontrol edip tekrar sipariş kaydı tutun"],
"action":["Alıcı, lokasyon ve teslim tarihine göre talep cetveli hazırlayın; kesin siparişleri makul yedekten ayırın. Miktarı onaylayacak kişiyi belirleyin ve editoryal bir fotoğrafı gerçek müşteri siparişinin kanıtı saymayın.","Gövde, kapak, conta ve çıkarılabilir parçaları içeren fiziksel numune isteyin. Farklı yapılandırmaları karşılaştırın; tanıtım fotoğrafından uyumluluk veya dayanım özelliği varsaymayın.","Fiziksel şişeyi gerçek ortamda ölçü, alan, denge ve kapak açma açısından deneyin. Sonuçları, onaylayan kişiyi ve numune revizyonunu kaydedin; tek ölçünün herkese uygun olduğunu söylemeyin.","Dağıtım, temizlik, kurutma ve parça değişimini belgelendirin. Gerçek malzeme ve kapak tertibatı için kanıt isteyin; belgesiz sıcaklık, sızdırmazlık veya sertifika iddiasında bulunmayın.","Her marka için yazılı izin alın ve baskıyı gerçek numune üzerinde inceleyin. Model, renk, kapak, sanat dosyası sürümü ve koli etiketlerini ayırarak yanlış teslimat ile ek maliyetleri önleyin.","Baskı, paketleme, numune, navlun, vergi ve dağıtım dahil teslim edilen kullanılabilir ürünün toplam maliyetini karşılaştırın. Numune ve nihai tasarım onaylanmadan kesin termin vaat etmeyin.","Birden çok koliden alınan ürünleri imzalı numuneyle karşılaştırın, hasarlı ürünleri ayırın ve teslimatı kaydedin. Aynı ürünün tekrarı için doğrulanmış teknik özellik ve kullanım miktarını saklayın."],
"intro":"Bu B2B rehberi sipariş miktarı, doğrulanmış numune, kapak ve malzeme belgeleri, koli planı, gerçek teslim maliyeti ve tekrar satın alma yönetimini anlatır. Lisanslı fotoğraf sadece kullanım bağlamıdır; XUYI müşterisi veya kesin ürün modeli göstermez.",
"question":["Fotoğraftaki ürün kesin XUYI modeli mi?","Belge olmadan ürün özelliği vaat edilebilir mi?","Farklı logo ve renkler ücretsiz birleştirilebilir mi?","Tekrar sipariş için hangi kayıtlar saklanmalı?"],
"answer":["Hayır. Fotoğraf lisanslı örnek sahnedir; tam fiziksel numune ayrıca doğrulanmalıdır.","Hayır. Ürün gövdesi, kapak, malzeme ve hedef pazar için uygun kanıt istenmelidir.","Her zaman değil. Varyant adetleri, logo izinleri, baskı ve ambalaj ücretlerini doğrulayın.","İmzalı numune, SKU, bileşenler, onaylı tasarım, teklif ve teslimat tutanağını saklayın."],
"head":["Aşama","Gerekli kanıt","Onay"],"links":["İlgili satın alma rehberini inceleyin","Tedarikçi onay adımlarını karşılaştırın"]}
}
def write_json(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def main():
 for i,item in enumerate(ISSUES,1):
  p=json.loads((D/f"blog-guides-20261031-{i}.json").read_text("utf8"))
  p.update({k:item[k] for k in ("slug","title","intro","group")})
  p["description"]=item["desc"]
  p["cover"]="/media/blog/"+item["cover"]
  p["primary_keyword"]=item["keyword"]
  p["secondary_keywords"]=[item["keyword"],item["group"].lower()+" supplier",item["keyword"]+" manufacturer",item["keyword"]+" OEM customization"]
  p["updated"]=DAY
  p["related"]=item["related"]
  p["sections"]=[{"heading":h,"paragraph":text+"\n\n"+EXTRA_EVIDENCE[j]} for j,(h,text) in enumerate(zip(item["heads"],item["paras"]))]
  p["checklist"]=[*["Confirm: "+x for x in item["heads"]], "Retain printed sample sign-off", "Reconcile carton allocation by variant", "Record reorder approval and lead-time evidence"]
  p["faqs"]=[
   {"question":"Is the cover photograph an exact XUYI SKU or buyer installation?","answer":"No. It is a commercially licensed illustrative scene; the physical XUYI product assembly must be approved separately."},
   {"question":"Can this category be advertised as leakproof, food-safe or dishwasher-safe without tests?","answer":"No. Obtain appropriate evidence for the exact bottle, cap, material and destination market before making a product claim."},
   {"question":"Does one bulk quote cover all logo and color combinations?","answer":"Not necessarily. Confirm permissions, variant-level minimum quantities, physical proofs, setup charges and carton labeling."},
   {"question":"What evidence should be retained before reordering?","answer":"Keep signed assembly samples, exact SKU, caps and seals, artwork version, quotes, carton records and receiving discrepancies."}
  ]
  for j,n in enumerate(p["product_notes"]):
   n["sku"]=item["skus"][j];n["section"]=(1,3,5)[j]
   for loc in ["en","es","pt","ru","tr"]:
    n["label"][loc]=(lambda x:{"en":"XUYI model ","es":"modelo XUYI ","pt":"modelo XUYI ","ru":"модель XUYI ","tr":"XUYI modeli "}[x]+item["skus"][j])(loc)
   n["text"]["en"]="Consider {product} only as a catalog reference at this decision stage; request its complete physical sample and verify the configuration rather than inferring it from the editorial photograph."
  p["inline_links"]=[["Read the practical related buying guide","/blog/"+item["related"][0]+"/"],["Compare documented buyer checks","/blog/"+item["related"][1]+"/"]]
  p["buyerDecisionTable"]={"title":item["group"]+" buyer approval matrix","intro":"Sign off each decision with actual physical samples, records and responsible people; never infer SKU performance from the contextual photograph.","head":["Stage","Required evidence","Buyer sign-off"],"rows":[[item["heads"][j],["Demand forecast and allocations","Signed complete physical sample","Actual fit and use notes","Assembly care and material evidence","Logo proof and variant quantities","Equivalent landed-cost quotation"][j],["Approve quantity","Approve assembled sample","Approve scenario","Approve procedure","Approve artwork","Approve commercial terms"][j]] for j in range(6)],"links":p["inline_links"]}
  assert all(len(section["paragraph"])>650 for section in p["sections"]),[(len(s["paragraph"]),s["heading"]) for s in p["sections"]]
  write_json(D/f"blog-guides-20261101-{i}.json",p)
  trans={}
  for lang,t in LOCALE.items():
   name=t["name"][i-1]
   scene={"es":["el surtido de una tienda de productos reutilizables","el uso de botellas junto a la red de tenis","el uso de una botella en un gimnasio"],
          "pt":["o sortimento de uma loja de garrafas reutilizáveis","o uso de garrafas junto à rede de tênis","o uso de garrafa numa academia"],
          "ru":["ассортимент многоразовых бутылок в магазине","использование бутылок у теннисной сетки","использование бутылки в спортзале"],
          "tr":["yeniden kullanılabilir şişelerin mağaza raflarını","tenis filesi yanındaki spor şişesini","spor salonunda şişe kullanan kişiyi"]}[lang][i-1]
   contextual={"es":"Para "+name+", el orden de cantidad, espacio, cierre, identidad y destino decide si una compra en volumen resulta útil.",
               "pt":"Para "+name+", quantidade, espaço, tampa, identidade e destino determinam se a compra em volume é adequada.",
               "ru":"Для "+name+" важны количество, хранение, крышки, маркировка и место выдачи при оптовом заказе.",
               "tr":name+" için adet, yerleşim, kapak, kimlik ve teslimat şekli toplu alımın başarısını belirler."}[lang]
   sections=[]
   for j,(heading,action) in enumerate(zip(t["stage"],t["action"])):
    para=contextual+" "+action+" "+{"es":"La imagen muestra "+scene+" y no identifica un pedido, una certificación ni un modelo XUYI. Registre cada decisión con pruebas verificables.","pt":"A imagem mostra "+scene+" como contexto, não um cliente nem produto XUYI. Registre a decisão com evidência verificável.","ru":"Фотография иллюстрирует "+scene+", а не заказ или подтвержденный артикул XUYI. Решения подтверждаются документами.","tr":"Fotoğraf "+scene+" gösteren bir bağlamdır; belirli bir XUYI siparişini veya testini kanıtlamaz. Kararları belgeleyin."}[lang]
    assert len(para)>230,(lang,i,j,len(para))
    sections.append([heading,para])
   trans[lang]={
    "title":t["title"][i-1],
    "description":t["intro"]+" "+contextual,
    "intro":contextual+" "+t["intro"]+" "+t["action"][0],
    "sections":sections,
    "checklist":[*t["stage"],t["action"][0],t["action"][4],t["action"][6]],
    "faqs":list(zip(t["question"],t["answer"])),
    "matrix":{"title":t["title"][i-1]+" – B2B","intro":contextual,"head":t["head"],"rows":[[t["stage"][j],t["action"][j][:155],t["head"][2]] for j in range(6)],"links":t["links"]},
    "inline":t["links"]
   }
  write_json(D/f"blog-localized-copy-20261101-{i}.json",trans)
  print("AUTHORED",p["slug"],[len(s["paragraph"]) for s in p["sections"]])
if __name__=="__main__":main()