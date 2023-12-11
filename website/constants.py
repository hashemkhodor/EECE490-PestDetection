# pesticides : dictionary( pesticide name : dictionary of headers)
# headers : list
# description: dictionary ( header : Text )
# NiceName : dictionary (header : nicename )

headers = [
    "Pesticide",
    "price_5acres",
    "evmt_score_animals",
    "evmt_score_pollution",
    "effectiveness_score",
    "human_health",
    "number_targeted_pests",
    # "Sources",
]

desc = [
    "Name of active ingredient",
    """Number of ounces of product necessary to treat 5 acres of land. For pesticides meant to be diluted, with no specific amount of gallons of solution per acre given, the amount is taken to be 20 gallons per acre (so 100 gallons in total).""",
    """Impact on native or endangered species.""",
    """Volatileness and effect on water polution.""",
    """Overall effectiveness against target pest. """,
    """Effect and danger on human health (direct exposure).""",
    "Number of targeted pests normalized ",
    # """UC IPM: University of California Integrated Pest Management program
    # PPDB: University of Hertfordshire Pesticide Properties DataBase
    # BPDB: University of Hertfordshire BioPesticides DataBase""",
]

niceNames = [
    "Pesticide",
    "Cost to treat 5 acres of land",
    "Impact on native species",
    "Impact on environment",
    "Effectiveness",
    "Impact on human health",
    "Versatility",
    # "Sources",
]

Sources1 = [
    "evmt_score_animals",
    "evmt_score_pollution",
    "human_health",
]
Sources2 = ["effectiveness_score"]

NiceName = dict(zip(headers, niceNames))
description = dict(zip(headers, desc))
