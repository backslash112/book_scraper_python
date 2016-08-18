from bs4 import BeautifulSoup
from urllib.request import urlopen
import threading
from multiprocessing.pool import ThreadPool
import queue

# Get the next page url from the current page url
def get_next_page_url(url):
    page = urlopen(url)
    soup_page = BeautifulSoup(page, 'lxml')
    page.close()
    # Get current page and next page tag
    current_page_tag = soup_page.find(class_="current")
    next_page_tag = current_page_tag.find_next_sibling()
    # Check if the current page is the last one
    if next_page_tag is None:
        next_page_url = None
    else:
        next_page_url = next_page_tag['href']
    return next_page_url


# Get the book detail urls by page url
def get_book_detail_urls(url):
    page = urlopen(url)
    soup = BeautifulSoup(page, 'lxml')
    page.close()
    urls = []
    book_header_tags = soup.find_all(class_="entry-title")
    for book_header_tag in book_header_tags:
        urls.append(book_header_tag.a['href'])
    return urls


# Get the book detail info by book detail url
def get_book_detail_info(url, q):
    # print(url)
    page = urlopen(url)
    book_detail_soup = BeautifulSoup(page, 'lxml')
    page.close()
    title_tag = book_detail_soup.find(class_="single-title")
    title = title_tag.string
    isbn_key_tag = book_detail_soup.find(text="Isbn:").parent
    isbn_tag = isbn_key_tag.find_next_sibling()
    isbn = isbn_tag.string.strip() # Remove the whitespace with the strip method
    book_info = { 'title': title, 'isbn': isbn }
    # print(book_info)
    q.put(book_info)


def run():
    url = "http://www.allitebooks.com/programming/net/page/1/"
    book_info_list = []

    def scapping_by_page(book_detail_urls):
        qs = []
        for book_detail_url in book_detail_urls:
            # Get the return value from the thread
            q = queue.Queue()
            thr = threading.Thread(target=get_book_detail_info, args=(book_detail_url, q))
            thr.start()
            qs.append(q)
        for q in qs:
            book_info = q.get()
            print(book_info)
            book_info_list.append(book_info)

    def scapping(page_url):
        print(page_url)
        book_detail_urls = get_book_detail_urls(page_url)
        scapping_by_page(book_detail_urls)

        next_page_url = get_next_page_url(page_url)
        if next_page_url is not None:
            scapping(next_page_url)
        else:
            return

    scapping(url)
    print(len(book_info_list))


run()
