import os
import queue
import json
import traceback
import datetime
from time import sleep

import requests

from pymongo import MongoClient

client = MongoClient()
db = client.joojoo
cities = db.cities

client_id = '452Q14YDXQPNQAA4BAHLXDQYWBD3HYLZ1RJY0VKFH2QZ4HR1'
client_secret = 'FTITSK1IQ55RIP5YFJTRRSFABXCB0MC1O01HOGDJALAD4WXU'
un_crawled_grids = []
start_time = datetime.datetime.now()


def get_grids(boundaries, division_size=250):
    vertical_points = [
        boundaries['sw']['lat'] * (1 - i / division_size) + boundaries['ne']['lat'] * (i / division_size) for i in
        range(division_size + 1)]
    horizontal_points = [
        boundaries['sw']['lng'] * (1 - i / division_size) + boundaries['ne']['lng'] * (i / division_size) for i in
        range(division_size + 1)]

    all_triangles = []

    for i in range(len(horizontal_points) - 1):
        for j in range(len(vertical_points) - 1):
            grid_boundaries = {'sw': {'lat': vertical_points[i], 'lng': horizontal_points[j]},
                               'ne': {'lat': vertical_points[i + 1], 'lng': horizontal_points[j + 1]}}
            all_triangles.append(grid_boundaries)

    return all_triangles


def divide_gird(grid):
    ld = {'sw': {'lat': grid['sw']['lat'], 'lng': grid['sw']['lng']},
          'ne': {'lat': (grid['sw']['lat'] + grid['ne']['lat']) / 2,
                 'lng': (grid['sw']['lng'] + grid['ne']['lng']) / 2}}
    lu = {'sw': {'lat': (grid['sw']['lat'] + grid['ne']['lat']) / 2, 'lng': grid['sw']['lng']},
          'ne': {'lat': grid['ne']['lat'],
                 'lng': (grid['sw']['lng'] + grid['ne']['lng']) / 2}}
    rd = {'sw': {'lat': grid['sw']['lat'], 'lng': (grid['sw']['lng'] + grid['ne']['lng']) / 2},
          'ne': {'lat': (grid['sw']['lat'] + grid['ne']['lat']) / 2,
                 'lng': grid['ne']['lng']}}
    ru = {
        'sw': {'lat': (grid['sw']['lat'] + grid['ne']['lat']) / 2, 'lng': (grid['sw']['lng'] + grid['ne']['lng']) / 2},
        'ne': {'lat': grid['ne']['lat'],
               'lng': grid['ne']['lng']}}
    return [ld, lu, rd, ru]


def crawl(grids, city_name):
    data = []
    q = queue.Queue()
    for grid in grids:
        q.put(grid)

    number_of_requests = 0
    counter = 0
    while True:
        grid = q.get()
        if grid is None:
            break
        result = request_api(grid)
        number_of_requests += 1
        if result is not None:
            if len(result) == 30:
                print('dense area detected in city ' + str(city_name))
                for item in divide_gird(grid):
                    q.put(item)
            data += result
            counter += 1
            if counter % 50 == 0 or q.qsize() == 0:
                print("=========saving for city  " + str(city_name) + "=========")
                if not os.path.exists('data/' + str(city_name)):
                    os.makedirs('data/' + str(city_name))
                with open('data/' + str(city_name) + '/public_services.json', 'w+', encoding='utf-8') as f:
                    f.write(json.dumps(data, ensure_ascii=False))
                counter = 0
                check_rate(number_of_requests)

            print("number of founded results: " + str(len(result)) + " in city " + str(city_name))
        else:
            un_crawled_grids.append(grid)
            print('error in city ' + str(city_name))
        print("length of queue in city " + str(city_name) + " is: " + str(q.qsize()))
        if q.qsize() == 0:
            break

    if not os.path.exists('data/' + str(city_name)):
        os.makedirs('data/' + str(city_name))
    with open('data/' + str(city_name) + '/uncrawled.txt', 'w+', encoding='utf-8') as f:
        f.write(json.dumps(un_crawled_grids, ensure_ascii=False))


def request_api(boundary):
    try:
        base_url = "https://api.foursquare.com/v2/venues/search?intent=browse&"

        request_url = base_url + "sw=" + str(boundary['sw']['lat']) + ',' + str(boundary['sw']['lng']) + '&ne=' + str(
            boundary['ne']['lat']) + ',' + str(
            boundary['ne']['lng']) + '&client_id=' + client_id + '&client_secret=' + client_secret + '&v=20170101'
        result = json.loads(requests.get(request_url, timeout=3).content.decode('utf-8'))
        if result['meta']['code'] == 200:
            return result['response']['venues']
        if result['meta']['code'] == 403:
            print('time limit exceeded')
            print('we are going for a long sleep ...')
            sleep(3600)
        else:
            print(result)
            return None
    except IOError:
        traceback.print_exc()
        return None


def check_rate(number_of_requests):
    good_rate = 5000 / 3600
    now = datetime.datetime.now()
    time_duration_in_seconds = (now - start_time).total_seconds()
    rate = number_of_requests / time_duration_in_seconds
    if rate > good_rate - 100 / 3600:
        print('our rate is ' + str(rate) + ' and the best rate is' + str(
            50 / 36) + ' so we are going fast, sleeping for a little while .. ')
        sleep(10)
        check_rate(number_of_requests)


# class CrawlThread(threading.Thread):
#     def __init__(self, thread_id, boundary):
#         threading.Thread.__init__(self)
#         self.thread_id = thread_id
#         self.boundary = boundary
#
#     def run(self):
#         print("Starting " + str(self.thread_id))
#         grids = get_grids(self.boundary, division_size=100)
#         crawl(grids, self.thread_id)


if __name__ == '__main__':
    cursor = cities.find({"country": "Iran"})
    all_uncrawled_cities = []
    for city in cursor:
        if not os.path.exists('../public_services' + '/data/' + city['english_name']):
            all_uncrawled_cities.append(city)
        else:
            print("=========Already crawled " + str(city['english_name']) + "=========")

    for city in all_uncrawled_cities:
        print("=========Crawling " + str(city['english_name']) + "=========")
        if 'sw_lat' in city:
            boundaries = {'sw': {'lat': city['sw_lat'], 'lng': city['sw_lng']},
                          'ne': {'lat': city['ne_lat'], 'lng': city['ne_lng']}}
            grids = get_grids(boundaries, 4)
            # for idx, boundary in enumerate(grids):
            #     thread = CrawlThread(idx, boundary)
            #     thread.start()
            crawl(grids, city['english_name'])
