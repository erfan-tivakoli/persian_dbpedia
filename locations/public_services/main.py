import queue
import json

import requests

client_id = '452Q14YDXQPNQAA4BAHLXDQYWBD3HYLZ1RJY0VKFH2QZ4HR1'
client_secret = 'FTITSK1IQ55RIP5YFJTRRSFABXCB0MC1O01HOGDJALAD4WXU'
un_crawled_grids = []


def set_tehran_boundaries():
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


def crawl(grids):
    data = []
    q = queue.Queue()
    for grid in grids:
        q.put(grid)

    counter = 0
    while True:
        item = q.get()
        if item is None:
            break
        result = request_api(item)
        if result is not None:
            if len(result) == 30:
                print('dense area detected')
                for item in divide_gird(grid):
                    q.put(item)
            data += result
            counter += 1
            if counter % 50 == 0:
                print("=========saving=========")
                with open('data/public_services.json', 'w+', encoding='utf-8') as f:
                    f.write(json.dumps(data, ensure_ascii=False))
                counter = 0
            print("number of founded results: " + str(len(result)))

        q.task_done()
        print("length of queue: " + str(q.qsize()))
        if q.qsize() == 0:
            break

    with open('data/uncrawled.txt', 'w+', encoding='utf-8') as f:
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
        else:
            print('error')
            un_crawled_grids.append(boundary)
    except IOError:
        print('error')
        un_crawled_grids.append(boundary)
        return None


if __name__ == '__main__':
    boundaries = set_tehran_boundaries()
    grids = get_grids(boundaries)
    crawl(grids)
