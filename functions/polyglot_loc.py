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
    result = []
    # Print the type of each entity
    try:
        for ents in text.entities:
            if ents.tag == "I-LOC":
                liste.append(' '.join(ents))
    except ValueError:
        return "language not identified"
    try:
        for i, el in enumerate(liste):
            el = el.replace(' - ', '-')
            if liste[i] not in liste[i + 1]:
                result.append(el)

    except IndexError:
        result.append(el)
    return list(set(result))


print(polyglot_loc(
    """nous sommes rentrés hier de Bruxelles après être passés par Paris."""))
