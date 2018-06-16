# https://www.programcreek.com/python/example/108180/geopy.geocoders.Nominatim

from geopy.geocoders import Nominatim



def geocode(value, country):
    geolocator = Nominatim(country_bias=country)
    location = geolocator.geocode(value, exactly_one=False)
    liste = []
    try:
        if len(location) == 1:
            return location[0].raw
        else:
            for i in location:
                liste.append(i.raw)
            return liste

    except Exception as inst:
        print(inst)


if __name__ == '__main__':

    print(geocode("rue Rogier  Namur", "BE"))

