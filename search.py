import asyncio
import time

from libgenesis import Libgen
from pathlib import Path
import pandas as pd

lg = Libgen()

async def download_single(name):
    download_location = []
    result = await lg.search(query=name, filters={'extension': 'azw3'})
    path = Path('Downloads/' + name)

    if len(result.keys()) > 1:
        item = result[list(result)[0]]
        file_path = await lg.download(item['mirrors']['main'],
                                      dest_folder=path,
                                      progress=progress,
                                      progress_args=[
                                          item['title']
                                      ])
        download_location.append(file_path)

async def download(title_list):
    for title in title_list:
        q = title
        result = await lg.search(query=q,filters={'extension':'azw3'})
        download_location = []
        path = Path('Downloads/'+q)
        if len(result.keys())>1:
            print('awz3')
        else:
            result = await lg.search(query=q, filters={'extension': 'mobi'})
            if len(result.keys()) > 1:
                print('mobi')
            else:
                result = await lg.search(query=q, filters={'extension': 'epub'})
                if len(result.keys()) > 1:
                    print('epub')
                else:
                    result = await lg.search(query=q, filters={'extension': 'pdf'})
                    print('pdf')

        if len(result.keys()) > 1:
            item = result[list(result)[0]]
            file_path = await lg.download(item['mirrors']['main'],
                                          dest_folder=path,
                                          progress=progress,
                                          progress_args=[
                                              item['title']
                                          ])
            download_location.append(file_path)

async def progress(current, total, title):
    print('Downloading ', current, ' of ', total, ' ', title)

async def main():
        res = await asyncio.gather((download(retrieve_titles())))
        return res

async def single_book():
    res = await asyncio.gather((download_single("The Viking Spirit")))
    return res

def retrieve_titles():
    file_path = 'goodreads_library_export.csv'
    df = pd.read_csv(file_path, usecols=[1], header = 0)
    list_titles = df['Title'].astype(str).values.tolist()
    return list_titles
   # df = pd.read_excel(file_path, sheet_name=sheet_name, usecols = ['Col2','Col3'])

asyncio.run(single_book())
