# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 17:08:40 2017

@author: Boulot
"""

#import geonames.adapters.search
#
# def get_geonames(value):
#    _USERNAME = 'ettorerizza'
#    sa = geonames.adapters.search.Search(_USERNAME)
#    country = "BE"
#    result = sa.query(value).country(country).language('FR').max_rows(1).execute()
#    for id_, name in result.get_flat_results():
#        # make_unicode() is only used here for Python version-compatibility.
#        print(geonames.compat.make_unicode("[{0}]: [{1}]").format(id_, name))
#
# print(str(get_geonames("lembecq")))
import requests


def get_geonames(value, country_code):
    url = "http://api.geonames.org/searchJSON?"

    payload = {"q": value,
               "maxRows": 1,
               "country": country_code,
               "style": "full",
               "lang=": "FR",
               "username": "ettorerizza"}
    if len(value) >= 1:
        try:
            r = requests.get(url, params=payload)

            return r.json()  # ["geonames"][0]["toponymName"]
        except IndexError:
            pass


print(get_geonames("La Louvière", "BE"))
