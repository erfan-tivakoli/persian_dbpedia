import csv
import json

'''
Here I suppose the data for cities and provinces are ready
'''

with open('data/cities.json') as f:
    all_cities = json.load(f)

with open('../province/data/provinces.json') as f:
    all_provinces = json.load(f)


with open('../source_files/world_cities.csv') as f:
    cities = []
    reader = csv.DictReader(f)

    for row in reader:
        city_name = row['city_ascii']
        for city in all_cities:
            if city['english_name'] == city_name:
                city['province'] = row['province']
                cities.append(city)
                break
    with open('data/cities.json', 'w+', encoding='utf-8') as g:
        g.write(json.dumps(cities, ensure_ascii=False))