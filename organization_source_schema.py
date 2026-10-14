"""Verified organization entity facts shared by homepage and About schemas.

The sales contact point is the existing public contact page, not an invented
telephone or address. Never imply material certification or offer availability.
"""
ORIGIN="https://xuyibottles.com"

SUBJECTS=[
    "plastic drinkware",
    "reusable plastic water bottles",
    "plastic water bottle wholesale",
    "plastic sports water bottles",
    "kids plastic water bottles",
    "plastic shaker bottles",
    "large-capacity plastic water jugs",
    "OEM plastic water bottles",
    "ODM plastic bottle development",
    "custom logo printing on plastic drinkware",
]

def enrich_organization(node):
    """Add supported sales and subject facts without overwriting owner fields."""
    if not isinstance(node,dict) or node.get("@type")!="Organization":
        return node
    node=dict(node)
    # A future publisher may have supplied their own verified sales point.
    node.setdefault("contactPoint",{
        "@type":"ContactPoint",
        "contactType":"sales",
        "url":ORIGIN+"/contact/"
    })
    node.setdefault("knowsAbout",list(SUBJECTS))
    return node