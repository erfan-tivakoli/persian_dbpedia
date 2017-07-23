import json
from tqdm import tqdm

__author__ = 'Rfun'

import csv
from translator import translate_to_persian


def load_countries_and_their_codes():
    print("=============Loading countries=============")
    countries = []
    with open('./../source_files/country.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            code = row[0]
            english_name = row[1]
            country = {"code": code, "english_name": english_name}
            countries.append(country)
    print("=============Loaded=============")
    return countries


def add_persian_name(countries):
    print("=============Adding persian names=============")
    batch_size = 10

    for iter in tqdm(range(0, len(countries), batch_size)):
        english_names = [country['english_name'] for country in countries[iter: iter + batch_size]]
        persian_names = translate_to_persian.batch_google_translate(english_names)
        if persian_names is not None:
            for i in range(len(english_names)):
                countries[iter + i]['persian_name'] = persian_names[i]
        else :
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
