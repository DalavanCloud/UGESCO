# -*- coding: utf-8 -*-
"""
Created on Sat Jul 29 12:37:24 2017

@author: Ettore Rizza
"""

from fuzzywuzzy import process
import pandas as pd
import re
from unidecode import unidecode
import string
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import wikipedia
import difflib
import spotlight #https://pypi.python.org/pypi/pyspotlight/0.7.1
import langid
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')


def fuzzy_match(value, liste):
    result, score = process.extractOne(value, liste)
    if score > 90:
        return result

def search_wikipedia(value):

    value = '"%s"' %(value)
    for lang in ["fr", "nl", "en"]:
        try:   
            url = "https://{}.wikipedia.org/w/api.php?".format(lang)    
        
            payload = {"action":"query",
                       "list":"search",
                       "srsearch":value,
                       "srwhat":"text",
                       "srprop":"snippet",
                       "continue":"",
                       "format":"json"}
            
            r = requests.get(url, params=payload).json()
            for page in r['query']['search']:
                    return page['snippet']
        except KeyError:
            continue
        
        

PUNCTUATION = re.compile('[%s]' % re.escape(string.punctuation))


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
        Strip leading and trailing whitespace, lowercase the string, remove all punctuation,
        in that order.
        '''
        return PUNCTUATION.sub('', string.strip().lower())

    def _latinize(self, string):
        '''
        Replaces unicode characters with closest Latin equivalent. For example,
        Alejandro González Iñárritu becomes Alejando Gonzalez Inarritu.
        '''
        return unidecode(string.decode('utf-8'))

    def _unique_preserving_order(self, seq):
        '''
        Returns unique tokens in a list, preserving order. Fastest version found in this
        exercise: http://www.peterbe.com/plog/uniqifiers-benchmark
        '''
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

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

def get_personnes(value, prenoms):
    CHARS = "abcdefghijklmnopqrstuvwxyzéëèàäâçüûùABCDEFGHIJKLMNOPQRSTUVWXYZ- "
    
    family_joint = ["d'", "d", "de", "du", "der", "den", "vander", "vanden", "van", "le", "la", "von"]
    
    valeurs = "".join(unidecode(c.lower().replace("-", " ")) for c in str(value) if c in CHARS).strip()
    valeurs = re.sub(r"\s+", " ", valeurs).split(' ')
    
    liste = []
    
    if len(valeurs) > 1:
        for i, token in enumerate(valeurs):
            if token in prenoms:
                liste.append(token)
                try:
                    liste.append(valeurs[i + 1])
                    if valeurs[i + 1] in family_joint and valeurs[i + 2] not in liste:
                        liste.append(valeurs[i + 2])
                        if valeurs[i + 2] in family_joint and valeurs[i + 3] not in liste:
                            liste.append(valeurs[i + 3])
                except IndexError:
                    try:
                        if valeurs[i - 1] not in liste:
                            liste.insert(1, valeurs[i - 1])
                            if valeurs[i - 2] in family_joint and valeurs[i - 2] not in liste:
                                liste.insert(1, valeurs[i - 2])
                            if valeurs[i - 3] in family_joint and valeurs[i - 3] not in liste:
                                liste.insert(1, valeurs[i - 3])
                    except IndexError:
                        pass
    
    #liste dédoublonnée
    seen = set()
    seen_add = seen.add
    liste = [x for x in liste if not (x in seen or seen_add(x))]
    return " ".join(liste)

def get_personnes_clean(value, prenoms, lieux):
    CHARS = "abcdefghijklmnopqrstuvwxyzéëèàäâçüûùABCDEFGHIJKLMNOPQRSTUVWXYZ- "
    
    family_joint = ["d'", "d", "de", "du", "der", "den", "vander", 
                    "saint", "sainte", "sint", "vanden", "van", "le", "la", "von"]
    
    valeurs = "".join(unidecode(c.lower()) for c in str(value) if c in CHARS).strip()
    valeurs = re.sub(r"\s+", " ", valeurs).split(' ')
    
    liste = []
    
    if len(valeurs) > 1:
        for i, token in enumerate(valeurs):
            if token in prenoms:
                try:
                    if(valeurs[i + 1] not in lieux ):
                        liste.append(token)
                        liste.append(valeurs[i + 1])
                        if(valeurs[i + 1] in family_joint and
                           valeurs[i + 2] not in liste):
                            liste.append(valeurs[i + 2])
                            if(valeurs[i + 2] in family_joint and 
                               valeurs[i + 3] not in liste):
                                liste.append(valeurs[i + 3])
#                    elif (len(valeurs[i + 1]) > 2 and
#                       valeurs[i + 1] in lieux):
#                        liste.append(token)
#                        liste.append(valeurs[i - 1])
                except IndexError:
                    try:
                        if(valeurs[i - 1] not in liste 
                           and len(valeurs[i - 1]) > 2 and
                           valeurs[i - 1] not in family_joint
                           and valeurs[i - 1] not in lieux):
                            liste.append(token)
                            liste.insert(1, valeurs[i - 1])
                            if(valeurs[i - 2] in family_joint and 
                               valeurs[i - 2] not in liste and
                               valeurs[i - 2] not in lieux):
                                liste.insert(1, valeurs[i - 2])
                                if(valeurs[i - 3] in family_joint and 
                                   valeurs[i - 3] not in liste and
                                   valeurs[i - 3] not in lieux):
                                    liste.insert(1, valeurs[i - 3])
                    except IndexError:
                        pass
    
    #liste dédoublonnée
    seen = set()
    seen_add = seen.add
    liste = [x.title() for x in liste if not (x in seen or seen_add(x))]
    return " ".join(liste)

#patronymes_locaux = []
#def get_personnes_patronymes(value, prenoms, lieux, mots, noms_famille, patronymes_locaux):
#    CHARS = "abcdefghijklmnopqrstuvwxyzéëèàäâçüûùABCDEFGHIJKLMNOPQRSTUVWXYZ- "
#    
#    family_joint = ["d'", "d", "de", "du", "der", "des", "den", "vander", 
#                    "saint", "sainte", "vanden", "van", "le", "la", "von"]
#    
#    valeurs = "".join(unidecode(c.lower()) for c in str(value) if c in CHARS).strip()
#    valeurs = re.sub(r"\s+", " ", valeurs).split(' ')
#    
#    liste = []
#    patronym = ""
#    if len(valeurs) > 1:
#        for i, token in enumerate(valeurs):
#            if token in prenoms:
#                try:
#                    if(valeurs[i + 1] not in lieux):
#                        liste.append(token)
#                        patronym = valeurs[i + 1]
#                        liste.append(valeurs[i + 1])
#                        if(valeurs[i + 1] in family_joint and 
#                           valeurs[i + 2] not in liste):
#                            patronym = valeurs[i + 1] + " " + valeurs[i + 2]
#                            liste.append(valeurs[i + 2])
#                            if(valeurs[i + 2] in family_joint and 
#                               valeurs[i + 3] not in liste):
#                                patronym = valeurs[i + 1] + " " + valeurs[i + 2] + " " + valeurs[i + 3]
#                                liste.append(valeurs[i + 3])
#                    else:
#                        try:
#                            if(valeurs[i - 1] not in liste 
#                               and len(valeurs[i - 1]) > 2 and 
#                               valeurs[i - 1] not in family_joint):
#                                liste.append(token)
#                                patronym = valeurs[i - 1]
#                                liste.insert(1, valeurs[i - 1])
#                                if(valeurs[i - 2] in family_joint and 
#                                   valeurs[i - 2] not in liste and
#                                   valeurs[i - 2] not in lieux):
#                                    patronym = valeurs[i - 2] + " " + valeurs[i - 1]
#                                    liste.insert(1, valeurs[i - 2])
#                                if(valeurs[i - 3] in family_joint and 
#                                   valeurs[i - 3] not in liste and
#                                   valeurs[i - 3] not in lieux):
#                                    patronym = valeurs[i - 3] + " " + valeurs[i - 2] + " " + valeurs[i - 1]
#                                    liste.insert(1, valeurs[i - 3])
#                        except IndexError:
#                            pass
#                        
#                except IndexError:
#                    try:
#                        if(valeurs[i - 1] not in liste 
#                           and len(valeurs[i - 1]) > 2):
#                            liste.append(token)
#                            patronym = valeurs[i - 1]
#                            liste.insert(1, valeurs[i - 1])
#                            if(valeurs[i - 2] in family_joint and 
#                               valeurs[i - 2] not in liste and
#                               valeurs[i - 2] not in lieux):
#                                patronym = valeurs[i - 2] + " " + valeurs[i - 1]
#                                liste.insert(1, valeurs[i - 2])
#                            if(valeurs[i - 3] in family_joint and 
#                               valeurs[i - 3] not in liste and
#                               valeurs[i - 3] not in lieux):
#                                patronym = valeurs[i - 3] + " " + valeurs[i - 2] + " " + valeurs[i - 1]
#                                liste.insert(1, valeurs[i - 3])
#                    except IndexError:
#                        pass
#
#    
#    if ((patronym not in lieux and
#        patronym not in mots and
#        len(patronym) > 2) or
#         patronym in noms_famille):
#        patronymes_locaux.append(patronym)
#        seen = set()
#        seen_add = seen.add
#        liste = [x.title() for x in liste if not (x in seen or seen_add(x))]
#        return " ".join(liste)
#    else:
#        return None
    
def get_family_name(value, prenoms, noms, lieux):
    CHARS = "abcdefghijklmnopqrstuvwxyzéëèàäâçüûùABCDEFGHIJKLMNOPQRSTUVWXYZ- "
    
    family_joint = ["d'", "d", "de", "du", "der", "den", "vander", "vanden", "van", "le", "la", "von"]
    
    valeurs = "".join(unidecode(c.lower().replace("-", " ")) for c in str(value) if c in CHARS).strip()
    valeurs = re.sub(r"\s+", " ", valeurs).split(' ')
    
    liste = []
    

    for i, token in enumerate(valeurs):
            try:
                if((token in noms) and token not in lieux):
                    liste.append(token)
                if(token in family_joint and 
                      (valeurs[i + 1] not in liste and
                       valeurs[i + 1] in noms)):
                        liste.append(token)
                        liste.append(valeurs[i + 1])
                        if(valeurs[i + 1] in family_joint and 
                           (valeurs[i + 2] not in liste and
                            valeurs[i + 2] in noms)):
                            liste.append(valeurs[i + 2])

            except IndexError:
                pass
    
    #liste dédoublonnée
    seen = set()
    seen_add = seen.add
    liste = [x.title() for x in liste if not (x in seen or seen_add(x))]
    result = " ".join(liste)
    if result != get_personnes_clean(value, prenoms, lieux):
        return result


def get_lieux(value, lieux):
    liste = []
    CHARS = "abcdefghijklmnopqrstuvwxyzéëèàäâçüûùABCDEFGHIJKLMNOPQRSTUVWXYZ- "
    valeurs = "".join(unidecode(c.lower().replace("-", " ")) for c in str(value) if c in CHARS).strip()
    valeurs = re.sub(r"\s+", " ", valeurs).split(' ')


    for i, tokens in enumerate(valeurs):
        try:
            if tokens in lieux:
                tokens = tokens
            if tokens + " " + valeurs[i+1] in lieux:
                tokens = tokens + " " + valeurs[i+1]
            if tokens + "-" + valeurs[i+1] in lieux:
                tokens = tokens + "-" + valeurs[i+1]
            if tokens + "-" + valeurs[i+1] + "-" + valeurs[i+2] in lieux:
                tokens = tokens + "-" + valeurs[i+1] + "-" + valeurs[i+2]
            if tokens + " " + valeurs[i+1] + " " + valeurs[i+2] in lieux:
                tokens = tokens + " " + valeurs[i+1] + " " + valeurs[i+2]
            if tokens + " " + valeurs[i+1] + " " + valeurs[i+2] + valeurs[i+3]in lieux:
                tokens = tokens + " " + valeurs[i+1] + " " + valeurs[i+2] + + valeurs[i+3]
            if tokens + " " + valeurs[i+1] + " " + valeurs[i+2] + valeurs[i+3]in lieux:
                tokens = tokens + "-" + valeurs[i+1] + "-" + valeurs[i+2] + valeurs[i+3]
        except IndexError:
            pass
        if tokens in lieux:
            liste.append(tokens)
        for i, tokens in enumerate(liste):
            try:
                if liste[i+1] in liste[i]:
                    del liste[i+1]
            except IndexError:
                pass
    
    liste = set(liste)
    return "||".join(liste)

def get_lieux_clean(value, lieux, prenoms):
    liste = []
    CHARS = "abcdefghijklmnopqrstuvwxyzéëèàäâçüûùABCDEFGHIJKLMNOPQRSTUVWXYZ "
    family_joint = ["d'", "d", "de", "du", "der", "den", "vander", "op", "vanden", "van", "le", "la", "von"]
    valeurs = "".join(unidecode(c.lower().replace("-", " ")) for c in str(value) if c in CHARS).strip()
    valeurs = re.sub(r"\s+", " ", valeurs).split(' ')


    for i, tokens in enumerate(valeurs):
        try:
            if(valeurs[i-1] in family_joint and 
                valeurs[i-2] in prenoms):
                continue
            if tokens in lieux:
                tokens = tokens
            if tokens + " " + valeurs[i+1] in lieux:
                tokens = tokens + " " + valeurs[i+1]
            if tokens + "-" + valeurs[i+1] in lieux:
                tokens = tokens + "-" + valeurs[i+1]
            if tokens + "-" + valeurs[i+1] + "-" + valeurs[i+2] in lieux:
                tokens = tokens + "-" + valeurs[i+1] + "-" + valeurs[i+2]
            if tokens + " " + valeurs[i+1] + " " + valeurs[i+2] in lieux:
                tokens = tokens + " " + valeurs[i+1] + " " + valeurs[i+2]
            if tokens + " " + valeurs[i+1] + " " + valeurs[i+2] + valeurs[i+3]in lieux:
                tokens = tokens + " " + valeurs[i+1] + " " + valeurs[i+2] + + valeurs[i+3]
            if tokens + " " + valeurs[i+1] + " " + valeurs[i+2] + valeurs[i+3]in lieux:
                tokens = tokens + "-" + valeurs[i+1] + "-" + valeurs[i+2] + valeurs[i+3]
        except IndexError:
            pass
        if tokens in lieux:
            liste.append(tokens)
        for i, tokens in enumerate(liste):
            try:
                if liste[i+1] in liste[i]:
                    del liste[i+1]
            except IndexError:
                pass

    liste = set(liste)
    return "||".join(liste)

def detect_lang(value):
    langid.set_languages(['fr','nl'])
    return langid.classify(value)


def get_wikipedia(value):
    for lang in ["fr", "nl", "en"]:
        wikipedia.set_lang(lang)
        try:
            w = wikipedia.page(value, auto_suggest=True)
            score= difflib.SequenceMatcher(None, value, re.sub(r"\(.+\)", "", w.title)).ratio()
            if score >= 0.7:
                return w.title + "||" + w.url + "||" + ":::".join(wikipedia.WikipediaPage(w.title).categories)
            elif score >= 0.5:
                return "Possibilité: " + w.title + "||" + w.url + "||" + ":::".join(wikipedia.WikipediaPage(w.title).categories)
        except wikipedia.exceptions.PageError:
            continue
        except wikipedia.exceptions.DisambiguationError as e:
            w = e.options[0]
            return w  + "||https://fr.wikipedia.org/wiki/" + w + " ::: ambigu "
    
def get_wikipedia_page2(value):

    if type(value) is str:
        value = value.title()
        for lang in ["fr", "nl", "en"]:
            
            url = "https://{}.wikipedia.org/w/api.php?".format(lang)
    
            payload = {"format":"json",
                       "action":"query",
                       "generator":"search",
                       "gsrnamespace":0,
                       "gsrsearch":value,
                       "gsrlimit":20,
                       "prop":"categories|extracts|info|revisions|pageprops",
                       "inprop":"url",
                       "ppprop":"wikibase_item",
                       "rvprop":"content",
                       "exintro":"",
                       "explaintext":"",
                       "exsentences":2,
                       "exlimit":"max",
                       "cllimit":"max"}
            
            r = requests.get(url, params=payload).json()
            try:
                for pageid, page in r["query"]["pages"].items():
                    try:
                        if page['title'].startswith(value) or page['title'].startswith("Ville"):
                            if "belgi" in page['extract'].lower():
                                for cat in page['categories']:                                        
                                    if ("commune" in cat['title'].lower() 
                                        or "ville" in cat['title'].lower()
                                        or "localité" in cat['title'].lower() 
                                        or "plaats" in cat['title'].lower() 
                                        or "municipalit" in cat['title'].lower()
                                        or "city" in cat['title'].lower()):
                                        
                                        info = (page['title'], 
                                                page['fullurl'],
                                                page['length'],
                                                page['categories'],
                                                page['extract'],
                                                page['pageprops']['wikibase_item'])
                                                #page['revisions'])
                                        return info
                                        break

                    except KeyError:
                        continue             
    
            except (KeyError, UnboundLocalError):
                 return None


def get_wikipedia_page(value):
    try:

        if type(value) is str:
            value = value.title()
            for lang in ["fr", "nl", "en"]:
                
                url = "https://{}.wikipedia.org/w/api.php?".format(lang)
        
                payload = {"format":"json",
                           "action":"query",
                           "titles":value,
                           "exlimit":5,
                           "prop":"categories|extracts|info|revisions|pageprops",
                           "inprop":"url",
                           "ppprop":"wikibase_item",
                           "exintro":"",
                           "explaintext":"",
                           "redirects":"",
                           "rvprop":"content"}
                
                r = requests.get(url, params=payload).json()
                for pageid, page in r["query"]["pages"].items():
                    homonym = False
                    for cat in page['categories']:
                        #print(cat)
                        if "Homonymie" in cat['title'] or "Doorverwijspagina" in cat['title'] or "Disambiguation" in cat['title']:
                            homonym = True
                        elif ("belgique" in cat['title'].lower() or 
                              "plaats" in cat['title'].lower() or 
                              "municipali" in cat['title'].lower() or
                              "localité" in cat['title'].lower()):
                            info = (page['title'], 
                                    page['fullurl'],
                                    page['length'],
                                    page['categories'],
                                    page['extract'],
                                    page['pageprops']['wikibase_item'])
                                    #page['revisions'])
                            return info
                            break
                        else:
                            continue


                        if homonym == True:
                            #print("homonyme")
                            continue
                        
                return info   
    except:
        return None 
    
def get_wikipedia_element(ville):
    try:
        resp = get_wikipedia_page(ville)
        if resp == None:
            resp = get_wikipedia_page2(ville)
        (title, url, length, categories, extract, wikidata) = resp
        return title + ":::" + url + ":::" + extract + ":::" + wikidata + ":::" + str(length)
    except TypeError:
        pass
    
def clean_person_names(value, liste_mots):
    family_joint = ["d'", "d", "de", "du", "der", "den", "vander", "vanden", "van", "le", "la", "von"]
    data = value.strip().lower().split(' ')
    try:
        if data[1] in family_joint:
            pass
        else:
            nom = data[1]
        
        if nom in liste_mots:
            return None
        else:
            return value
    except IndexError:
        pass
    except UnboundLocalError:
        return value
    
def compare_names(value, noms_famille, liste_mots):
    family_joint = ["d'", "d", "de", "du", "der", "den", "vander", "vanden", "van", "le", "la"]
    test = value.strip().lower().split(' ')
    try:
        name = test[-1]
        if test[-3] in family_joint:
            name = test[-3] + " " + test[-2] + " " + test[-1]
        elif test[-2] in family_joint:
            name = test[-2] + " " + test[-1]
    except IndexError:
        pass
    if name in noms_famille or clean_person_names(value, liste_mots) is not None:
        return "Possible nom"
    else:
        return "Improbable"
    
def query(value, lang):
            value = value.title()
            sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
            sparql.setQuery("""
            PREFIX schema: <http://schema.org/>
            SELECT DISTINCT ?item ?article ?itemDescription WHERE {
            ?item rdfs:label "%s"@%s.
            ?item wdt:P17 wd:Q31.
            ?article schema:about ?item.
            ?article schema:isPartOf <https://%s.wikipedia.org/>.
            SERVICE wikibase:label { bd:serviceParam wikibase:language "%s". }
            }
            """ % (value, lang, lang, lang)) 
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            try:
                results_df = pd.io.json.json_normalize(results['results']['bindings'])
                resultats = results_df.iloc[0]['article.value']
            except IndexError:
                resultats = None
            return resultats

def get_sparql(value):
    if value is not None:
        try:
            resultats = query(value, "fr")
            if resultats is None:
                resultats = query(value, "nl")
                if resultats is None:
                    resultats = query(value, "en")
        except IndexError:
            resultats = None
        return resultats

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

def get_dbpedia_person(value):
    
    from SPARQLWrapper import SPARQLWrapper, JSON
    
    sparql = SPARQLWrapper("http://dbpedia.org/sparql/")
    sparql.setQuery("""
    SELECT DISTINCT ?entity ?score1
    	WHERE {
    		?entity ?p ?label.
    		?label <bif:contains> "'%s'" OPTION(score ?score1). 
    		FILTER (?p=<http://www.w3.org/2000/01/rdf-schema#label>).
    		?entity a ?type.
    		FILTER (?type IN (<http://dbpedia.org/ontology/Person>)).
    		FILTER isIRI(?entity). 
    	} ORDER BY desc(?score1) LIMIT 5
    """ %value) 
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    liste = []
    for result in results["results"]["bindings"]:
        liste.append(result["entity"]["value"])
    
    return "||".join(liste)

def get_viaf(value, score):

    value = unidecode(value.lower())
    
    url = "http://www.viaf.org/viaf/AutoSuggest?" 
    
    payload = {"query":value}
    
    r = requests.get(url, params=payload).json()
    liste = []
    try:
        for el in r["result"]:
            if el['nametype'] == 'personal':
                result = unidecode(el["term"])
                result = re.sub(r"\d+", "", result).strip()
                liste.append(result)
        match = difflib.get_close_matches(value, liste, n=1, cutoff=score)[0]
    
        resultats = (match, "http://viaf.org/viaf/" + el['viafid'] + " ||candidates: " + str(len(liste)))
        return "||".join(resultats)
    except:
        return None

def get_dbpediaspotlight(value, dbpedia_types):
    
    types_filter = {
        'policy': "whitelist",
        'types': "DBpedia:{}".format(dbpedia_types),
        'coreferenceResolution': False}
     #ce service rest ne fonctionne plus. Utiliser plutôt un service en localhost comme dans Ugesco
    annotations = spotlight.annotate('http://spotlight.sztaki.hu:2225/rest/annotate',
                                      value,
                                      confidence = 0.2, 
                                      support = 10, 
                                      filters = types_filter)

    liste = []
    for el in annotations:
        liste.append(el['URI'] + "||" + el['types'])
    
    return ",".join(liste)
    
#print(get_dbpediaspotlight("albert einstein était à bruxelles lundi, après son rendez-vous avec Elio Di rupo", "Person"))

def stem_sentence(value):
    from nltk import PorterStemmer, word_tokenize

    tokens = word_tokenize(value)
    
    liste = []
    for el in tokens:
        liste.append(PorterStemmer().stem(el))
    return " ".join(liste)

def soundex(value):
    import re
    
    input_string = value
    
    # Initialize the end result with the first letter of the input string
    soundex_result = input_string[0].upper()
    
    # Remove all instances of h's and w's, since letters with like values
    # are all treated similar when they are adjacent or separated only by
    # h's and w's. This will make our later regex operations simpler.
    input_string = re.sub('[hw]', '', input_string, flags=re.I)
    
    # Replace all valued consonants with their respective values. Adjacent
    # valued consonants are treated as one consonant.
    input_string = re.sub('[bfpv]+', '1', input_string, flags=re.I)
    input_string = re.sub('[cgjkqsxz]+', '2', input_string, flags=re.I)
    input_string = re.sub('[dt]+', '3', input_string, flags=re.I)
    input_string = re.sub('l+', '4', input_string, flags=re.I)
    input_string = re.sub('[mn]+', '5', input_string, flags=re.I)
    input_string = re.sub('r+', '6', input_string, flags=re.I)
    
    # This transformed string still contains the first letter, so remove
    # its value from the string.
    input_string = input_string[1:]
    
    # Now remove all vowels and y's from the string.
    input_string = re.sub('[aeiouy]','', input_string, flags=re.I)
    
    # Take the first 3 digits of the transformed string and append them to the result
    soundex_result += input_string[0:3]
    
    # Soundex results are supposed to have an opening letter followed by three digits.
    # If there are less than 4 characters total, append with zeros until there are 4.
    if len(soundex_result) < 4:
        soundex_result += '0'*(4-len(soundex_result))
    
    return soundex_result

def soundex_sentence(value):
    liste = []
    for el in value.split(" "):
        liste.append(soundex(el))
    return " ".join(liste)