import requests
import requests_cache
from time import sleep

# Nominatim bloque les requêtes répétées
requests_cache.install_cache('nominatim_cache')


def get_nominatim(value, countrycodes=['BE',''], limit=5, lang="fr"):
    # doc : https://wiki.openstreetmap.org/wiki/Nominatim
    url = 'http://nominatim.openstreetmap.org/'

    s = requests.Session()

    params = {'q': value,
              'format': 'jsonv2',
              'addressdetails': 1,
              'limit': limit,
              'email': 'yourmail@mail.com',
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
        'From': 'yourmail@mail.com'
    }

    result = s.get(url, params=params, headers=headers, timeout=10).json()

    # Nominatim bloque les requêtes trop rapides
    sleep(1)

    return result


if __name__ == '__main__':

    print(get_nominatim("bruxelles"))
