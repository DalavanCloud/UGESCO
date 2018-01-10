# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 20:26:17 2018

@author: ettor
"""

import spotlight


def get_dbpediaspotlight(value, db_type):
    """use pyspotlight to annotate text. To use it, First lauch
    java -jar dbpedia-spotlight-0.7.1.jar fr  http://localhost:2222/rest
    in the folder D:\dbpdia_spotlight
    """
    types_filter = {
        'policy': "whitelist",
        'types': "DBpedia:{}".format(db_type),
        'coreferenceResolution': False}
    try:

        annotations = spotlight.annotate('http://localhost:2222/rest/annotate',
                                         value,
                                         confidence=0.2,
                                         support=20,
                                         filters=types_filter)
        liste = []
        for el in annotations:
            liste.append(el['URI'] + "||" + el['types'])
    except spotlight.SpotlightException:
        pass

    return ":::".join(liste)


print(get_dbpediaspotlight(
    "La famille Michel est originaire d'Hoegaarden (Flandre). Fils de Martine et de Louis Michel. Son père est ancien président du Mouvement réformateur (dont la présidence sera reprise par son fils, et deviendra député européen et ministre d'État.", "Place"))
