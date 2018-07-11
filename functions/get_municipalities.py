# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 20:07:37 2018

@author: ettor
"""

import re
import pandas as pd
from unidecode import unidecode

geo = pd.read_csv(
    r"C:\Users\ettor\Documents\GitHub\BelgicaPress\communes_et_sections_geonames.csv", encoding="utf8")
lieux_be = set([str(name).strip().lower() for name in geo.alternate_name])


def get_municipalities(value, lieux):
    liste = []
    CHARS = "abcdefghijklmnopqrstuvwxyzéëèàäâçüûùABCDEFGHIJKLMNOPQRSTUVWXYZ- "
    valeurs = "".join(unidecode(c.lower().replace("-", " "))
                      for c in str(value) if c in CHARS).strip()
    valeurs = re.sub(r"\s+", " ", valeurs).split(' ')

    for i, tokens in enumerate(valeurs):
        try:
            if tokens in lieux:
                tokens = tokens
            if tokens + " " + valeurs[i + 1] in lieux:
                tokens = tokens + " " + valeurs[i + 1]
            if tokens + "-" + valeurs[i + 1] in lieux:
                tokens = tokens + "-" + valeurs[i + 1]
            if tokens + "-" + valeurs[i + 1] + "-" + valeurs[i + 2] in lieux:
                tokens = tokens + "-" + valeurs[i + 1] + "-" + valeurs[i + 2]
            if tokens + " " + valeurs[i + 1] + " " + valeurs[i + 2] in lieux:
                tokens = tokens + " " + valeurs[i + 1] + " " + valeurs[i + 2]
            if tokens + " " + valeurs[i + 1] + " " + valeurs[i + 2] + valeurs[i + 3]in lieux:
                tokens = tokens + " " + \
                    valeurs[i + 1] + " " + valeurs[i + 2] + + valeurs[i + 3]
            if tokens + " " + valeurs[i + 1] + " " + valeurs[i + 2] + valeurs[i + 3]in lieux:
                tokens = tokens + "-" + \
                    valeurs[i + 1] + "-" + valeurs[i + 2] + valeurs[i + 3]
        except IndexError:
            pass
        if tokens in lieux:
            liste.append(tokens)
        for i, tokens in enumerate(liste):
            try:
                if liste[i + 1] in liste[i]:
                    del liste[i + 1]
            except IndexError:
                pass

    liste = set(liste)
    return "||".join(liste)


text = "Maisons atteintes par les obus des forts (Dolhain et rue du Palais-Verviers) en mai 1940 -- -- [Photo Ciné A. Ruwet]"

print(get_municipalities(text, lieux_be))
