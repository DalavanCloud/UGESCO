# examples : https://www.programcreek.com/python/example/108180/geopy.geocoders.Nominatim

from geopy.geocoders import Nominatim


def geocode(value, country, one=True):
    geolocator = Nominatim(country_bias=country,
                           user_agent='ettorerizza@gmail.com')

    location = geolocator.geocode(value,
                                  exactly_one=one,
                                  limit=None,
                                  addressdetails=True, 
                                  language="FR",
                                  geometry="KML")
    liste = []
    try:
        if len(location) == 2:
            return location.raw
        else:
            for i in location:
                liste.append(i.raw)
            return liste

    except Exception as inst:
        print(inst)


if __name__ == '__main__':

    print(geocode("arc de triomphe", "FR"))
