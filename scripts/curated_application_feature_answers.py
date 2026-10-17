#!/usr/bin/env python3
"""Meaningful scenario-specific buying answers for thin application/feature pages.

These are buying questions and verification criteria, not unverified product
claims. All five languages use reviewed text rather than automatic translation
at runtime. No photos, product database or structured product facts change.
"""
from html import escape
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent.parent
TOPIC_GRIDS=json.loads((ROOT/"data/topic-decision-grids-en.json").read_text(encoding="utf8"))
LOCALES=("en","es","pt","ru","tr")
EYEBROWS={
 "en":"MODEL SELECTION","es":"SELECCIÓN DE MODELOS",
 "pt":"SELEÇÃO DE MODELOS","ru":"ВЫБОР МОДЕЛИ","tr":"MODEL SEÇİMİ"
}
LABELS={
 "en":("Before choosing this bottle style","Use these questions to specify an actual model and a testable sample.","Discuss sample and quotation"),
 "es":("Antes de elegir este tipo de botella","Utilice estas preguntas para definir un modelo y evaluar una muestra.","Consultar muestra y cotización"),
 "pt":("Antes de escolher este tipo de garrafa","Use estas perguntas para definir um modelo e avaliar uma amostra.","Consultar amostra e cotação"),
 "ru":("Перед выбором бутылки","Эти вопросы помогут указать точную модель и проверить образец.","Обсудить образец и расчет"),
 "tr":("Bu şişe tipini seçmeden önce","Belirli bir modeli seçmek ve numuneyi değerlendirmek için bu soruları kullanın.","Numune ve teklif isteyin"),
}
# Two distinct practical checks per route. They describe what the buyer must
# request and verify, rather than asserting a particular SKU passed testing.
TOPICS={
 "applications/everyday-hydration":{
  "en":["Compare filled bottle dimensions and available capacity with the intended bag, desk or commute; catalog dimensions require sample confirmation.","Check how the chosen lid and seal can be removed and cleaned. Request instructions for the exact model rather than assuming dishwasher compatibility."],
  "es":["Compare las dimensiones y la capacidad con el bolso, escritorio o trayecto previsto; confirme las medidas con una muestra.","Revise cómo se desmontan y limpian la tapa y la junta. Solicite instrucciones del modelo; no suponga que admite lavavajillas."],
  "pt":["Compare dimensões e capacidade com a mala, mesa ou deslocação; confirme as medidas com uma amostra.","Verifique como retirar e limpar a tampa e vedação. Solicite instruções para o modelo; não presuma compatibilidade com máquina de lavar."],
  "ru":["Сравните размер наполненной бутылки и объем с сумкой, рабочим местом и маршрутом; размеры из каталога уточните по образцу.","Проверьте, как снимаются и очищаются крышка и уплотнение. Не предполагайте пригодность для посудомоечной машины без инструкции."],
  "tr":["Dolu şişenin boyutlarını ve kapasitesini çanta, masa ve günlük kullanım ile karşılaştırın; katalog ölçülerini numuneyle doğrulayın.","Kapak ve contanın nasıl çıkarılıp temizlendiğini kontrol edin. Model belgelerini görmeden bulaşık makinesine uygun olduğunu varsaymayın."]
 },
 "applications/gym-sports":{
  "en":["Confirm whether the exact model includes the drinking spout, mixing accessory and carrying feature shown in the picture; visual examples do not prove package contents.","Evaluate the chosen cap's sealing and one-handed use with a physical sample in the intended gym or sports scenario before calling it leakproof."],
  "es":["Confirme si el modelo incluye boquilla, accesorio de mezcla y asa mostrados; una foto no garantiza el contenido del paquete.","Evalúe el cierre y la apertura con una mano utilizando una muestra en el uso deportivo previsto antes de afirmar que no hay fugas."],
  "pt":["Confirme se o modelo inclui bico, misturador e alça mostrados; a fotografia não comprova os componentes fornecidos.","Avalie a vedação e abertura com uma mão numa amostra para o uso esportivo pretendido antes de afirmar que não vaza."],
  "ru":["Уточните, входят ли показанные носик, смешивающая вставка и ручка в выбранную комплектацию; фото этого не доказывает.","Проверьте герметичность крышки и открывание одной рукой на реальном образце для предполагаемого спортивного применения."],
  "tr":["Fotoğraftaki içme ağzı, karıştırıcı parça ve taşıma bölümünün seçilen modelde bulunduğunu doğrulayın; görseller paket içeriği garantisi değildir.","Sızdırmazlık veya tek elle açma iddiasından önce kapağı gerçek numunede kullanım senaryosuna göre test edin."]
 },
 "applications/kids-school":{
  "en":["Define the intended age range and destination market before choosing straw, handle and removable parts; ask for component-specific food-contact evidence and suitability assessment.","Check cleaning access, strap attachment and the complete closure on the finished sample. Do not infer child safety or leakproof performance from pictures."],
  "es":["Defina la edad prevista y el mercado antes de elegir pajita, asa y piezas desmontables; solicite evidencia de contacto alimentario para cada componente.","Compruebe acceso para limpieza, fijación de correa y cierre en la muestra final. Las fotos no demuestran seguridad infantil ni ausencia de fugas."],
  "pt":["Defina a faixa etária e o mercado antes de escolher palhinha, alça e peças removíveis; solicite documentação de contacto alimentar por componente.","Verifique a limpeza, a fixação da alça e o fecho numa amostra final. Fotografias não comprovam segurança infantil nem estanqueidade."],
  "ru":["Укажите возрастную группу и рынок назначения до выбора трубочки, ручки и съемных деталей; запросите документы на материалы каждого компонента.","Проверьте доступность очистки, крепление ремешка и крышку на готовом образце. Фото не подтверждают безопасность для детей или герметичность."],
  "tr":["Pipet, sap ve sökülebilir parçaları seçmeden önce yaş grubunu ve hedef pazarı belirtin; her bileşenin gıda temas belgelerini isteyin.","Numunede temizlik erişimini, askı bağlantısını ve kapağı kontrol edin. Fotoğraflar çocuk güvenliği veya sızdırmazlık kanıtı değildir."]
 },
 "applications/outdoor-travel":{
  "en":["Compare the weight and balance of the filled candidate bottle with its handle or strap. Request exact dimensions and a physical sample for transport checks.","Confirm temperature limits, sealing and cleaning suitability for the selected resin and complete lid assembly; do not infer hot-water or drop resistance from a lifestyle image."],
  "es":["Compare peso y equilibrio de la botella llena con su asa o correa. Solicite dimensiones y muestra para evaluar el transporte.","Confirme límites de temperatura, cierre y limpieza de la resina y tapa elegidas; una imagen no demuestra resistencia al calor ni a caídas."],
  "pt":["Compare peso e equilíbrio da garrafa cheia com a alça ou correia. Solicite dimensões e amostra para verificar o transporte.","Confirme limites de temperatura, vedação e limpeza da resina e tampa escolhidas; uma foto não demonstra resistência ao calor ou quedas."],
  "ru":["Оцените вес и равновесие наполненной бутылки с ручкой или ремнем. Запросите размеры и образец для транспортной проверки.","Уточните температурные ограничения, герметичность и очистку выбранного материала и крышки; фото не подтверждает стойкость к нагреву или падениям."],
  "tr":["Dolu şişenin sap veya askıyla ağırlık ve dengesini değerlendirin. Taşıma için gerçek ölçüleri ve numuneyi isteyin.","Malzeme ve kapak takımının sıcaklık sınırlarını, sızdırmazlığını ve temizliğini doğrulayın; fotoğraftan sıcak suya ya da düşmeye dayanıklılık sonucu çıkarmayın."]
 },
 "applications/promotional-gifts":{
  "en":["Compare printable area, final logo artwork and color sample for the chosen SKU. Request a decorated prototype before committing to a campaign quantity.","Confirm individual packaging, carton count, destination labeling and delivery deadline in a written quotation; custom branding and inventory are model dependent."],
  "es":["Revise el área de impresión, archivo del logotipo y muestra de color del modelo. Pida un prototipo decorado antes del pedido promocional.","Confirme embalaje individual, cantidad por caja, etiquetado y plazo por escrito; personalización y existencias dependen del modelo."],
  "pt":["Compare área de impressão, arte final do logótipo e amostra de cor do modelo. Peça protótipo decorado antes de confirmar a campanha.","Confirme embalagem individual, quantidades por caixa, rotulagem e prazo por escrito; personalização e estoque dependem do modelo."],
  "ru":["Согласуйте поле печати, макет логотипа и цветовой образец выбранной модели. Закажите декорированный образец до утверждения рекламного тиража.","Письменно уточните индивидуальную упаковку, количество в коробке, маркировку и срок поставки; оформление и наличие зависят от модели."],
  "tr":["Seçilen modelin baskı alanını, logo tasarımını ve renk numunesini karşılaştırın. Kampanya adedini onaylamadan önce baskılı numune isteyin.","Tekli ambalajı, koli adedini, hedef pazar etiketini ve teslim süresini yazılı doğrulayın; baskı ve stok modele bağlıdır."]
 },
 "features/carry-handle":{
  "en":["Verify that the pictured handle, strap or loop is included with the exact variant rather than being an optional accessory.","Test grip comfort and handle attachment when the bottle is filled to its intended capacity. Do not assume a load rating without supplier evidence."],
  "es":["Verifique que el asa, correa o aro de la foto pertenece a la variante exacta y no es un accesorio opcional.","Evalúe comodidad y fijación del asa con la botella llena. No presuponga resistencia de carga sin pruebas del proveedor."],
  "pt":["Confirme que a alça, correia ou anel mostrado pertence à variante exata e não é um acessório opcional.","Teste conforto e fixação com a garrafa cheia. Não suponha capacidade de carga sem evidência do fornecedor."],
  "ru":["Уточните, входит ли изображенная ручка, ремень или петля в данную комплектацию, или это дополнительный аксессуар.","Проверьте удобство захвата и крепление ручки у наполненной бутылки. Не заявляйте допустимую нагрузку без подтверждения."],
  "tr":["Görseldeki sap, askı veya halkanın seçilen varyanta dahil olup olmadığını doğrulayın; isteğe bağlı aksesuar olabilir.","Şişe doluyken tutuş rahatlığını ve bağlantıyı test edin. Tedarikçi kanıtı olmadan taşıma yükü iddia etmeyin."]
 },
 "features/flip-top":{
  "en":["Compare hinge, lock and drinking opening on the actual lid sample; similar-looking flip tops can use different seals and components.","Request cleaning and leak-testing instructions for the specific cap assembly. Do not describe a photographed lid as leakproof without testing."],
  "es":["Compare bisagra, cierre y boquilla en una muestra real; tapas similares pueden tener juntas distintas.","Solicite instrucciones de limpieza y pruebas de fugas para esa tapa. No declare que una tapa no gotea solo por la foto."],
  "pt":["Compare dobradiça, trava e abertura na tampa real; modelos parecidos podem ter vedações diferentes.","Solicite instruções de limpeza e teste de vazamento para a tampa exata. Uma foto não prova vedação."],
  "ru":["Сравните шарнир, замок и питьевое отверстие на образце крышки; внешне похожие модели могут иметь разные уплотнения.","Запросите инструкции по очистке и проверке протечек для конкретной крышки. Фото не доказывает герметичность."],
  "tr":["Gerçek numunede menteşe, kilit ve içme ağzını karşılaştırın; benzer görünümlü kapakların contaları farklı olabilir.","Seçilen kapak için temizlik ve sızıntı testi talimatlarını isteyin. Fotoğrafı sızdırmazlık kanıtı olarak kullanmayın."]
 },
 "features/straw-lid":{
  "en":["Ask whether the straw, mouthpiece and replacement seal are included and which parts can be removed for cleaning on the exact variant.","For children or school use, confirm target-age suitability, destination-market documentation and the completed assembly, not just the plastic resin name."],
  "es":["Pregunte si incluye pajita, boquilla y junta de repuesto, y qué piezas pueden retirarse para limpiar.","Para niños, confirme edad prevista, documentos del mercado y conjunto final; no basta con el nombre de la resina."],
  "pt":["Confirme se palhinha, bocal e vedação estão incluídos e quais peças podem ser removidas para limpeza.","Para crianças, verifique faixa etária, documentação do mercado e montagem completa, não apenas o nome da resina."],
  "ru":["Уточните, входят ли трубочка, питьевой наконечник и уплотнение в набор, и какие детали снимаются для мытья.","Для детей и школы проверьте возраст, документы рынка назначения и готовую конструкцию, а не только тип пластика."],
  "tr":["Pipet, ağızlık ve contanın dahil olduğunu, hangi parçaların temizlik için çıkarılabildiğini sorun.","Çocuk veya okul kullanımında yalnızca reçineye değil, yaş uygunluğuna, pazar belgelerine ve tamamlanmış ürüne bakın."]
 },
 "features/large-capacity":{
  "en":["Check whether the stated volume refers to the exact variant and compare filled handling, base stability and lid access on a sample.","Larger bottle dimensions change carton volume and freight costs; confirm actual carton size and quantities before comparing supplier quotations."],
  "es":["Verifique que el volumen anunciado corresponde a la variante y evalúe manejo, base y tapa con una muestra llena.","Las dimensiones grandes afectan embalaje y transporte; confirme medidas y unidades por caja antes de comparar ofertas."],
  "pt":["Confirme que a capacidade se refere à variante e avalie manuseio, base e tampa com uma amostra cheia.","Dimensões maiores afetam caixas e frete; confirme medidas e quantidades antes de comparar orçamentos."],
  "ru":["Уточните объем конкретного варианта, оцените устойчивость основания, ручку и крышку наполненного образца.","Большие размеры влияют на объем коробки и фрахт; проверьте габариты и число штук до сравнения предложений."],
  "tr":["Belirtilen hacmin tam olarak seçilen varyanta ait olduğunu doğrulayın; dolu numunede tutuş, taban ve kapağı inceleyin.","Büyük boyutlar koli hacmini ve nakliyeyi etkiler; teklifleri karşılaştırmadan önce koli ölçüsü ve adedini doğrulayın."]
 },
 "features/gradient-colors":{
  "en":["Approve the color transition against a physical molded sample, not an edited product photograph. Check each requested color reference and production method.","Confirm logo legibility and print placement on both light and dark areas. Keep the approved sample or color master for batch comparison."],
  "es":["Apruebe el degradado con una muestra física, no solo con una foto editada. Verifique referencias de color y proceso de fabricación.","Compruebe legibilidad y posición del logotipo en zonas claras y oscuras. Conserve la muestra aprobada para comparar lotes."],
  "pt":["Aprove o degradê com amostra física, não apenas fotografia editada. Confira referências de cor e processo de produção.","Verifique legibilidade e posição do logótipo nas áreas claras e escuras. Guarde a amostra aprovada para comparar lotes."],
  "ru":["Утвердите градиент по физическому образцу, а не обработанной фотографии; согласуйте эталоны цветов и технологию.","Проверьте читаемость логотипа на светлых и темных участках. Сохраните утвержденный образец для сравнения партий."],
  "tr":["Degrade renk geçişini düzenlenmiş fotoğrafa değil fiziksel numuneye göre onaylayın; renk referanslarını ve yöntemi netleştirin.","Logonun açık ve koyu alanlarda okunabilirliğini ve konumunu doğrulayın. Parti karşılaştırması için onaylı numuneyi saklayın."]
 },
}

def render_topic_grid(route, lang):
    """English source-authored decision grid; never machine-translate the prose."""
    if lang!="en":
        return ""
    data=TOPIC_GRIDS["topics"].get(route)
    if not data:
        return ""
    rows=data["rows"]
    if len(rows)<4 or any(len(item)!=3 for item in rows):
        raise ValueError("Invalid reviewed topic decision grid: "+route)
    out='<div class="topic-decision-grid"><h3>'+escape(data["title"])+'</h3><p>'+escape(data["intro"])+'</p>'
    out+='<div class="topic-decision-grid__scroll"><table><thead><tr><th scope="col">Scenario</th><th scope="col">Buying consideration</th><th scope="col">Confirm with the selected model</th></tr></thead><tbody>'
    for row in rows:
        out+='<tr><th scope="row">'+escape(row[0])+'</th><td>'+escape(row[1])+'</td><td>'+escape(row[2])+'</td></tr>'
    label,url=data["link"]
    if not url.startswith("/") or url.startswith("//") or any(c in url for c in ('<','>','"',"'",' ')):
        raise ValueError("Invalid buyer link: "+route)
    return out+'</tbody></table></div><p><a href="'+escape(url)+'">'+escape(label)+' →</a></p></div>'

def render_buyer_evidence(route, lang, existing_main=""):
    """Shared rendering component, called BEFORE final HTML is generated.

    D1 main body is authoritative. If the administrator already wrote this
    module, never replace it; a newly approved locale can be added to TOPICS.
    """
    route=route.strip("/")
    if route not in TOPICS or 'id="buyer-evidence-checks"' in existing_main:
        return ""
    if lang not in LOCALES:
        return ""
    answers=TOPICS[route].get(lang)
    if not answers or len(answers)!=2 or any(len(a)<55 for a in answers):
        raise ValueError("Incomplete reviewed buyer guidance: "+route+"/"+lang)
    title,intro,cta=LABELS[lang]
    url="/"+("" if lang=="en" else lang+"/")+"contact/#inquiry"
    return (
        '<section class="section buyer-evidence-checks" id="buyer-evidence-checks">'
        '<div class="shell"><div class="section__head"><div>'
        '<span class="eyebrow">'+escape(EYEBROWS[lang])+'</span>'
        '<h2 class="section__title">'+escape(title)+'</h2>'
        '<p>'+escape(intro)+'</p></div></div>'
        '<ol class="buyer-evidence-checks__items"><li>'+escape(answers[0])+
        '</li><li>'+escape(answers[1])+'</li></ol>'
        +render_topic_grid(route,lang)+
        '<a href="'+url+'" class="buyer-evidence-checks__cta">'+escape(cta)+' →</a>'
        '</div></section>'
    )

def apply(dist):
    dist=Path(dist)
    if len(TOPICS)!=10:
        raise ValueError("Expected precisely five applications and five features")
    count=0
    for route,content in TOPICS.items():
        if set(content)!=set(LOCALES):
            raise ValueError("Missing reviewed translation: "+route)
        for lang in LOCALES:
            prefix="" if lang=="en" else lang+"/"
            file=dist/prefix/route/"index.html"
            if not file.is_file():
                raise FileNotFoundError(file)
            source=file.read_text(encoding="utf8")
            # Preserve an existing source/CMS authored decision block and
            # avoid duplication when the build step runs more than once.
            existing=source.count('id="buyer-evidence-checks"')
            if source.count("</main>")!=1 or existing>1:
                raise ValueError("Unexpected original page: "+str(file))
            if existing==1:
                continue
            answers=content[lang]
            if len(answers)!=2 or min(map(len,answers))<55:
                raise ValueError("Missing specific buyer guidance: "+str(file))
            title,intro,cta=LABELS[lang]
            inquiry="/"+prefix+"contact/#inquiry"
            block=(
                '<section class="section buyer-evidence-checks" id="buyer-evidence-checks">'
                '<div class="shell"><div class="section__head"><div>'
                '<span class="eyebrow">'+escape(EYEBROWS[lang])+'</span>'
                '<h2 class="section__title">'+escape(title)+'</h2>'
                '<p>'+escape(intro)+'</p></div></div>'
                '<ol class="buyer-evidence-checks__items"><li>'+escape(answers[0])+
                '</li><li>'+escape(answers[1])+'</li></ol>'
                '<a href="'+inquiry+'" class="buyer-evidence-checks__cta">'+escape(cta)+' →</a>'
                '</div></section>'
            )
            file.write_text(source.replace("</main>",block+"</main>",1),encoding="utf8")
            count+=1
    print("XUYI_DISTINCT_BUYER_DECISION_CHECKS",count,"application and feature pages, five locales")
    return count

if __name__=="__main__":
    apply(ROOT/"dist")
