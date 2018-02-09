# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup


def cvClassToQid(array):
    """ Turn computer vision classes into Wikidata qids"""
    with open(r"classes_places.json", "r") as f:
        classes = json.load(f)
		
    qid_array = []
    for el in array:
        key = el.split('/')[0].lower().strip()
        qid_array.append("wd:" + classes[key])
    return ", ".join(qid_array)
    


def getLCS(array):
    """
    Get the Least common subsumers between several Wikidata qids in a list
	Return a Python list
    """
	
    query = {"query": """
    SELECT ?lcs ?lcsLabel WHERE {
    ?lcs ^wdt:P279* %s .
    filter not exists {
    ?sublcs ^wdt:P279* %s ;
          wdt:P279 ?lcs .
      }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en " . } }""" % (array, array)
    }
    url = "https://query.wikidata.org/sparql"
    r = requests.get(url, params=query)
    soup = BeautifulSoup(r.text, "lxml")

    return [x.text for x in soup.find_all("literal")]


if __name__ == '__main__':
    
    array = ["synagogue/indoor", "mosque/outdoor",
         "church", "palace"]  

    list_of_qids = cvClassToQid(array)

    print(getLCS(list_of_qids))
