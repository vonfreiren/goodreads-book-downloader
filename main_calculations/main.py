import asyncio
import traceback
from datetime import datetime
from pathlib import Path

import pandas as pd
from libgenesis import Libgen
from pymongo import MongoClient

from mail.notification import notify

my_client = MongoClient("mongodb://localhost:27017/")
db = my_client["Library"]

book_db = db["Book"]
missing_books_db = db['Missing_Book']

lg = Libgen()

title = 'The Greek Myths Reimagined'

extension_azw3 = 'azw3'
extension_azw = 'azw'
extension_mobi = 'mobi'
extension_epub = 'epub'
extension_pdf = 'pdf'


async def download_single(name, extension):
    download_location = []
    result = await lg.search(query=name, filters={'extension': extension})

    if len(result.keys()) > 0:
        item = result[list(result)[0]]
        file_path = await lg.download(item['mirrors']['main'],
                                      dest_folder=Path('Downloads/' + item['title']),
                                      progress=progress,
                                      progress_args=[
                                          item['title']
                                      ])
        download_location.append(file_path)


async def download_multiple(title_list, database=False, mail=False):
    if database:
        existing_titles = find_books()
    else:
        existing_titles = []
    extension = ''
    for title in title_list:
        try:
            if title not in existing_titles:
                q = title
                result = await lg.search(query=q, filters={'extension': extension_azw3})
                download_location = []
                path = Path('Downloads/' + q)
                if len(result.keys()) > 0:
                    extension = extension_azw3
                else:
                    result = await lg.search(query=q, filters={'extension': extension_azw})
                    if len(result.keys()) > 0:
                        extension = extension_azw
                    else:
                        result = await lg.search(query=q, filters={'extension': extension_mobi})
                        if len(result.keys()) > 0:
                            extension = extension_mobi
                        else:
                            result = await lg.search(query=q, filters={'extension': extension_epub})
                            if len(result.keys()) > 0:
                                extension = extension_epub
                            else:
                                result = await lg.search(query=q, filters={'extension': extension_pdf})
                                extension = extension_pdf

                if len(result.keys()) > 0:
                    item = result[list(result)[0]]
                    file_path = await lg.download(item['mirrors']['main'],
                                                  dest_folder=path,
                                                  progress=progress,
                                                  progress_args=[
                                                      item['title']
                                                  ])
                    download_location.append(file_path)
                    print("Downloaded book: "+ title + "in format: " + extension)
                    if database:
                        insert_data(item)
                    if mail:
                        notify(title, title, file_path)

                else:
                    if database:
                        insert_missing_data(title)
        except:
            traceback.print_exc()
            print('Error for: '+ title)



async def progress(current, total, title):
    print('Downloading ', current, ' of ', total, ' ', title)


async def main():
    res = await asyncio.gather((download_multiple(retrieve_titles())))
    return res


async def single_book(title, extension=extension_azw3):
    res = await asyncio.gather((download_single(title, extension)))
    return res


def retrieve_titles(path):
    file_path = path
    df = pd.read_csv(file_path, usecols=[1], header=0)
    list_titles = df['Title'].astype(str).values.tolist()
    return list_titles


def retrieve_ids(path):
    file_path = path
    df = pd.read_csv(file_path, usecols=[0], header=0)
    list_ids = df['Book Id'].astype(str).values.tolist()
    return list_ids


def retrieve_authors(path):
    file_path = path
    df = pd.read_csv(file_path, usecols=[2], header=0)
    list_ids = df['Author'].astype(str).values.tolist()
    return list_ids


def insert_data(book):
    book['last_update'] = datetime.now()
    book_db.insert_one(book)


def insert_missing_data(book):
    missing_books_db.insert_one({'name': book, 'last_check': datetime.now()})


def find_books():
    return list(book_db.find({}, {"title": 1, '_id': 0}))


def delete_date():
    book_db.delete_many({})
    missing_books_db.delete_many({})


def update_goodreads_book_id():
    list_ids = retrieve_ids()
    list_books = retrieve_titles()
    for count, book in enumerate(list_books):
        book_db.update_one({'title': book}, {'$set': {'book_id': list_ids[count]}})
