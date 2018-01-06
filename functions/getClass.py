# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

item = "Q32815"


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

print(getClass(item))
