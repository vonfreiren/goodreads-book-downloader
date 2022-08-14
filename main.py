import asyncio
from libgenesis import Libgen
from pathlib import Path
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

my_client = MongoClient("mongodb://localhost:27017/")
db = my_client["Library"]

book_db = db["Book"]
missing_books_db = db['Missing_Book']


lg = Libgen()

title = 'The Greek Myths Reimagined'

extension_azw3 = 'azw3'
extension_mobi = 'mobi'
extension_epub = 'epub'
extension_pdf = 'pdf'

async def download_single(name, extension):
    download_location = []
    result = await lg.search(query=name, filters={'extension': extension})
    path = Path('Downloads/' + name)

    if len(result.keys()) > 0:
        item = result[list(result)[0]]
        file_path = await lg.download(item['mirrors']['main'],
                                      dest_folder=Path('Downloads/' + item['title']),
                                      progress=progress,
                                      progress_args=[
                                          item['title']
                                      ])
        download_location.append(file_path)

async def download_multiple(title_list):
    existing_titles = find_books()
    for title in title_list:
        if title not in existing_titles:
            q = title
            result = await lg.search(query=q,filters={'extension':'azw3'})
            download_location = []
            path = Path('Downloads/'+q)
            if len(result.keys())>0:
                print('awz3')
            else:
                result = await lg.search(query=q, filters={'extension': 'mobi'})
                if len(result.keys()) > 0:
                    print('mobi')
                else:
                    result = await lg.search(query=q, filters={'extension': 'epub'})
                    if len(result.keys()) > 0:
                        print('epub')
                    else:
                        result = await lg.search(query=q, filters={'extension': 'pdf'})
                        print('pdf')

            if len(result.keys()) > 0:
                item = result[list(result)[0]]
                file_path = await lg.download(item['mirrors']['main'],
                                              dest_folder=path,
                                              progress=progress,
                                              progress_args=[
                                                  item['title']
                                              ])
                download_location.append(file_path)
                insert_data(item)
            else:
                insert_missing_data(title)

async def progress(current, total, title):
    print('Downloading ', current, ' of ', total, ' ', title)

async def main():
        res = await asyncio.gather((download_multiple(retrieve_titles())))
        return res

async def single_book(title, extension=extension_azw3):
    res = await asyncio.gather((download_single(title, extension)))
    return res

def retrieve_titles():
    file_path = 'goodreads_library_export.csv'
    df = pd.read_csv(file_path, usecols=[1], header = 0)
    list_titles = df['Title'].astype(str).values.tolist()
    return list_titles
   # df = pd.read_excel(file_path, sheet_name=sheet_name, usecols = ['Col2','Col3'])


def insert_data(book):
    book['last_update'] = datetime.now()
    book_db.insert_one(book)


def insert_missing_data(book):

    missing_books_db.insert_one({'name': book, 'last_check': datetime.now()})

def find_books():
    return list(book_db.find({},{"title": 1, '_id': 0}))

def delete_date():
    book_db.delete_many({})
    missing_books_db.delete_many({})

if __name__ == '__main__':
   #asyncio.run(single_book(title, extension_epub))
    asyncio.run(download_multiple((retrieve_titles())))


