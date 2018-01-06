# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 11:52:22 2018

@author: ettor
"""

from polyglot.text import Text

def polyglot_loc(x):
    """extract a list of locations from the string X
    using polyglot NER. Remove duplicates and nested locs ('Mons - sur')"""

    text = Text(x)
    
    liste = []
    liste2 = []
    # Print the type of each entity
    for ents in text.entities:
        if ents.tag == "I-LOC":
            liste.append(' '.join(ents))
    try:
        for i, el in enumerate(liste):
            el = el.replace(' - ', '-')
            if liste[i] not in liste[i+1]:
                liste2.append(el)

    except IndexError:
        liste2.append(el)
    return list(set(liste2))
    
print(polyglot_loc("""Nous avions été à Montigny-sur-Sambre avec Charles Michel pour assister au Te Deum de la Basilique de Liège-sur-Aulnois."""))

