# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup


def classToQid(array):
    """ get Wikidata qid from computer vision classes"""
    qid_array = []

    with open(r"classes_places.json", "r") as f:
        classes = json.load(f)

    for i in array:
        i = i.split('/')[0].lower().strip()
        qid_array.append("wd:" + classes[i])
    return ", ".join(qid_array)
    


def getLCS(array):
    """
    get the Least common subsumer between several Wikidata qids in a list
    """
    query = {"query": """
    SELECT ?lcs ?lcsLabel WHERE {

    ?lcs ^wdt:P279* %s .
    filter not exists {
    ?sublcs ^wdt:P279* %s ;
          wdt:P279 ?lcs .
      }

    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } }""" % (array, array)
    }

    url = "https://query.wikidata.org/sparql"

    r = requests.get(url, params=query)

    soup = BeautifulSoup(r.text, "lxml")

    return [x.text for x in soup.find_all("literal")]


if __name__ == '__main__':
    
    array = ["synagogue/indoor", "mosque/outdoor",
         "church", "palace"]  

    list_of_qids = classToQid(array)

    print(getLCS(list_of_qids))
