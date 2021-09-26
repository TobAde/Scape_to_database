# Scape_to_database
# Aliexpress Scraper

## Table of contents
* Introduction
* Getting started
* Usage
* Technologies used
* License

## Introduction
This is a web scrapping project designed to scrape data from Ebay search page and upload the data to a postgres database.
The information collected from the website are listed below:
* Item_title - this is the name of the product as shown on the website
* Item_url - this is the link (url) to the item on aliexpress
* Image_url - this is the link (url) to the image used to list the item
* Price - this is the price at which the item was listed



## Getting started
To use this scrapper function, the required packages listed in the ```requirements.txt``` file will have to be installed using 'pip install'.
For database connection, the parameters will be saved in a ```.env``` file and it should look like this:
```
DB=your_database
USER= user
PASSWORD= your_password
HOST=your_host
PORT = your_port
```

## Usage
The ```scrape``` function, which takes in two parameters, is used to scrape data 
using the item(search phrase) and minimum number of products required.
The function returns a dataframe that holds the scraped data from the website.
The ```Database``` class inserts the data into tables in the postgres database.
You can run the ```scrape``` function and add it to the postgres database using the data.py file as shown below

```python
from src.db import Database
from src.scraper import scrape


my_database = Database()
my_database.create_tables(scrape('Bag',200))

item_bag = my_database.to_csv(my_database.select_item('bag'),'bag')

```

## Technologies used
* [Python 3.8](https://www.python.org/) - Base programming language used.
* [Postgres Database](https://www.postgresql.org/) - Database used to store data scraped.

## License
The MIT License - Copyright (c) 2021 