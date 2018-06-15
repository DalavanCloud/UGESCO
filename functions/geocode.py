# https://www.programcreek.com/python/example/108180/geopy.geocoders.Nominatim

from geopy.geocoders import Nominatim
import google_streetview.api


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

    print(geocode("gare du nord", "BE"))

    # Import google_streetview for the api module

    # Define parameters for street view api
    params = [{
            'size': '600x300',  # max 640x640 pixels
            'location': 'rue de bruxelles braine-le-comte',
            'heading': '151.78',
            'pitch': '-0.76',
            'key': 'AIzaSyA9rAKcbJITiJbVGxS-fC5E-k0b2S98MMo'
        }]

        # Create a results object
    results = google_streetview.api.results(params)
    results.download_links('downloads')
