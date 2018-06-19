# -*- coding: utf-8 -*-

import wikipedia
from fuzzywuzzy import fuzz
import warnings
import requests

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')


def get_wikipedia_suggestions(value):

    for lang in ["fr", "en", "nl"]:

        url = "https://{}.wikipedia.org/w/api.php?".format(lang)

        payload = {"format": "json",
                   "action": "opensearch",
                   "search": value,
                   "limit": 10,
                   "profile": "fuzzy",
                   "redirect": "resolve"}
        try:
            r = requests.get(url, params=payload).json()
            if len(r[3]) == 0:
                continue
            return r
        except Exception as e:
            print(e)


def get_wikipedia(value):
    # liste = []

    for e,i in enumerate(get_wikipedia_suggestions(value)):
        print(i[1])
        best_title = fuzz.ratio(i[1][0])
        if fuzz.ratio(best_title, value) >= 90:
            w = wikipedia.page(best_title)
    return w

    # try:
    #     w = wikipedia.page(value)

    #     score = fuzz.ratio(value, w.title)
    #     print(score)
    #     if score >= 90:
    #         print(score)
    #         liste.append("Probable: " + w.title + "||" + w.url + "||" +
    #                      ":::".join(wikipedia.WikipediaPage(w.title).categories))
    #     elif score >= 50:
    #         liste.append("Possibilité: " + w.title + "||" + w.url + "||" +
    #                      ":::".join(wikipedia.WikipediaPage(w.title).categories))
    #     else:
    #         liste.append("Improbable: " + w.title + "||" + w.url + "||" +
    #                      ":::".join(wikipedia.WikipediaPage(w.title).categories))
    # except wikipedia.exceptions.PageError:
    #     pass
    # except wikipedia.exceptions.DisambiguationError as e:
    #     w = e.options[0]
    #     return w + "||https://fr.wikipedia.org/wiki/" + w + " ::: ambigu "
    # return liste


print(get_wikipedia("la louvièr"))
