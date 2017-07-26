import json
from tqdm import tqdm

__author__ = 'Rfun'

import csv
from translator import translate


def load_countries_and_their_codes():
    print("=============Loading countries=============")
    countries = []
    countries_name = set({})
    with open('./../source_files/world_cities.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            iso2 = row['iso2']
            iso3 = row['iso3']
            english_name = row['country']
            country = {"iso3": iso3, 'iso2': iso2, "english_name": english_name}
            if english_name not in countries_name:
                countries.append(country)
                countries_name.add(english_name)

    print("=============Loaded=============")
    return countries


def add_persian_name(countries):
    print("=============Adding persian names=============")
    batch_size = 10

    for iter in tqdm(range(0, len(countries), batch_size)):
        english_names = [country['english_name'] for country in countries[iter: iter + batch_size]]
        persian_names = translate.batch_translate(english_names, "en", "fa")
        if persian_names is not None:
            for i in range(len(english_names)):
                countries[iter + i]['persian_name'] = persian_names[i]
        else:
            for i in range(len(english_names)):
                countries[iter + i]['persian_name'] = ""

    return countries


def main():
    countries = load_countries_and_their_codes()
    countries = add_persian_name(countries)
    with open('data/countries.json', 'w+', encoding='utf-8') as f:
        f.write(json.dumps(countries, ensure_ascii=False))


if __name__ == '__main__':
    main()
