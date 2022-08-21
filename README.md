# Books

This app parses the Goodreads library of your account (want to read, read, etc.) and tries to download the books from libgen.rs

The format of the downlaoded books is prioritized and can be modified:

- azw3
- mobi
- epub
- pdf

Once the book is download, the book informaiton is added into a MongoDB collection. 
hose books that could not be downloaded, are also added into a separate collection.
