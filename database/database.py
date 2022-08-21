from pymongo import MongoClient

my_client = MongoClient("mongodb://localhost:27017/")
db = my_client["Library"]

book_db = db["Book"]
missing_books_db = db['Missing_Book']
recommended_books_db = db["Recommended_Books"]


def retrieve_security_db(book_id):
    book = book_db.find_one({"book_id": book_id})
    return book


def retrieve_recommended_books_db(book_id):
    book = recommended_books_db.find_one({"book_id": book_id})
    return book


def is_book_already_in_db(book_id):
    if retrieve_security_db(book_id) or retrieve_recommended_books_db(book_id):
        return True
