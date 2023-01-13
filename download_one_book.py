import asyncio

from main_calculations.main import download_multiple

text = input("Include the title of the Book: ")
asyncio.run(download_multiple(title_list=[text], database=False, mail=False))



