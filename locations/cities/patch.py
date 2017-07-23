import json
from tqdm import tqdm
from translator import translate
__author__ = 'Rfun'

if __name__ == '__main__':
    new_cities = []
    with open('data/cities.json') as f:
        cities = json.load(f)
        for city in tqdm(cities):
            if not all(ord(c) < 128 for c in city['country']):
                print(city['country'])
                city['country'] = translate.single_translate(city['country'], "fa", "en")
            new_cities.append(city)
    with open('data/cities.json', 'w+', encoding='utf-8') as f:
        f.write(json.dumps(new_cities, ensure_ascii=False))