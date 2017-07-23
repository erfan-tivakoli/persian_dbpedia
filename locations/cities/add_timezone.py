import json

__author__ = 'Rfun'

import traceback
from tqdm import tqdm
from pymongo import MongoClient

client = MongoClient()
db = client.joojoo
import requests

with open('./data/cities.json') as f:
    all_cities = json.load(f)

def main():
    cities = []
    for city in tqdm(all_cities):
        try:
            lat = city['lat']
            lng = city['lng']
            url = "http://api.geonames.org/timezoneJSON?formatted=true&lat=" + lat + "&" + "lng=" + lng + "&username=Rimon&style=full"
            result = requests.get(url).json()
            city['timezon_id'] = result['timezone_id']
            db.cities.update({"_id": city["_id"]},
                             {"$set": {"country_code": result['countryCode'], 'timezone_id': result['timezoneId'],
                                       'country_english_name': result['countryName']}})
        except:
            traceback.print_exc()
            print(city['english_name'])



if __name__ == '__main__':
    main()