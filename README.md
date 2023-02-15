# Books Downloader

## Main

This applications parses the Goodreads library of your account (want to read, read, etc.) and downloads the different titles included in your profile. 

The URL is enough (it can also read the CSV files with the titles)

The format of the downloaded books is prioritized and can be modified:

- azw3
- mobi
- epub
- pdf

## Instructions

You will need to have a config.yaml file in the same directory as the script that contains the path where you want to save the files, and the URL of the Goodreads profile with books read. The options are in the config.yaml file

- path: '/Users/javier/PycharmProjects/books-goodreads/downloads'
- url_goodreads: 'https://www.goodreads.com/review/list/13344444-xxxx-bbbbb-cccccc'


## Optional features

### Storage and Tacking

Once the book is downloaded, the book informaiton is added into a MongoDB collection. 

Those books that could not be downloaded, are also added into a separate collection, so it can be tracked and see if are available in future executions.

### Notifications

It's also possible to send emails with the attached book.


