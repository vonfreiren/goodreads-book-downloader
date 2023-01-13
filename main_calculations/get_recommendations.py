import random
import re
import time
from datetime import datetime

import bs4
import urllib3
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver

from auxiliar import other_information
from database import database_information
from database.database import is_book_already_in_db
from main_calculations.main import retrieve_ids, retrieve_authors, retrieve_titles

my_client = MongoClient(database_information.mongo_address)
db = my_client["Library"]
recommended_books_db = db["Recommended_Books"]

headers_list = other_information.url_headers


def get_my_books(path):
    list_ids = retrieve_ids(path=path)
    list_titles = retrieve_titles(path=path)
    list_authors = retrieve_authors(path=path)
    for count, book_id in enumerate(list_ids):
        scrape_book(book_id, list_titles[count], list_authors[count])


def scrape_book(book_id, title, author):
    user_agent_list = headers_list

    for i in range(1, 4):
        user_agent = random.choice(user_agent_list)
        headers = {'User-Agent': user_agent}

    url = 'https://www.goodreads.com/book/show/' + book_id
    http = urllib3.PoolManager()
    try:
        response = http.request('GET', url, headers=headers)
        time.sleep(5)

        soup = bs4.BeautifulSoup(response.data, 'html.parser')
        similar_link = soup.find('a', {'class': 'actionLink right seeMoreLink'}).get('href')
        find_similarities(similar_link, title, author, book_id)
    except:
        print("Problem Start with " + book_id)


def find_similarities(link, title, author, parent_id):
    window_size = "1920,1080"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % window_size)

    driver = webdriver.Chrome('../files/driver/chromedriver', chrome_options=chrome_options)
    driver.get(link)

    time.sleep(20)

    html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")
    list_ids = []
    clean_list_ids = []
    similarities = soup.find_all('div', {'data-react-class': 'ReactComponents.SimilarBooksList'})
    for similar in similarities:
        links = similar.find_all('a')
        for link in links:
            try:
                string_link = link.get('href')
                if string_link is not None:
                    id = string_link.split('/')[-1].split('-')[0]
                    if id is not None and string_link is not None:
                        list_ids.append(id)
                        if len(id) < 12:
                            clean_list_ids.append(id)
            except:
                print("Problem")
    clean_list_ids = list(set(clean_list_ids))
    find_list_info(clean_list_ids, title, author, parent_id)


def find_list_info(clean_list_ids, title, author, parent_id):
    for book_id in clean_list_ids:
        get_book_info(book_id, title, author, parent_id)


def get_book_info(book_id, title, author, parent_id):
    if is_book_already_in_db(book_id):
        print('Book already existing' + book_id + ':' + title + ':' + author)
    else:
        url = 'https://www.goodreads.com/book/show/' + book_id

        http = urllib3.PoolManager()
        for i in range(1, 4):
            user_agent = random.choice(headers_list)
            headers = {'User-Agent': user_agent}
        try:
            response = http.request('GET', url, headers=headers)
            soup = bs4.BeautifulSoup(response.data, 'html.parser')
            time.sleep(5)

            print(book_id)
            dict_recommended_book = {'book_id_title': book_id,
                                     'book_id': get_id(book_id),
                                     'book_title': ' '.join(soup.find('h1', {'id': 'bookTitle'}).text.split()),
                                     'author_link': soup.find('a', {'class': 'authorName'})['href'],
                                     'author': ' '.join(soup.find('span', {'itemprop': 'name'}).text.split()),
                                     'num_ratings': soup.find('meta', {'itemprop': 'ratingCount'})['content'].strip(),
                                     'num_reviews': soup.find('meta', {'itemprop': 'reviewCount'})['content'].strip(),
                                     'average_rating': soup.find('span', {'itemprop': 'ratingValue'}).text.strip(),
                                     'recommended_from_id': parent_id,
                                     'recommended_from_title': title,
                                     'recommended_from_author': author,
                                     'add_date': datetime.now()}

            recommended_books_db.insert_one(dict_recommended_book)

        except:
            print("Problem End with: " + book_id)


def get_id(book_id):
    pattern = re.compile("([^.-]+)")
    return pattern.search(book_id).group()


get_my_books(path=other_information.file_path)
