import csv
import difflib
from tqdm import tqdm
from translator import translate
import json

__author__ = 'Rfun'




def load_provinces_with_their_country():
    print("=============Loading provinces=============")
    provinces = []
    provinces_names = set({})

    with open('./../source_files/world_cities.csv') as f:
        reader = csv.DictReader(f)

        for row in reader:
            english_name = row['province']


            country = row['country']

            province = {'english_name': english_name, 'country': country}
            if english_name not in provinces_names:
                provinces.append(province)
                provinces_names.add(english_name)

    print("=============Loaded=============")
    return provinces


def add_persian_name(provinces):
    print("=============Adding persian names=============")
    batch_size = 10

    for iter in tqdm(range(0, len(provinces), batch_size)):
        english_names = [province['english_name'] for province in provinces[iter: iter + batch_size]]
        persian_names = translate.batch_translate(english_names, "en", "fa")
        if persian_names is not None:
            for i in range(len(english_names)):
                provinces[iter + i]['persian_name'] = persian_names[i]
        else:
            for i in range(len(english_names)):
                provinces[iter + i]['persian_name'] = ""

    return provinces


def main():
    provinces = load_provinces_with_their_country()
    provinces = add_persian_name(provinces)
    with open('data/provinces.json', 'w+', encoding='utf-8') as f:
        f.write(json.dumps(provinces, ensure_ascii=False))


if __name__ == '__main__':
    main()
