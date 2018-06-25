import Levenshtein as L

string1 = "Musée royal de l'Afrique centrale"
string2 = "musée colonial de Tervueren"

print('Levenshtein is  ', L.distance(string1, string2))
print('jaro-winkler is ', L.jaro_winkler(string1, string2))
print('jaro is ', L.jaro(string1, string2))


from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

print('difflib is ', similar(string1, string2))


##########################################################################

data = "place gilson bruxelles belgique"
target = ["Place Charles Gilson", "avenue Gilson", "Gilson"]


import jellyfish
def get_jw_match(data, target):
    """Uses the jaro-winkler algorithm to match strings(names) from the   target(the set from which you want to find matches) to the data(the set for which you are trying to find matches."""
    score_dict = dict()
    for i, item_target in enumerate(target):
        for j, item_data in enumerate(data):
            jw_score = jellyfish.jaro_winkler(item_data, item_target)
            score_dict[i] = j

    return score_dict

print(get_jw_match(data, target))

######################################################""
from ngram import NGram

def get_similar(data, target):
    G = NGram(target)
    return G.find(data)


def get_similars(data, target, threshold):
    G = NGram(target)
    return G.search(data, threshold=threshold)[0][0]

print(get_similar(data, target))
print(get_similars(data, target, 0.1))