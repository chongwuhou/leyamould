"""G-series factory-model customizable polymer choices, source-rendered."""
from html import escape
import re
LOCALES={
 "en":("Custom plastic material options","Factory G-series models can be made to order in different plastic materials, including PP, PC, PETG, Tritan copolyester, PE and ABS when appropriate to the component and design. Please specify the body, lid, straw and seal separately. Custom material options are available subject to the final design, sample approval and intended destination-market testing; this list does not identify a standard stock resin or certify any finished bottle.","Request this G-series material configuration"),
 "es":("Opciones de materiales plásticos a medida","Los modelos de fábrica de la serie G permiten solicitar diferentes plásticos, como PP, PC, PETG, copoliéster Tritan, PE y ABS, según la pieza y el diseño. Indique por separado el material del cuerpo, la tapa, la pajita y las juntas. Las opciones requieren confirmar viabilidad, muestra y pruebas aplicables al mercado de destino; no describen necesariamente el material de serie ni una certificación.","Consultar los materiales de esta serie G"),
 "pt":("Opções de materiais plásticos personalizados","Os modelos de fábrica da série G permitem solicitar diferentes plásticos, incluindo PP, PC, PETG, copoliéster Tritan, PE e ABS, conforme a peça e o projeto. Informe separadamente os materiais do corpo, da tampa, do canudo e das vedações. A personalização depende da viabilidade, da amostra aprovada e dos testes aplicáveis ao mercado; esta lista não prova o material padrão nem a certificação.","Solicitar esta configuração da série G"),
 "ru":("Пластиковые материалы под заказ","Для заводских моделей серии G можно заказать различные пластики, в том числе PP, PC, PETG, сополиэфир Tritan, PE и ABS, если материал подходит для конкретной детали и конструкции. Отдельно уточните материал корпуса, крышки, трубочки и уплотнителей. Необходимы согласование конструкции, образца и проверки для целевого рынка; это не заявление о материале готового складского изделия или сертификации.","Запросить материалы для модели G"),
 "tr":("Özel plastik malzeme seçenekleri","G serisi fabrika modelleri için parçaya ve tasarıma uygun olmak koşuluyla PP, PC, PETG, Tritan kopolyester, PE ve ABS dahil farklı plastik malzemeler sipariş üzerine değerlendirilebilir. Gövde, kapak, pipet ve contaların malzemelerini ayrı belirtin. Uygunluk, onaylı numune ve hedef pazar testleri gereklidir; bu liste stok ürünün kesin reçinesi veya sertifikasyonu anlamına gelmez.","G serisi malzeme seçeneklerini sorun")
}
def render_g_material_options(route,locale,existing_main=""):
    slug=route.strip("/").split("/")[-1]
    if not re.fullmatch(r"g-[0-9]{2,3}",slug):
        return ""
    if 'id="g-series-custom-material-options"' in existing_main:return ""
    title,copy,cta=LOCALES[locale]
    href="/"+("" if locale=="en" else locale+"/")+"contact/#inquiry"
    return ('<section class="section g-series-material-options" id="g-series-custom-material-options">'
      '<div class="shell"><h2>'+escape(title)+'</h2><p>'+escape(copy)+'</p>'
      '<a href="'+href+'">'+escape(cta)+' →</a></div></section>')
