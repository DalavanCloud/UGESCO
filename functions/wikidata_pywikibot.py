from pywikibot.data import api
import pywikibot
import pprint


def search_entities(site, itemtitle):
    params = {'action': 'wbsearchentities',
              'format': 'json',
              'language': 'en',
              'type': 'item',
              'search': itemtitle}
    request = api.Request(site=site, parameters=params)
    return request.submit()


def get_entities(site, wdItem):
    request = api.Request(site=site,
                          action='wbgetentities',
                          format='json',
                          ids=wdItem,
                          languages='en|fr',
                          props='sitelinks/urls|descriptions|aliases|labels',
                          sitefilter='enwiki|frwiki')
    return request.submit()


def prettyPrint(variable):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(variable)


# Login to wikidata
site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()

item_to_search = "Bruxelles"

wikidataEntries = search_entities(site, item_to_search)


# Print the different Wikidata entries
prettyPrint(wikidataEntries)

# Print each wikidata entry as an object
for wdEntry in wikidataEntries["search"]:
    result = get_entities(site, wdEntry["id"])
prettyPrint(result)
