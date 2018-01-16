# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

array = ["Q32815", "Q34627"] #mosque and synagogue


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


print(getLCS(array))
