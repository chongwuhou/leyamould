"""Targeted locale meta-description repair for two D1 rows duplicated from the bicycle-shop guide.

Only replace a description when it is byte-for-byte the same (after whitespace
normalization) as the corresponding localized bicycle-shop description. Any
different CMS-owner edit remains authoritative.
"""
REFERENCE_ROUTE = "/blog/bicycle-shop-water-bottle-cage-fit-wholesale-buying/"

OVERRIDES = {
    ("/blog/construction-site-crew-water-bottles-bulk-procurement/", "es"):
        "Compra mayorista para cuadrillas de obra: muestras reales, tapa, higiene, reparto por turno, costes y entrega a cada obra.",
    ("/blog/workplace-refill-station-reusable-bottle-bulk-sourcing/", "es"):
        "Botellas reutilizables para empleados y puntos de recarga: compatibilidad con grifos, limpieza, asignación y coste de suministro.",
    ("/blog/construction-site-crew-water-bottles-bulk-procurement/", "pt"):
        "Compra em atacado para equipes de obras: amostra completa, tampa, higiene, distribuição por turno e custo entregue.",
    ("/blog/workplace-refill-station-reusable-bottle-bulk-sourcing/", "pt"):
        "Garrafas reutilizáveis para pontos de água de funcionários: encaixe na torneira, limpeza, distribuição e custo total.",
    ("/blog/construction-site-crew-water-bottles-bulk-procurement/", "ru"):
        "Оптовая закупка бутылок для строительных бригад: образцы, крышки, гигиена, распределение по сменам и доставка.",
    ("/blog/workplace-refill-station-reusable-bottle-bulk-sourcing/", "ru"):
        "Многоразовые бутылки для точек воды на работе: проверка крана, уход за бутылкой, выдача и затраты на поставку.",
    ("/blog/construction-site-crew-water-bottles-bulk-procurement/", "tr"):
        "Şantiye ekipleri için toptan su şişesi: gerçek numune, kapak, hijyen, vardiya dağıtımı ve teslim maliyeti.",
    ("/blog/workplace-refill-station-reusable-bottle-bulk-sourcing/", "tr"):
        "Çalışan su dolum noktaları için yeniden kullanılabilir şişeler: musluk uyumu, temizlik, stok ve toplam maliyet.",
}

def _normalize(value):
    return " ".join(value.split()) if isinstance(value, str) else ""

def apply(fields, route, locale, translations):
    """Repair only a confirmed duplicate of the localized bicycle-shop description."""
    replacement = OVERRIDES.get((route, locale))
    if replacement is None or not isinstance(fields, dict):
        return fields
    reference = translations.get((REFERENCE_ROUTE, locale)) or {}
    current_description = _normalize(fields.get("description"))
    reference_description = _normalize(reference.get("description"))
    if not current_description or current_description != reference_description:
        return fields
    return {**fields, "description": replacement}
