# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 12:35:54 2018

@author: ettor
"""

import pandas as pd
import requests
import requests_cache


requests_cache.install_cache('wikidata_cache')


def get_wikidata(value, type_id, prop_id='', prop_value='', lang="fr"):
  """ Use the Antonin's API to return the best match on Wikidata based on the type and a property.
  The result is a tuple (main_type, match, name, qid, score)
  Example : get_wikidata('Binche', 'Q618123', 'P17', 'Q31')
  Result : ('municipality of Belgium', False, 'Binche', 'Q95121', 100.0)
  """
  base_url = "https://tools.wmflabs.org/openrefine-wikidata/%s/api" % (lang)

  query = {"query": """{"query":"%s",
                      "limit":0,
                      "type" : "%s"}""" % (value, type_id)}

  if prop_id or prop_value:
    query = {"query": """{"query":"%s",
                      "limit":0,
                      "type" : "%s",
                      "properties":[{"pid":"%s",
                      "v":{"id":"%s"}}]}""" % (value, type_id, prop_id, prop_value)}

  r = requests.get(base_url, params=query)

  # print(r.url)

  json_result = r.json()

  # print(json_result)

  try:
    qid = [d['id'] for d in json_result['result']]
    name = [d['name'] for d in json_result['result']]
    score = [d['score'] for d in json_result['result']]
    match = [d['match'] for d in json_result['result']]
    main_type = [d['type'][0]['name'] for d in json_result['result']]

    df = pd.DataFrame({'qid': qid,
                       'name': name,
                       'score': score,
                       'match': match,
                       'main_type': main_type
                       })

    # order by score
    df.sort_values(['score'], ascending=[
                   False], inplace=True)

    # select the best match
    match = df[df['match'] == True].values

    if match.size > 0:
      best_match = tuple(map(tuple, match))[0]
    else:
      best_match = tuple(map(tuple, df.iloc[[0]].values))[0]

    return best_match

  except IndexError:
    return "No match"


if __name__ == '__main__':

  print(get_wikidata('Binche', 'Q618123', 'P31', 'Q15273785', "fr"))
  print(get_wikidata('Binche', 'Q618123'))

  print(get_wikidata('camp de beverloo', 'Q618123'))
