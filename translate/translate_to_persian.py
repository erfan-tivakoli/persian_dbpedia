__author__ = 'Rfun'

from _codecs import encode
import traceback
import requests
import time

max_number_of_tries = 5
source_lan = "en"
target_lan = "fa"


def single_google_translate(english_word):

    number_of_tries = 0
    query = english_word
    while True:
        try:
            url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=" + source_lan + "&tl=" + \
                  target_lan + "&dt=t&q=" + query
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                result = r.json()
                return result[0][0][0]
        except IOError:
            number_of_tries += 1
            print("problem in translating " + query + " to persian")
            traceback.print_exc()
            time.sleep(10)
        if number_of_tries == max_number_of_tries:
            print('cant translate ' + query + " after " + str(max_number_of_tries) + " tries")
            break
    return None

def batch_google_translate(list_of_english_words):
    number_of_tries = 0
    query = '\n'.join(english_word for english_word in list_of_english_words)
    while True:
        try:
            url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=" + source_lan + "&tl=" + \
                  target_lan + "&dt=t&q=" + query
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                result = r.json()
                translated_words = []
                for item in result[0]:
                    translated_words.append(item[0].strip())
                return translated_words
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
    batch_google_translate(['hello', 'america', 'asghar', 'book'])