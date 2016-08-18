from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
import urllib.request
import csv
import time
import requests
import queue
import threading
from multiprocessing.pool import ThreadPool


def get_price_amazon(isbn, q):
    base_url = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords="
    url = base_url + str(isbn)
    # page = urlopen(url)
    # soup = BeautifulSoup(page, 'lxml')
    # page.close()
    # Amazon don't allow automated access to their data, so need to fake the User-Agent
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    response = opener.open(url)
    html_content = response.read()

    soup = BeautifulSoup(html_content, 'lxml')
    # price_regexp = re.compile("\￥[0-9]+(\.[0-9]{2})?") # for amazon.cn
    price_regexp = re.compile("\$[0-9]+(\.[0-9]{2})?") # for amazon.com
    price = soup.find(text=price_regexp)
    # return [isbn, price]
    q.put([isbn, price])


def get_all_isbn():
    all_isbn = []
    with open('isbn.csv', 'rt') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            all_isbn.append(row[0])
    return all_isbn


def run():
    qs = []
    pool = ThreadPool(processes=10)
    book_price_list = []
    for isbn in get_all_isbn():
        # result = get_price_amazon(isbn)
        # Multi-threading
        q = queue.Queue()
        pool.apply_async(get_price_amazon, args=(isbn, q))
        qs.append(q)

    for q in qs:
        price = q.get()
        print(price)
        book_price_list.append(price)

    print(len(book_price_list))
    save_to_csv(book_price_list)


def save_to_csv(list):
    print('save')
    with open('prices.csv', 'w', newline='') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerow(['isbn','price'])
        a.writerows(list)


run()
