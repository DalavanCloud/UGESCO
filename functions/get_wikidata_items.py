from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

def get_wikidata_item(predicat, objet):
    """
    Use the WDQ service to get items by property and object.
    Return a panda dataframe with the items and their english label.
    """
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    sparql.setQuery("""
    SELECT ?item ?itemLabel
    WHERE
    {
        ?item wdt:%s wd:%s .
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
    }
    """ % (predicat, objet))
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    results_df = pd.io.json.json_normalize(results['results']['bindings'])
    return results_df[['item.value', 'itemLabel.value']]


if __name__ == '__main__':

    #Instances of building
    print(get_wikidata_item('P31', 'Q41176'))








