# examples : https://www.programcreek.com/python/example/108180/geopy.geocoders.Nominatim

from geopy.geocoders import Nominatim


def geocode(value, country, one=False):
    geolocator = Nominatim(country_bias=country,
                           user_agent='ettorerizza@gmail.com')

    location = geolocator.geocode(value,
                                  exactly_one=one,
                                  timeout=4,
                                  limit=None,
                                  addressdetails=True,
                                  language="FR",
                                  geometry="KML")
    liste = []
    try:
    	if location:
	        if len(location) == 2:
	            return location  # remplacer address par raw pour avoir tous les détails
	        else:
	            for i in location:
	                liste.append(i)
	            return liste

    except Exception as inst:
        print(inst)


if __name__ == '__main__':

    print(geocode("Boulevard Anspacht Bruxelles", ""))
