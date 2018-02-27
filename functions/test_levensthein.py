import Levenshtein as L

string1 = 'Bruxelles'
string2 = 'Brussels'

print('Levenshtein is  ', L.distance(string1, string2))
print('jaro-winkler is ', L.jaro_winkler(string1, string2))
print('jaro is ', L.jaro(string1, string2))


from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

print('difflib is ', similar(string1, string2))
