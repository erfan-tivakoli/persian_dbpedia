#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from translator import translate


def city_crawler():
    cities = []
    for i in tqdm(range(1, 18)):
        try:
            url = "http://prayer.aviny.com/Search_City.aspx?Page=" + str(i) + "&Num=100&Q=&Country=-1&Province=-1"
            r = requests.get(url).content
            soup = BeautifulSoup(r, 'html.parser')
            for td in soup.find(id="DataGrid1").contents[2:-1]:
                city = {'persian_name': td.find("a").text, 'lng': lat_or_lng_converter((td.find_all("div"))[0].text),
                        'lat': lat_or_lng_converter((td.find_all("div"))[1].text),
                        'english_name': (td.find_all("td"))[-2].text,
                        'country': translate.single_translate((td.find_all("td"))[-1].text, "fa", "en")}
                cities.append(city)
        except IOError:
            print('problem in index ' + str(i))
    return cities


def lat_or_lng_converter(input):
    hour = input.split("°")[0]
    rest_part = input.split("°")[1]
    minute = rest_part.split("´")[0]
    rest_part = input.split("´")[1]
    second = rest_part.split("˝")[0]
    rest_part = rest_part.split("˝")[1]

    factor = 1
    if rest_part.__contains__("W") or rest_part.__contains__("S"):
        factor = -1
    return str(factor * (int(hour) + int(minute) / 60 + int(second) / 3600))


def update_cities_json(cities):
    with open('./data/cities.json') as f:
        previous_cities = json.load(f)
        all_cities_english_names = [city['english_name'] for city in previous_cities]
        for city in cities:
            if city['english_name'] not in all_cities_english_names:
                print("saving " + city['english_name'])
                previous_cities.append(city)
            else:
                print('already had ' + city['english_name'])
    return previous_cities


def main():
    cities = city_crawler()
    cities = update_cities_json(cities)
    with open('data/cities.json', 'w+', encoding='utf-8') as f:
        f.write(json.dumps(cities, ensure_ascii=False))


if __name__ == "__main__":
    main()