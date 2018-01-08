# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 17:08:34 2018

@author: ettor
"""
import re
import pandas as pd
from unidecode import unidecode

geo = pd.read_table(r"data\streets_and_POI.tsv")
streets = set([unidecode(str(name).strip().lower().replace('-', ' ')) for name in geo.lowercase])


def get_streets(text, streets):
    CHARS = "abcdefghijklmnopqrstuvwxyzéëèàäâçüûùABCDEFGHIJKLMNOPQRSTUVWXYZ-' "
    valeurs = "".join(unidecode(c.lower().replace("' ", "'").replace('-', ' ')) for c in str(text) if c in CHARS).strip()
    valeurs = re.sub(r"\s+", " ", valeurs)
    liste = []


    for tokens in streets:
        if tokens in valeurs:
            liste.append(tokens)
    if len(liste) > 1 and min(liste, key=len) in max(liste, key=len):
        liste.remove(min(liste, key=len))
        
    
    return "||".join(set(liste))
        
text = """Eglise de Zelzate."""
print(get_streets(text, streets))