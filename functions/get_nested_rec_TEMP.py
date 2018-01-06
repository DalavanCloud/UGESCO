# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

https://stackoverflow.com/questions/35969611/python-csv-to-nested-json
"""


import json
import numpy as np
import pandas as pd

#classe destinée à éviter des erreurs d'encodage du genre 
#"TypeError: Object of type 'int64' is not JSON serializable"
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

df = pd.read_csv("C:/Users/ettor/Desktop/data.csv")

def get_nested_rec(key, grp):
    rec = {}
    rec['PrimaryId'] = key[0]
    rec['FirstName'] = key[1]
    rec['LastName'] = key[2]
    rec['City'] = key[3]

    for field in ['CarName','DogName']:
        rec[field] = list(grp[field].unique())

    return rec

records = []
for key, grp in df.groupby(['PrimaryId','FirstName','LastName','City']):
    rec = get_nested_rec(key, grp)
    records.append(rec)

records = dict(data = records)

print(json.dumps(records, indent=4, cls=MyEncoder))