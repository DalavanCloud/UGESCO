import requests
import functools
from ngram import NGram


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
def gsrsearch(query, lang, results=10):
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

        most_similar = get_similars(query, search_results, 1)
        return most_similar + " (%s)" % (url_results[search_results.index(most_similar)])

    except IndexError:

        return list(zip(search_results, url_results))


if __name__ == '__main__':
    print(gsrsearch("namur belgique", "fr"))
