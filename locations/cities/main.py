__author__ = 'Rfun'

import csv
import difflib


from tqdm import tqdm
from translator import translate
import json
from elasticsearch import Elasticsearch

es = Elasticsearch()

'''
Here I supposed that you've run the countries/main
and now there is a countries.json file in the data
subdirectory of countries directory
'''

with open('./../countries/data/countries.json') as f:
    all_countries = json.load(f)
    all_countries_standard_name = []
    for item in all_countries:
        all_countries_standard_name.append(item['english_name'])


def load_cities_with_their_country():
    print("=============Loading cities=============")
    cities = []
    with open('./../source_files/world_cities.csv') as f:
        reader = csv.DictReader(f)

        for row in reader:
            english_name = row['city_ascii']
            lat = row['lat']
            lng = row['lng']

            country = row['country']
            province = row['provinces']
            city = {'english_name': english_name, 'lat': lat, 'lng': lng, 'country': country, 'provinces' : province}
            cities.append(city)

    print("=============Loaded=============")
    return cities



def add_persian_name(cities):
    print("=============Adding persian names=============")
    batch_size = 10

    for iter in tqdm(range(0, len(cities), batch_size)):
        english_names = [city['english_name'] for city in cities[iter: iter + batch_size]]
        persian_names = translate.batch_translate(english_names, "en", "fa")
        if persian_names is not None:
            for i in range(len(english_names)):
                cities[iter + i]['persian_name'] = persian_names[i]
        else:
            for i in range(len(english_names)):
                cities[iter + i]['persian_name'] = ""

    return cities

def add_cities_to_elastic():
    with open('data/cities.json') as f:
        cities = json.load(f)
    for city in tqdm(cities):
        es.index(index="joojoo", doc_type='cities', id=city['lat'] +'-' + city['lng'],
                 body=city)

def main():
    cities = load_cities_with_their_country()
    cities = add_persian_name(cities)
    with open('data/cities.json', 'w+', encoding='utf-8') as f:
        f.write(json.dumps(cities, ensure_ascii=False))




if __name__ == '__main__':
    # main()
    add_cities_to_elastic()