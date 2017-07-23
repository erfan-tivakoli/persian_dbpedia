__author__ = 'Rfun'

from _codecs import encode
import traceback
import requests
import time
from urllib.parse import quote

max_number_of_tries = 5
source_lan = "en"
target_lan = "fa"

#ToDo : create a config file with yandex api_key that you've got
with open('config', 'r+') as f:
    api_key = f.readline().strip()


def batch_google_translate(list_of_english_words):
    number_of_tries = 0
    query = quote('&'.join('text=' + english_word for english_word in list_of_english_words), safe='=&')
    while True:
        try:
            url = "https://translate.yandex.net/api/v1.5/tr.json/translate?key=" + \
                  api_key + "&" + query + "&lang=" + source_lan + "-" + target_lan

            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                result = r.json()
                translated_words = []
                for item in result['text']:
                    translated_words.append(item.strip())
                return translated_words
        except IOError:
            number_of_tries += 1
            print("problem in translating " + query + " to persian")
            traceback.print_exc()
            time.sleep(10)
        if number_of_tries == max_number_of_tries:
            print('cant translator ' + query + " after " + str(max_number_of_tries) + " tries")
            break
    return None


if __name__ == '__main__':
    # single_google_translate("hello")
    batch_google_translate(['hello', 'america', 'asghar', 'book'])