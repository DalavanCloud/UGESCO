# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 12:35:54 2018

@author: ettor
"""

import requests
import pandas as pd

base_url = "https://tools.wmflabs.org/openrefine-wikidata/en/api"

query = {"query" : """{"query":"Paris",
                      "limit":6,
                      "type" : "Q618123",
                      "properties" : [
                         {"pid":"P17","v":"Q142"}
                         ]
                         }"""}

r = requests.get(base_url, params = query)

#print(r.url)

json_result = r.json()

#print(json_result)

qid = [d['id'] for d in json_result['result']]
id_magnitude = [int(d['id'].replace("Q", '')) for d in json_result['result']]
name = [d['name'] for d in json_result['result']]
score = [d['score'] for d in json_result['result']]
match = [d['match'] for d in json_result['result']]

df = pd.DataFrame({  'qid': qid,
                     'name': name,
                     'id_magnitude': id_magnitude,
                     'score': score,
                     'match':match
                  })
     
#order by score then by inverse qid magnitude
df.sort_values(['score', 'id_magnitude'], ascending=[False, True], inplace=True)






