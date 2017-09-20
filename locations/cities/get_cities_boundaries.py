__author__ = 'Rfun'

from pymongo import MongoClient
import googlemaps

client = MongoClient()
db = client.joojoo
cities = db.cities
gmaps = googlemaps.Client(key='AIzaSyDzz47NRO-0bzrb6uS1n3VBmaR_ebZA_RU')


def main():
    cursor = cities.find({})
    for city in cursor:
        try:
            english_name = city['english_name']
            if 'sw_lat' not in city and city['country'] == 'Iran':
                print("going for " + city['english_name'])
                geocode_result = gmaps.geocode(english_name)
                ne_lat = geocode_result[0]['geometry']['bounds']['northeast']['lat']
                ne_lng = geocode_result[0]['geometry']['bounds']['northeast']['lng']
                sw_lat = geocode_result[0]['geometry']['bounds']['southwest']['lat']
                sw_lng = geocode_result[0]['geometry']['bounds']['southwest']['lng']

                cities.update({"_id": city["_id"]}, {"$set": {"ne_lat": ne_lat,
                                                              "ne_lng": ne_lng,
                                                              "sw_lat": sw_lat,
                                                              "sw_lng": sw_lng}})
            else:
                print('we had city ' + english_name + 'before')
        except:
            print("========problem in " + english_name + "==========")


if __name__ == '__main__':
    main()