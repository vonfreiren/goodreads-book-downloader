import asyncio

from auxiliar import other_information
from main import download_multiple, retrieve_titles

asyncio.run(download_multiple(title_list=retrieve_titles(path=other_information.file_path), database=True, mail=False))
