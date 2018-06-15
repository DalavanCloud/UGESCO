from SPARQLWrapper import SPARQLWrapper, JSON
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setQuery("""#calcule la distance entre un item et l'une de ses superclasses
# Ici, distance de 5 entre l'université d'Amsterdam (start) et location (end)
# de 3 entre dog et animal et de 3 entre gare du nord et structure architecturale
#ATTENTIOn : s'il existe plusieurs chemins, celui trouvé ne sera pas forcemment le plus court !

select ?start ?end (count(?mid) as ?length)
where {
  values (?start ?end) { (wd:Q214341 wd:Q17334923) (wd:Q144 wd:Q729) (wd:Q3246590 wd:Q811979)}
  ?start wdt:P31?/wdt:P279+ ?mid .
  ?mid wdt:P31?/wdt:P279* ?end .
}
group by ?start ?end """)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    print(result)
