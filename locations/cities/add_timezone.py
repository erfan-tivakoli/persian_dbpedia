import json
import traceback
from tqdm import tqdm
from pymongo import MongoClient
import requests

__author__ = 'Rfun'

client = MongoClient()
db = client.joojoo

with open('./data/cities.json') as f:
    all_cities = json.load(f)


def get_lat_lng_of_cities():
    available_usernames = ['mega', 'sarah', 'barak', 'smith', 'Rimon']
    iterator = 0
    cities = []
    max_number_of_tries = 3
    number_of_sequential_tries = 0
    for city in tqdm(all_cities):
        try:
            lat = city['lat']
            lng = city['lng']
            url = "http://api.geonames.org/timezoneJSON?formatted=true&lat=" + lat + "&" + \
                  "lng=" + lng + "&" + "username=" + available_usernames[iterator] +"&style=full"
            result = requests.get(url).json()
            city['timezone_id'] = result['timezoneId']
            cities.append(city)
            number_of_sequential_tries = 0
        except IOError:
            traceback.print_exc()
            print(city['english_name'])
        except KeyError:
            number_of_sequential_tries += 1
            if number_of_sequential_tries == max_number_of_tries:
                number_of_sequential_tries = 0
                print("time limit exceeded in  " + str(all_cities.index(city)) + " , we change the username :D")
                iterator += 1

    return cities


def main():
    cities = get_lat_lng_of_cities()
    with open('data/cities.json', 'w+', encoding='utf-8') as f:
        f.write(json.dumps(cities, ensure_ascii=False))


if __name__ == '__main__':
    main()
