import asyncio

from bs4 import BeautifulSoup
import requests
import yaml
from main_calculations.main import download_multiple

parent_url = 'https://www.goodreads.com'

#Create config.yaml with:
# path (where to save files)
# url profile with books read

with open('config.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

filepath = data['path']
main_url = data['url_goodreads']


headers = {'User-agent': 'Mozilla/5.0'}

all_books = []

for i in range(1, 100):
    url = main_url + '?page=' + str(i)

    soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")
    books = soup.select('img[id*="cover_review"]')
    if len(books) == 0:
        break
    else:
        all_books = all_books + books
    dates = soup.find_all("span", {'class': "date_read_value"})
    counter = 1


list_books = []

for book in all_books:
    title = book['alt']
    list_books.append(title)


asyncio.run(download_multiple(title_list=list_books, database=False, mail=False))




