import asyncio

from auxiliar import other_information
from main import retrieve_titles, download_single, download_multiple

text = input("Include the title of the Book: ")
asyncio.run(download_multiple(title_list=[text], database=False, mail=True))



