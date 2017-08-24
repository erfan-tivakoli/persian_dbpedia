import csv

from pymongo import MongoClient
from tqdm import tqdm

client = MongoClient()
db = client.joojoo
cities = db.cities


def add_population_to_cities():
    cities_with_population = {}
    with open('./../source_files/world_cities.csv') as f:
        reader = csv.DictReader(f)

        for row in reader:
            cities_with_population[row['city_ascii'] + '_' + row['lat'] + '_' + row['lng']] = int(row['pop'])

    all_cities = cities.find()
    for city in tqdm(all_cities):
        population = cities_with_population.get(city['english_name'] + '_' + city['lat'] + '_' + city['lng'], 0)
        db.cities.update({"_id": city["_id"]}, {"$set": {"population": population}})


if __name__ == '__main__':
    add_population_to_cities()
