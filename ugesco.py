# -*- coding: utf-8 -*-
import json
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


def getClass(item):
    """
    get the class(es) of a Wikidata item
    """
    query = {"query": """
    SELECT ?classe ?classeLabel WHERE { 
    wd:%s wdt:P279 ?classe . 

    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } 
    }
    """ % (item)
    }

    url = "https://query.wikidata.org/sparql"

    r = requests.get(url, params=query)

    # print(r.text)

    soup = BeautifulSoup(r.text, "lxml")

    return [x.text for x in soup.find_all("uri")]

def getLCS(array):
    """
    get the least common subsumer between the two
    first Wikidata items in a list
    """
    query = {"query": """
    SELECT ?classe ?classeLabel WHERE { 
    wd:%s wdt:P279* ?classe . 
    wd:%s wdt:P279* ?classe . 
    filter not exists { ?otherClass wdt:P279 ?classe ; ^wdt:P279* wd:%s, wd:%s . } 

    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } 
    }
    """ % (array[0], array[1], array[0], array[1])
    }

    url = "https://query.wikidata.org/sparql"

    r = requests.get(url, params=query)

    # print(r.text)

    soup = BeautifulSoup(r.text, "lxml")

    return [x.text for x in soup.find_all("literal")]




class MyEncoder(json.JSONEncoder):
    """
    classe destinée à éviter des erreurs d'encodage du genre
    "TypeError: Object of type 'int64' is not JSON serializable"
    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


def get_nested_rec(key, grp):
    """
    fonction destinée à transformer un csv en json
    suivant le schéma de Samnang
    """
    rec = dict(PrimaryId=key[0],
               FirstName=key[1],
               LastName=key[2],
               City=key[3])

    for field in ['CarName', 'DogName']:
        rec[field] = list(grp[field].unique())

    return rec
