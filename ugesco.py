# -*- coding: utf-8 -*-
import json
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from flatten_json import flatten

#fonction qui sert à splitter les colonnes multivaluées
def tidy_split(df, column, sep, keep=False):
    """
    Split the values of a column and expand so the new DataFrame has one split
    value per row. Filters rows where the column is missing.

    Params
    ------
    df : pandas.DataFrame
        dataframe with the column to split and expand
    column : str
        the column to split and expand
    sep : str
        the string used to split the column's values
    keep : bool
        whether to retain the presplit value as it's own row

    Returns
    -------
    pandas.DataFrame
        Returns a dataframe with the same columns as `df`.
    """
    indexes = list()
    new_values = list()
    df = df.dropna(subset=[column])
    for i, presplit in enumerate(df[column].astype(str)):
        values = presplit.split(sep)
        if keep and len(values) > 1:
            indexes.append(i)
            new_values.append(presplit)
        for value in values:
            indexes.append(i)
            new_values.append(value)
    new_df = df.iloc[indexes, :].copy()
    new_df[column] = new_values
    return new_df



def json_to_df(file):
    """
    Input a json file, flatten it and return it as dataframe
    """
    with open(file, "r", encoding="utf-8") as f:
        json_file = json.load(f)
    
    df = pd.DataFrame([flatten(line) for line in json_file])
    
    return df

def get_wikidata(query, type_id, prop_id, prop_value):
    """ Use the Antonin's API to return the best match on Wikidata based on type and property.
    Best match = match, or higher score + lesser qid magnitude
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
                         }""" % (query, type_id, prop_id, prop_value)}

    r = requests.get(base_url, params=query)

    # print(r.url)

    json_result = r.json()

    try:
        # print(json_result)

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

        # order by score then by inverse qid magnitude
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
