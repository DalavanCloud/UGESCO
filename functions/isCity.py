# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

item = "Q239"  # Bruxelles


def isCity(item):
    """
    get the class(es) of a Wikidata item
    """
    query = {"query": """
    SELECT ?classe WHERE { 
    wd:%s wdt:P31/wdt:P279* ?classe . 

    }
    """ % (item)
    }

    url = "https://query.wikidata.org/sparql"

    r = requests.get(url, params=query)

    print(r.text)

    soup = BeautifulSoup(r.text, "lxml")

    result = [x.text.split("/")[-1] for x in soup.find_all("uri")]

    print(result)

    if "Q15284" in result:
        return True
    elif len(result) == 0:
        return "No information"
    else:
        return False


print(getClass(item))
