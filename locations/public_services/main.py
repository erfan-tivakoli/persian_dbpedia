import os
import queue
import json
import threading
import traceback
import datetime
from time import sleep

import requests

client_id = '452Q14YDXQPNQAA4BAHLXDQYWBD3HYLZ1RJY0VKFH2QZ4HR1'
client_secret = 'FTITSK1IQ55RIP5YFJTRRSFABXCB0MC1O01HOGDJALAD4WXU'
un_crawled_grids = []
start_time = datetime.datetime.now()


def get_tehran_boundaries():
    boundaries = {'sw': {'lat': 35.5590784, 'lng': 51.0934209}, 'ne': {'lat': 35.8345498, 'lng': 51.6062163}}
    return boundaries


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


def crawl(grids, thread_id=1):
    data = []
    q = queue.Queue()
    for grid in grids:
        q.put(grid)

    number_of_requests = 0
    counter = 0
    while True:
        item = q.get()
        if item is None:
            break
        result = request_api(item)
        number_of_requests += 1
        if result is not None:
            if len(result) == 30:
                print('dense area detected in thread ' + str(thread_id))
                for item in divide_gird(grid):
                    q.put(item)
            data += result
            counter += 1
            if counter % 50 == 0:
                print("=========saving for thread  " + str(thread_id) + "=========")
                if not os.path.exists('data/' + str(thread_id)):
                    os.makedirs('data/' + str(thread_id))
                with open('data/' + str(thread_id) + '/public_services.json', 'w+', encoding='utf-8') as f:
                    f.write(json.dumps(data, ensure_ascii=False))
                counter = 0
                check_rate(number_of_requests)

            print("number of founded results: " + str(len(result)) + " in thread " + str(thread_id))
        else:
            un_crawled_grids.append(item)
            print('error in thread ' + str(thread_id))
        q.task_done()
        print("length of queue in thread " + str(thread_id) + " is: " + str(q.qsize()))
        if q.qsize() == 0:
            break

    with open('data/' + str(thread_id) + '/uncrawled.txt', 'w+', encoding='utf-8') as f:
        f.write(json.dumps(un_crawled_grids, ensure_ascii=False))


def request_api(boundary):
    try:
        base_url = "https://api.foursquare.com/v2/venues/search?intent=browse&"

        request_url = base_url + "sw=" + str(boundary['sw']['lat']) + ',' + str(boundary['sw']['lng']) + '&ne=' + str(
            boundary['ne']['lat']) + ',' + str(boundary['ne'][
                                                   'lng']) + '&client_id=' + client_id + '&client_secret=' + client_secret + '&v=20170101'
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
    boundaries = get_tehran_boundaries()
    grids = get_grids(boundaries)
    # for idx, boundary in enumerate(grids):
    #     thread = CrawlThread(idx, boundary)
    #     thread.start()
    crawl(grids)
