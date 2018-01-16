# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import pandas as pd
import requests
import requests_cache

requests_cache.install_cache('wikidata_cache')


def get_wikidata(item, type_id, prop_id, prop_value):
  """ Use the Antonin's API to return the best match on Wikidata based on the type and a property.
  Best match = exact match, or higher score + lesser qid magnitude
  The result is a tuple (id_magnitude, main_type, match, name, qid, score)
  Example : get_wikidata('Binche', 'Q618123', 'P17', 'Q31')
  Result : (95121, 'municipality of Belgium', False, 'Binche', 'Q95121', 100.0)
  """
  base_url = "https://tools.wmflabs.org/openrefine-wikidata/en/api"

  query = {"query": """{"query":"%s",
                      "limit":6,
                      "type" : "%s",
                      "properties" : [
                         {"pid":"%s","v":"%s"}
                         ]
                         }""" % (item, type_id, prop_id, prop_value)}

  r = requests.get(base_url, params=query)

  # print(r.url)

  try:
      json_result = r.json()
  except:
    return "no json/error"

  #print(json_result)

  try:
    qid = [d['id'] for d in json_result['result']]
    id_magnitude = [int(d['id'].replace("Q", ''))
                    for d in json_result['result']]
    name = [d['name'] for d in json_result['result']]
    score = [d['score'] for d in json_result['result']]
    match = [d['match'] for d in json_result['result']]
    main_type = [d['type'][0]['name'] for d in json_result['result']]

    df = pd.DataFrame({'qid': qid,
                       'name': name,
                       'id_magnitude': id_magnitude,
                       'score': score,
                       'match': match,
                       'main_type': main_type
                       })

    # order by score then by inverse qid magnitude. NOTE : magnitude inutile depuis qu'Antonin a modifié l'API
    df.sort_values(['score', 'id_magnitude'], ascending=[
                   False, True], inplace=True)

    # select the best match
    match = df[df['match'] == True].values

    if match.size > 0:
      best_match = match
    else:
      best_match = tuple(map(tuple, df.iloc[[0]].values))[0]

    return best_match

  except IndexError:
    return "No match"


#print(get_wikidata('Binche', 'Q618123', 'P17', 'Q31'))

#item = "Belgique"  # Bruxelles


def isQidACity(item):
    """
    get the class(es) of a Wikidata qid
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
        return None
    else:
        return False


#print(isCity(item))


def isStringACity(item):
    if item is not "":
        return get_wikidata(item, 'Q618123', 'P31/P279*', 'Q493522')
    else:
        return None

print(isStringACity("Morlanwelz"))