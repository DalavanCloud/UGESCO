# -*- coding: utf-8 -*-
import json
import random
import re
import numpy as np
import pandas as pd
import requests
import requests_cache
from time import sleep
from bs4 import BeautifulSoup
from unidecode import unidecode
from dict_digger import dig  # facilite l'accès aux dictionnaires
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module='bs4')
from flatten_json import flatten
from rosette.api import API, DocumentParameters, RosetteException
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
import functools
from ngram import NGram

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


def get_similar(data, target):
    G = NGram(target)
    return G.find(data)


def get_similars(data, target, threshold):
    G = NGram(target)
    return G.search(data, threshold=threshold)[0][0]


class cache(object):

    def __init__(self, fn):
        self.fn = fn
        self._cache = {}
        functools.update_wrapper(self, fn)

    def __call__(self, *args, **kwargs):
        key = str(args) + str(kwargs)
        if key in self._cache:
            ret = self._cache[key]
        else:
            ret = self._cache[key] = self.fn(*args, **kwargs)

        return ret

    def clear_cache(self):
        self._cache = {}


@cache
def gsrsearch(query, lang="FR", results=10):
    '''
    Do a Wikipedia search for `query` and 
    return a list of tuples (page title, url).
    Use ngram module to get the best match

    Keyword arguments:

    * lang : language iso code : en, fr, etc.
    * results - the maximum number of results returned

    '''

    search_params = {
        'action': 'query',
        'generator': 'search',
        'prop': 'info',
        'inprop': 'url',
        'gsrlimit': results,
        'gsrsearch': query,
        'format': 'json'
    }

    url = "https://{}.wikipedia.org/w/api.php?".format(lang.lower())

    raw_results = requests.get(url, params=search_params).json()

    try:

        search_results = [d['title']
                          for i, d in raw_results['query']['pages'].items()]
        url_results = [d['fullurl']
                       for i, d in raw_results['query']['pages'].items()]
    except KeyError:
        return None

    try:

        most_similar = get_similars(query, search_results, 0.15)
        return most_similar + " (%s)" % (url_results[search_results.index(most_similar)])

    except IndexError:

        return list(zip(search_results, url_results))



# Nominatim bloque les requêtes répétées
requests_cache.install_cache('nominatim_cache')

s = requests.Session()


def get_nominatim(value, countrycodes=['BE', ''], limit=5, lang="fr"):
    # doc : https://wiki.openstreetmap.org/wiki/Nominatim
    url = 'http://nominatim.openstreetmap.org/'

    params = {'q': value,
              'format': 'jsonv2',
              'addressdetails': 1,
              'limit': limit,
              'email': 'ettorerizza@mail.com',
              'polygon_kml': 0,
              'extratags': 1,
              'namedetails': 0,
              # ajouter un country_code vide simule
              # la péréférence pour un pays de geopy
              # sans se limiter à celui-ci
              'countrycodes': countrycodes,
              'accept-language': lang
              }

    headers = {
        'User-Agent': 'Ugesco app',
        'From': 'ettorerizza@mail.com'
    }

    result = s.get(url, params=params, headers=headers, timeout=10).json()

    # Nominatim bloque les requêtes trop rapides
    sleep(1)

    return result


# chemins vers l'appli Stanford NER et le modèle CRF Europeana
MODEL = r'D:\stanford-ner-2017-06-09\classifiers\eunews.fr.crf.gz'
STANFORD_JAR = r'D:\stanford-ner-2017-06-09\stanford-ner.jar'

PUNCTUATION = re.compile('[%s]' % re.escape(
    '!"#$%&()*+,./:;<=>?@[\\]^_`{|}~'))


class Fingerprinter(object):
    '''
    Python implementation of Google Refine fingerprinting algorithm described here:
    https://github.com/OpenRefine/OpenRefine/wiki/Clustering-In-Depth
    Requires the unidecode module: https://github.com/iki/unidecode
    '''

    def __init__(self, string):
        self.string = self._preprocess(string)

    def _preprocess(self, string):
        '''
        Strip leading and trailing whitespace, lowercase the string, remove all punctuation except -,
        in that order.
        '''
        return PUNCTUATION.sub('', string.strip().lower())

    def _latinize(self, string):
        '''
        Replaces unicode characters with closest Latin equivalent. For example,
        Alejandro González Iñárritu becomes Alejando Gonzalez Inarritu.
        '''
        return unidecode(string)

    def _unique_preserving_order(self, seq):
        '''
        Returns unique tokens in a list, preserving order. Fastest version found in this
        exercise: http://www.peterbe.com/plog/uniqifiers-benchmark
        '''
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    def get_fingerprint_nonsorted(self):
        '''
        Gets non sorted fingerpint that remove isolated letters
        '''
        result = self._latinize(' '.join(
            self._unique_preserving_order(
                self.string.split()

            )
        ))

        return re.sub(r'\b\w{1}\b', '', result)

    def get_fingerprint(self):
        '''
        Gets conventional fingerpint.
        '''
        return self._latinize(' '.join(
            self._unique_preserving_order(
                sorted(self.string.split())
            )
        ))

    def get_ngram_fingerprint(self, n=1):
        '''
        Gets ngram fingerpint based on n-length shingles of the string.
        Default is 1.
        '''
        return self._latinize(''.join(
            self._unique_preserving_order(
                sorted([self.string[i:i + n]
                        for i in range(len(self.string) - n + 1)])
            )
        ))


def classify(text):
    """
    Test du Stanford NER tagger avec NLTK et les modèles CRF d'Europeana
    entrainés sur des journaux :
    http://lab.kbresearch.nl/static/html/eunews.html
    Récrire cette partie en utilisant pathlib pour éviter les chemins absolus
    """
    st = StanfordNERTagger(MODEL,
                           STANFORD_JAR,
                           encoding='utf-8')

    tokenized_text = word_tokenize(text)
    ner_output = st.tag(tokenized_text)

    return ner_output


def rechunk(ner_output):
    """regroupe les entités par type si elles sont consécutives.
    [('Jean', 'I-PERS'), ('Duvieusart', 'I-PERS')] devient ainsi
    [('Jean Duvieusart', 'I-PERS')]"""
    chunked, pos, prev_tag = [], "", None
    for i, word_pos in enumerate(ner_output):
        word, pos = word_pos
        if pos in ['I-PERS', 'I-LIEU', 'I-ORG'] and pos == prev_tag:
            chunked[-1] += word_pos
        else:
            chunked.append(word_pos)
        prev_tag = pos

    clean_chunked = [tuple([" ".join(wordpos[::2]), wordpos[-1]])
                     if len(wordpos) != 2 else wordpos for wordpos in chunked]

    return clean_chunked


def get_ner_lieux(clean_chunks):
    """récupération des lieux dans la liste de tuples"""
    list_loc = []
    for i, j in clean_chunks:
        if j == "I-LIEU":
            list_loc.append(i)
    list_loc = list(set(list_loc))
    return list_loc


def get_ner(text):
    """Récupération des lieux à l'aide de stanford NER"""
    ner_output = classify(text)
    clean_chunks = rechunk(ner_output)
    lieux = get_ner_lieux(clean_chunks)

    return lieux


def isQidACity(item):
    """
    Test if an items is considered as a city in the Wikidata ontology.
    The answer can be True, False or None.
    """
    query = {"query": """
    SELECT ?classe WHERE { 
    wd:%s wdt:P31/wdt:P279* ?classe . 

    }
    """ % (item)
    }

    url = "https://query.wikidata.org/sparql"

    r = requests.get(url, params=query)

    soup = BeautifulSoup(r.text, "lxml")

    result = [x.text.split("/")[-1] for x in soup.find_all("uri")]

    if "Q15284" in result:
        return True
    elif len(result) == 0:
        return None
    else:
        return False


def rosette(text):
    """ Extract PER, LOC, ORG, TITLE, DATE... from a text with Rosette API """
    # Create an API instance
    api = API(user_key="c3a4cbadf2c7be90a768b0269282209b",
              service_url="https://api.rosette.com/rest/v1/")
    params = DocumentParameters()
    params["content"] = text
    params["genre"] = "social-media"
    # Extract entities
    liste = []
    try:
        result = api.entities(params)
        for i in result['entities']:
            liste.append(i['type'] + "||" +
                         i['normalized'] + "||" + i['mention'])
        return ",".join(liste)
    except RosetteException as exception:
        return exception

# fonction qui sert à splitter les colonnes multivaluées


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


# def get_nested_rec(key, grp):
#     """
#     fonction destinée à transformer un csv en json
#     suivant le schéma de Samnang
#     """
#     rec = dict(PrimaryId=key[0],
#                FirstName=key[1],
#                LastName=key[2],
#                City=key[3])

#     for field in ['CarName', 'DogName']:
#         rec[field] = list(grp[field].unique())

#     return rec
