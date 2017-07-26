from functools import lru_cache

__author__ = 'Rfun'

from _codecs import encode
import traceback
import requests
import time
from urllib.parse import quote
import re

max_number_of_tries = 3

# ToDo : create a config file with yandex api_key that you've got
# with open('./config', 'r+') as f:
#     api_key = f.readline().strip()
api_key = "trnsl.1.1.20170723T101148Z.946fdc967d37b51b.0cd5c419db7f308a9082b5135cd5dd9e62e7e0b3"

@lru_cache(maxsize=50)
def single_translate(word, source_lan, target_lan):
    number_of_tries = 0
    query = quote('text=' + word, safe='=&')
    while True:
        try:
            url = "https://translate.yandex.net/api/v1.5/tr.json/translate?key=" + \
                  api_key + "&" + query + "&lang=" + source_lan + "-" + target_lan

            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                result = r.json()
                if re.search('[a-zA-Z]',result['text'][0]) is None:
                    return result['text'][0].strip()
                else:
                    return None
        except IOError:
            number_of_tries += 1
            print("problem in translating " + query + " to persian")
            traceback.print_exc()
            time.sleep(10)
        if number_of_tries == max_number_of_tries:
            print('cant translator ' + query + " after " + str(max_number_of_tries) + " tries")
            break
    return None


def batch_translate(list_of_words, source_lan, target_lan):
    number_of_tries = 0
    query = quote('&'.join('text=' + english_word for english_word in list_of_words), safe='=&')
    while True:
        try:
            url = "https://translate.yandex.net/api/v1.5/tr.json/translate?key=" + \
                  api_key + "&" + query + "&lang=" + source_lan + "-" + target_lan

            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                result = r.json()
                translated_words = []
                for item in result['text']:
                    if re.search('[a-zA-Z]', item) is None:
                        translated_words.append(item.strip())
                    else:
                        translated_words.append("")
                return translated_words
            else:
                number_of_tries +=1
                print('returned status : '  + str(r.status_code))
                if number_of_tries == max_number_of_tries:
                    print('cant translate ' + query + " after " + str(max_number_of_tries) + " tries")
                    break
        except IOError:
            number_of_tries += 1
            print("problem in translating " + query + " to persian")
            traceback.print_exc()
            time.sleep(10)
        if number_of_tries == max_number_of_tries:
            print('cant translate ' + query + " after " + str(max_number_of_tries) + " tries")
            break
    return None


if __name__ == '__main__':
    # single_google_translate("hello")
    batch_translate(['hello', 'america', 'asghar', 'book'], "en", "fa")